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
    date_str = match.group('date')
    date = dateutil.parser.parse(date_str)
    table = match.group('table').lower()
    return date, table, filename

def _build_cmd(dbs, template):
    return template[0] % tuple(dbs[table] for table in template[1:])

class DbIdx:
    cfgs = {
#        # configuration format
#        <provider-name>: [
#            {
#                "container": <name-of-swift-container>,
#                "pattern": regexp to match object (file) name; must contain
#                    "(?P<date>...)" and "(?P<table>...)"
#                "cmd": [
#                    first item is ipmeta provider configuration command
#                    format; remaining items are names of tables.  The object
#                    names corresponding to the tables for a selected date
#                    will be subbed into format.
#                ]
#            },
#        ],
        "netacq-edge": [
            {
                "container": "datasets-external-netacq-edge-processed",
                # e.g., 2017-03-16.netacq-4-polygons.csv.gz
                "pattern": r"(?P<date>\d+-\d+-\d+)\.netacq-4-(?P<table>.+)\.csv\.gz",
                "cmd": ["-b %s -l %s", "blocks", "locations"],
            },
        ],
        "maxmind": [
            {   # maxmind v1
                "container": "datasets-external-maxmind-city-v4",
                # e.g., 2015-02-16.GeoLiteCity-Blocks.csv.gz
                "pattern": r"(?P<date>\d+-\d+-\d+)\.GeoLiteCity-(?P<table>.+)\.csv\.gz",
                "cmd": ["-b %s -l %s", "blocks", "location"],
            },
#           {   # maxmind v2 (note: It's ok to enable both v1 and v2.)
#               "container": "datasets-external-maxmind-city2",
#               # e.g., 2020-08-19.GeoLite2-City-Blocks.csv.gz
#               "pattern": r"(?P<date>\d+-\d+-\d+)\.GeoLite2-City-(?P<table>.+)\.csv\.gz",
#               "cmd": ["-b %s -l %s", "blocks", "location"],
#           },
        ],
        "pfx2as": [
            {
                "container": "datasets-routing-routeviews-prefix2as",
                # e.g., 2020/08/routeviews-rv2-20200823-2200.pfx2as.gz
                "pattern": r"\d+/\d+/routeviews-rv2-(?P<date>\d{8})-\d+\.(?P<table>pfx2as)\.gz",
                "cmd": ["-f %s", "pfx2as"],
            },
        ],
    }

    def __init__(self, provider):
        self.prov_name = provider
        self.prov_cfg = self._load_provider_config(provider)
        self.latest_time = None
        self.dbs = {}
        self._load_dbs()

    def _load_provider_config(self, provider):
        return DbIdx.cfgs[provider]

    def _load_dbs(self):
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
                            self.dbs.setdefault(date, {})["_cfg"] = cfg
                            # format the name as expected by libipmeta/wandio
                            self.dbs[date][table] = \
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
            cfg = self.dbs[t]["_cfg"]
            if not all([tbl in self.dbs[t] for tbl in cfg["cmd"][1:]]):
                continue
            # is this the best time we've seen so far?
            if t <= time and (not best_time or best_time < t):
                best_time = t
        if not best_time:
            raise RuntimeError("No complete datasets for %s" % (self.prov_name))
        dbs = self.dbs[best_time]

        return dbs if not build_cmd else _build_cmd(dbs, dbs["_cfg"]["cmd"])

