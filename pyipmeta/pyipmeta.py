import argparse
import datetime
import dateutil.parser
import dbidx
import json
import _pyipmeta


class IpMeta:

    def __init__(self,
                 provider,
                 time=None,
                 provider_config=None
                 ):
        self.ipm = _pyipmeta.IpMeta()

        # configure the provider
        self.prov = self.ipm.get_provider_by_name(provider)
        if not self.prov:
            raise ValueError("Invalid provider specified: '%s'" % provider)

        if provider_config is None:
            # use our helper to try and figure out the provider config
            idx = dbidx.DbIdx(provider)
            parsed_time = self._parse_timestr(time)
            provider_config = idx.best_db(parsed_time, build_cmd=True)
        elif time is not None:
            # doesn't make sense to specify both provider_config AND time
            raise ValueError("Only one of 'time' and 'provider_config' may be specified")

        self.ipm.enable_provider(self.prov, provider_config)

    @staticmethod
    def _parse_timestr(timestr):
        if timestr is None:
            return None
        return dateutil.parser.parse(timestr, ignoretz=True)

    def lookup(self, ipaddr):
        return self.prov.lookup(ipaddr)


def main():
    parser = argparse.ArgumentParser(description="""
    Historical IP/Prefix Metadata tagging tool. Supports Maxmind and Net Acuity Edge
    """)
    parser.add_argument('-p', '--provider',
                        nargs='?', required=False,
                        help="Metadata provider to use ('netacq-edge' or 'maxmind')",
                        choices=["maxmind", "netacq-edge"],
                        default="netacq-edge")
    parser.add_argument('-d', '--date',
                        nargs='?', required=False,
                        help="Date to use for automatic DB selection (default: latest DB)")
    parser.add_argument('-c', '--provider-config',
                        nargs='?', required=False,
                        help="Explicit libipmeta config string to pass to specified provider")

    gp = parser.add_mutually_exclusive_group(required=True)
    gp.add_argument('addrs', nargs='*', help='IP Addresses or prefixes to look up', default=[])
    gp.add_argument('-f', '--file', nargs='?',
                    help="File with list of IPs/prefixes to look up")

    opts = vars(parser.parse_args())

    ipm = IpMeta(provider=opts["provider"], time=opts["date"],
                 provider_config=opts["provider_config"])

    if opts["file"] is not None:
        with open(opts["file"], "r") as fh:
            for line in fh:
                line = line.strip()
                do_lookup(ipm, line)

    for addr in opts["addrs"]:
        do_lookup(ipm, addr)


def do_lookup(ipm, addr):
    print json.dumps({
        "query": addr,
        "result": ipm.lookup(addr),
    })
