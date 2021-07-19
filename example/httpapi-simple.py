#!/usr/bin/env python

# This file is part of pyipmeta.
#
# Copyright (C) 2017-2020 The Regents of the University of California.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import flask
import logging
import pyipmeta
import datetime
import schedule


app = flask.Flask("IPMeta Server")

base_response = {
    "type": "metadata.lookup",
    "error": None,
    "queryParameters": {},
    "data": None
}

ipm = pyipmeta.IpMeta(provider="netacq-edge")
ipm_updated_time = datetime.datetime.now()

def clean_res(res_list):
    dedup = {}
    for res in res_list:
        if "id" not in res:
            continue
        if res["id"] in dedup:
            dedup[res["id"]]["matched_ips"] += res["matched_ips"]
            continue
        dedup[res["id"]] = {
            "type": "ipgeo",
            "continent_code": res["continent_code"],
            "country_code": res["country_code"],
            "matched_ips": res["matched_ips"],
        }
    return dedup.values()


@app.route('/iplookup/<string:ip_addr>', methods=['GET', 'POST'])
def lookup_pfx(ip_addr):
    res_list = ipm.lookup(ip_addr)
    # res_list = clean_res(res_list)
    fr = base_response.copy()
    fr["data"] = {
        "metadata": res_list
    }
    return flask.jsonify(res_list)

def job():
    print ("job")

def main():
    parser = argparse.ArgumentParser(description="""
    Simple HTTP API for performing IP/Prefix geolocation
    """)
    parser.add_argument('-l',  '--listen-ip',
                        nargs='?', required=True,
                        help='IP/Hostname to listen on')

    parser.add_argument('-P',  '--listen-port',
                        nargs='?', required=True,
                        help='Port to listen on')

    opts = vars(parser.parse_args())

    logging.basicConfig(level="DEBUG",
                        format='%(asctime)s|%(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info("Ready to accept queries")

    schedule.every(10).seconds.do(job)
    schedule.run_pending()
    app.run(host=opts["listen_ip"], port=opts["listen_port"])


if __name__ == "__main__":
    main()
