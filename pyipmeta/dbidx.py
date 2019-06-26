import datetime
import re
import sys
import subprocess
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

# TODO: allow customization of built commands (e.g., no polygon table?)
# TODO: allow use of special "latest" db
# TODO: switch to using swift
# TODO: add support for pfx2as


class DbIdx:

    def __init__(self, provider):
        self.prov_cfg = self._load_provider_config(provider)
        self.latest_time = None
        self.dbs = {}
        self._load_dbs()

    def _load_provider_config(self, provider):
        server = "http://loki.caida.org:3282"
        cfgs = {
            "netacq-edge": {
                "file_pfx": server + "/netacuity-dumps/Edge-processed",
                "filelist": "md5.md5",
                "name_parser": self.parse_netacq_filename,
                "cmd_builder": self.build_netacq_cmd,
                "tables_required": ["blocks", "locations", "polygons"],
            },
            "maxmind": {
                "file_pfx": server + "/maxmind-geolite-dumps/city-v4",
                "filelist": "md5.md5",
                "name_parser": self.parse_maxmind_filename,
                "cmd_builder": self.build_maxmind_cmd,
                "tables_required": ["blocks", "location"],
            },
        }
        return cfgs[provider]

    def _load_dbs(self):
        for line in urlopen("%s/%s" % (self.prov_cfg["file_pfx"],
                                               self.prov_cfg["filelist"])):
            line = line.decode('utf-8')
            (filename, chksum) = line.strip().split(" ")
            (date, table, filename) = self.prov_cfg["name_parser"](filename)
            if not date:
                continue
            if date not in self.dbs:
                self.dbs[date] = {}
            self.dbs[date][table] = "%s/%s" % (self.prov_cfg["file_pfx"], filename)
            self.latest_time = date if self.latest_time is None else max(self.latest_time, date)

    def best_db(self, time=None, build_cmd=False):
        if time is None:
            time = self.latest_time
            dbs = self.dbs[time]
        else:
            best_time = None
            for t in self.dbs:
                # are all the required files available?
                ok = True
                for tbl in self.prov_cfg["tables_required"]:
                    if tbl not in self.dbs[t]:
                        ok = False
                        break
                if not ok:
                    continue
                # is this the best time we've seen so far?
                if t < time and (not best_time or best_time < t):
                    best_time = t
            dbs = self.dbs[best_time]

        return dbs if not build_cmd else self.prov_cfg["cmd_builder"](dbs)

    def latest_db(self, build_cmd=False):
        return self.best_db(build_cmd=build_cmd)

    @staticmethod
    def parse_netacq_filename(filename):
        # 2017-03-16.netacq-4-polygons.csv.gz
        match = re.match(r"(\d+-\d+-\d+)\.netacq-4-(.+)\.csv\.gz", filename)
        if not match:
            return None, None, filename
        date_str = match.group(1)
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        table = match.group(2)
        return date, table, filename

    @staticmethod
    def build_netacq_cmd(dbs):
        return "-b %s -l %s" % (dbs["blocks"], dbs["locations"])

    @staticmethod
    def build_maxmind_cmd(dbs):
        return "-b %s -l %s" % (dbs["blocks"], dbs["location"])

    @staticmethod
    def parse_maxmind_filename(filename):
        # 2015-02-16.GeoLiteCity-Blocks.csv.gz
        match = re.match(r"(\d+-\d+-\d+)\.GeoLiteCity-(.+)\.csv\.gz", filename)
        if not match:
            return None, None, filename
        date_str = match.group(1)
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        table = match.group(2).lower()
        return date, table, filename
