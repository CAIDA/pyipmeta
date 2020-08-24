import os
import datetime
import re
import sys
import subprocess
from swiftclient.service import SwiftService, SwiftError

# TODO: allow customization of built commands (e.g., no polygon table?)
# TODO: switch to using swift
# TODO: add support for pfx2as


def parse_netacq_filename(filename):
    # 2017-03-16.netacq-4-polygons.csv.gz
    match = re.match(r"(\d+-\d+-\d+)\.netacq-4-(.+)\.csv\.gz", filename)
    if not match:
        return None, None, filename
    date_str = match.group(1)
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    table = match.group(2)
    return date, table, filename

def build_netacq_cmd(dbs):
    return "-b %s -l %s" % (dbs["blocks"], dbs["locations"])

def parse_maxmind_filename(filename):
    # 2015-02-16.GeoLiteCity-Blocks.csv.gz
    match = re.match(r"(\d+-\d+-\d+)\.GeoLiteCity-(.+)\.csv\.gz", filename)
    if not match:
        return None, None, filename
    date_str = match.group(1)
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    table = match.group(2).lower()
    return date, table, filename

def build_maxmind_cmd(dbs):
    return "-b %s -l %s" % (dbs["blocks"], dbs["location"])

class DbIdx:
    cfgs = {
        "netacq-edge": {
            "container": "datasets-external-netacuity-edge-processed",
            "name_parser": parse_netacq_filename,
            "cmd_builder": build_netacq_cmd,
            "tables_required": ["blocks", "locations", "polygons"],
        },
        "maxmind": {
            "container": "datasets-external-maxmind-city-v4",
            "name_parser": parse_maxmind_filename,
            "cmd_builder": build_maxmind_cmd,
            "tables_required": ["blocks", "location"],
        },
    }

    def __init__(self, provider):
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
            try:
                list_parts_gen = swift.list(container=self.prov_cfg["container"])
                for page in list_parts_gen:
                    if not page["success"]:
                        raise page["error"]
                    for item in page["listing"]:
                        (date, table, filename) = \
                            self.prov_cfg["name_parser"](item["name"])
                        if not date:
                            continue
                        self.dbs.setdefault(date, {})[table] = \
                            "swift://%s/%s" % (self.prov_cfg["container"], filename)
                        if self.latest_time is None or date > self.latest_time:
                            self.latest_time = date
            except SwiftError as e:
                logger.error(e.value)

    @staticmethod
    def all_providers():
        return DbIdx.cfgs.keys()

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

