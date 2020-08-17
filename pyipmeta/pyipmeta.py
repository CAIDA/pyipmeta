import argparse
import dateutil.parser
from . import dbidx
import json
import _pyipmeta


class IpMeta:

    def __init__(self,
                 providers=None,
                 time=None,
                 **kwargs
                 ):
        self.ipm = _pyipmeta.IpMeta(**kwargs)
        self.prov = list()

        parsed_time = self._parse_timestr(time)

        if providers is None:
            # use all providers known by our helper
            prov_dict = dbidx.DbIdx.all_providers()

        else:
            prov_dict = dict()
            for arg in providers:
                args = arg.strip().split(None, 1)
                if len(args) == 2:
                    # "<name> <config>"
                    if time is not None:
                        raise ValueError("Only one of 'time' and 'provider_config' may be specified")
                    prov_dict[args[0]] = args[1]
                else:
                    # "<name>"
                    # use our helper to try and figure out the provider config
                    try:
                        idx = dbidx.DbIdx(args[0])
                    except KeyError as e:
                        raise ValueError("Invalid provider specified: '%s'" % args[0]) from None
                    prov_dict[args[0]] = idx.best_db(parsed_time, build_cmd=True)

        for prov_name, prov_config in prov_dict.items():
            # configure the provider
            prov = self.ipm.get_provider_by_name(prov_name)
            if not prov:
                raise ValueError("Invalid provider specified: '%s'" % prov_name)
            if not self.ipm.enable_provider(prov, prov_config):
                raise RuntimeError("Could not enable provider (check stderr)")
            self.prov.append(prov)

    @staticmethod
    def _parse_timestr(timestr):
        if timestr is None:
            return None
        return dateutil.parser.parse(timestr, ignoretz=True)

    def provmask(self, names, must_be_enabled=False):
        """Convert list of provider names to a provider mask."""
        mask = 0
        for name in names:
            prov = self.ipm.get_provider_by_name(name)
            if prov is None:
                raise ValueError("Invalid provider '%s'" % name)
            if must_be_enabled and not prov.enabled:
                raise ValueError("Provider '%s' is not enabled" % name)
            mask = mask | (1 << (prov.id - 1))
        return mask

    def lookup(self, ipaddr, provmask=0):
        return self.ipm.lookup(ipaddr, provmask)


def main():
    parser = argparse.ArgumentParser(description="""
    Historical IP/Prefix Metadata tagging tool. Supports Maxmind and Net Acuity Edge
    """)
    parser.add_argument('-p', '--provider',
        required=False, action='append',
        help="Metadata provider to use ('netacq-edge' or 'maxmind') and its configuration (repeatable)")
    parser.add_argument('-d', '--date',
        required=False,
        help="Date to use for automatic DB selection (default: latest DB)")

    parser.add_argument('prefix', nargs='*', help='IP address or prefix to look up', default=[])
    parser.add_argument('-f', '--file',
        help="File with list of addresses/prefixes to look up")

    opts = vars(parser.parse_args())

    ipm = IpMeta(providers=opts["provider"], time=opts["date"])

    if opts["file"] is not None:
        with open(opts["file"], "r") as fh:
            for line in fh:
                line = line.strip()
                do_lookup(ipm, line)

    for prefix in opts["prefix"]:
        do_lookup(ipm, prefix)


def do_lookup(ipm, addr):
    print(json.dumps({
        "query": addr,
        "result": ipm.lookup(addr),
    }))
