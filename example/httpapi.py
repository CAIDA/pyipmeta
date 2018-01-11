#!/usr/bin/env python

import argparse
import flask
import logging
import _pyipmeta


app = flask.Flask("IPMeta Server")

base_response = {
    "type": "metadata.lookup",
    "error": None,
    "queryParameters": {},
    "data": None
}

ipm = _pyipmeta.IpMeta()
prov = None


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


@app.route('/metadata/lookup/ipgeo/<string:ip_addr>', methods=['GET', 'POST'])
@app.route('/metadata/lookup/ipgeo/<string:ip_addr>/<string:prefix_len>',
           methods=['GET', 'POST'])
def lookup_pfx(ip_addr, prefix_len=None):
    if prefix_len:
        ip_addr = "%s/%s" % (ip_addr, prefix_len)
    res_list = prov.lookup(ip_addr)
    res_list = clean_res(res_list)
    fr = base_response.copy()
    fr["data"] = {
        "metadata": res_list
    }
    return flask.jsonify(fr)


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

    parser.add_argument('-p',  '--provider-name',
                        nargs='?', required=True,
                        help='IPMeta provider name')

    parser.add_argument('-c',  '--provider-config',
                        nargs='?', required=True,
                        help='IPMeta provider config')

    opts = vars(parser.parse_args())

    logging.basicConfig(level="DEBUG",
                        format='%(asctime)s|%(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    global prov

    prov = ipm.get_provider_by_name(opts["provider_name"])
    if not prov:
        raise ValueError("Could not find provider '%s'" % opts["provider_name"])

    ipm.enable_provider(prov, opts["provider_config"])

    if not prov.enabled:
        raise ValueError("Could not enable IPMeta provider")

    logging.info("Ready to accept queries")

    app.run(host=opts["listen_ip"], port=opts["listen_port"])


if __name__ == "__main__":
    main()
