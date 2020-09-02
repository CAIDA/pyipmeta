import os
import argparse
import dateutil.parser
from . import dbidx
import json
import _pyipmeta
import logging
import threading
import weakref

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv('PYIPMETA_LOGLEVEL', 'INFO'))


class IpMeta:

    def __init__(self,
                 providers=None,
                 time=None,
                 **kwargs
                 ):
        self.ipm_args = kwargs
        self.target_time = self._parse_timestr(time)
        self.reload_period = 10*60 # 10 minutes
        self.reloader_stop = None

        logger.debug('IpMeta.__init__(%r, %r)', providers, time)

        if providers is None:
            # use all providers known by our helper
            providers = dbidx.DbIdx.all_providers()

        self.prov_dict = dict()
        for arg in providers:
            args = arg.strip().split(None, 1)
            if args[0] in self.prov_dict:
                raise ValueError("Provider '%s' may not be repeated" % (args[0],))
            self.prov_dict[args[0]] = dict()
            if len(args) == 2:
                # "<name> <config>"
                if time is not None:
                    raise ValueError("Only one of 'time' and 'provider_config' may be specified")
                self.prov_dict[args[0]] = { "auto": False, "cmd": args[1] }
            else:
                # "<name>"
                # let _reload() figure out the config
                self.prov_dict[args[0]] = { "auto": True, "cmd": None }
        self._reload(force_load=True)

        if self.target_time is None and self.reload_period is not None:
            self.reloader_stop = threading.Event()
            reloader_thread = threading.Thread(target=IpMeta._periodic_reload,
                    args=(weakref.ref(self),), daemon=True)
            reloader_thread.start()

    def __del__(self):
        logger.debug("IpMeta.__del__()")
        # stop the reloader_thread immediately
        if self.reloader_stop:
            self.reloader_stop.set()

    @staticmethod
    def _periodic_reload(ref):
        """Periodically check for new data and reload if needed."""
        # This method never holds a strong reference to the IpMeta object for
        # very long, so it doesn't prevent the object from being deleted.
        reload_period = ref().reload_period
        reloader_stop = ref().reloader_stop
        logger.debug("_periodic_reload started")
        while not reloader_stop.wait(reload_period):
            ipm = ref()
            if ipm is None:
                break
            logger.debug("_periodic_reload reloading")
            ipm._reload()
            reload_period = ipm.reload_period
            ipm = None  # release the strong reference
        logger.debug("_periodic_reload stopped")

    def _load(self):
        """Load ipm according to prov_dict.

        Loading is done into a second ipm object; when done, the new object
        atomically replaces the old, so this is safe to call in a thread while
        other threads read from ipm.
        """
        new_ipm = _pyipmeta.IpMeta(**self.ipm_args)
        for prov_name, prov_info in self.prov_dict.items():
            # configure the provider
            prov = new_ipm.get_provider_by_name(prov_name)
            if not prov:
                raise ValueError("Invalid provider specified: '%s'" % prov_name)
            logger.debug('enable_provider("%s", "%s")' % (prov_name, prov_info["cmd"]))
            if not new_ipm.enable_provider(prov, prov_info["cmd"]):
                raise RuntimeError("Could not enable provider (check stderr)")
        self.ipm = new_ipm

    def _reload(self, force_load=False):
        """Reload ipm if new db files are available.

        If new db files are available for target_time for any providers marked
        "auto", load a new ipm object to replace the existing one.
        """
        for prov_name, prov_info in self.prov_dict.items():
            if prov_info["auto"]:
                idx = dbidx.DbIdx(prov_name)
                cmd = idx.best_db(self.target_time, build_cmd=True)
                if cmd != prov_info["cmd"]:
                    logger.info("need reload for %s: %r", prov_name, cmd)
                    logger.debug("  (was: %r)", prov_info["cmd"])
                    prov_info["cmd"] = cmd
                    force_load = True
        if force_load:
            self._load()
        else:
            logger.debug("no reload needed")

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
            mask = mask | prov.mask
        return mask

    def lookup(self, ipaddr, provmask=0):
        return self.ipm.lookup(ipaddr, provmask)


def main():
    logging.basicConfig(datefmt='%H:%M:%S',
            format='[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s')

    parser = argparse.ArgumentParser(description="""
    Historical IP/Prefix Metadata tagging tool. Supports Maxmind and Net Acuity Edge
    """)
    parser.add_argument('-p', '--provider',
        required=False, action='append',
        help="Metadata provider name and configuration (repeatable).  Available providers: "
            + ", ".join(name for name in dbidx.DbIdx.all_providers()))
    parser.add_argument('-d', '--date',
        required=False,
        help="Date to use for automatic DB selection (default: latest DB)")
    parser.add_argument('-l', '--loglevel',
        required=False,
        help="Logging level")
    parser.add_argument('-f', '--file',
        help="File with list of addresses/prefixes to look up")
    parser.add_argument('prefix', nargs='*', help='IP address or prefix to look up', default=[])

    opts = vars(parser.parse_args())

    if opts["loglevel"] is not None:
        logger.setLevel(opts["loglevel"])

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
