import os
import dateutil
import re
import sys
import subprocess
from swiftclient.service import SwiftService, SwiftError


def _parse_filename(filename, pattern):
    match = re.match(pattern, filename)
    if not match:
        return None, None, filename
    date = dateutil.parser.parse(match.group('date'))
    table = match.group('table').lower()
    return date, table, filename

def _build_cmd(db, cmd):
    return " ".join([subcmd[0] % db[subcmd[1]]
        for subcmd in cmd if subcmd[1] in db])

class DbIdx:
    cfgs = {
#        # configuration format
#        <provider-name>: [
#            One or more container descriptions:
#            {
#                "container": <name-of-swift-container>,
#                "pattern": regexp to match object (file) name; must contain
#                    "(?P<date>...)" and "(?P<table>...)"
#                "cmd": [
#                    list of (fmt, tablename, required) tuples.
#                    For each tuple, if the object corresponding to tablename
#                    exists for the given date, it is subbed into the fmt
#                    string.  All the generated strings are concatenated to
#                    form an ipmeta provider command string.  If the object
#                    does not exist for the given date, and required=False,
#                    the table is skipped; if required=True, the entire date
#                    is skipped.
#                ],
#            },
#        ],
        "netacq-edge": [
            {
                "container": "datasets-external-netacq-edge-processed",
                # e.g., 2017-03-16.netacq-4-blocks.csv.gz
                "pattern": r"(?P<date>\d+-\d+-\d+)\.netacq-4-(?P<table>.+)\.csv\.gz",
                "cmd": [
                    ("-l %s", "locations", True),
                    ("-b %s", "blocks",    True),
                    ("-6 %s", "ipv6",      False),
                ],
            },
        ],
        "maxmind": [
            {   # maxmind v1
                "container": "datasets-external-maxmind-city-v4",
                # e.g., 2015-02-16.GeoLiteCity-Blocks.csv.gz
                "pattern": r"(?P<date>\d+-\d+-\d+)\.GeoLiteCity-(?P<table>.+)\.csv\.gz",
                "cmd": [
                    ("-b %s", "blocks",   True),
                    ("-l %s", "location", True),
                ],
            },
#           {   # maxmind v2 (note: It's ok to enable both v1 and v2.)
#               "container": "datasets-external-maxmind-city2",
#               # e.g., 2020-08-19.GeoLite2-City-Blocks-IPv6.csv.gz
#               "pattern": r"(?P<date>\d+-\d+-\d+)\.GeoLite2-City-(?P<table>.+)\.csv\.gz",
#               "cmd": [
#                   ("-b %s", "blocks-ipv4",  True),
#                   ("-b %s", "blocks-ipv6",  True),
#                   ("-l %s", "locations-en", True),
#               ],
#           },
        ],
        "pfx2as": [
            {
                "container": "datasets-routing-routeviews-prefix2as",
                # e.g., 2020/08/routeviews-rv2-20200823-2200.pfx2as.gz
                "pattern": r"\d+/\d+/routeviews-rv2-(?P<date>\d{8})-\d+\.(?P<table>pfx2as)\.gz",
                "cmd": [("-f %s", "pfx2as", True)],
            },
        ],
    }

    def __init__(self, provider):
        self.prov_name = provider
        self.prov_cfg = self._load_provider_config(provider)
        self.latest_time = None
        self.dbs = {}    # time -> table name -> file name
        self.dbcfgs = {} # time -> db config info
        self._load_index()

    def _load_provider_config(self, provider):
        if provider not in DbIdx.cfgs:
            raise RuntimeError("Unknown provider '%s'" % provider)
        return DbIdx.cfgs[provider]

    def _load_index(self):
        swift_opts = {
            # Apparently SwiftService by default checks only ST_AUTH_VERSION.
            # We emulate the swift CLI, and check three different variables.
            "auth_version": os.environ.get('ST_AUTH_VERSION',
                os.environ.get('OS_AUTH_VERSION',
                os.environ.get('OS_IDENTITY_API_VERSION', '1.0'))),
            }
        with SwiftService(options=swift_opts) as swift:
            for cfg in self.prov_cfg:
                try:
                    list_parts_gen = swift.list(container=cfg["container"])
                    for page in list_parts_gen:
                        if not page["success"]:
                            raise page["error"]
                        for item in page["listing"]:
                            (date, table, filename) = _parse_filename(item["name"],
                                    cfg["pattern"])
                            if not date:
                                continue
                            self.dbcfgs[date] = cfg
                            # format the name as expected by libipmeta/wandio
                            self.dbs.setdefault(date, {})[table] = \
                                "swift://%s/%s" % (cfg["container"], filename)
                            if self.latest_time is None or date > self.latest_time:
                                self.latest_time = date
                except SwiftError as e:
                    # logger.error(e.value)
                    raise e

    @staticmethod
    def all_providers():
        return DbIdx.cfgs.keys()

    def best_db(self, time=None, build_cmd=False):
        if time is None:
            time = self.latest_time
        best_time = None
        for t in self.dbs:
            # are all the required files available?
            cfg = self.dbcfgs[t]
            if not all([subcmd[1] in self.dbs[t] for subcmd in cfg["cmd"] if subcmd[2]]):
                continue
            # is this the best time we've seen so far?
            if t <= time and (not best_time or best_time < t):
                best_time = t
        if not best_time:
            raise RuntimeError("No complete datasets for %s" % (self.prov_name))
        best_db = self.dbs[best_time]
        cfg = self.dbcfgs[best_time]
        return best_db if not build_cmd else _build_cmd(best_db, cfg["cmd"])
