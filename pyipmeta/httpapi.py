import argparse
import flask
import logging
import _pyipmeta


app = flask.Flask("IPMeta Server")
dummy = {
    "country": "NZ"
}

ipm = _pyipmeta.IpMeta()
prov = None


@app.route('/metadata/lookup/ip/<string:ip_addr>', methods=['GET', 'POST'])
@app.route('/metadata/lookup/ip/<string:ip_addr>/<string:prefix_len>',
           methods=['GET', 'POST'])
def lookup_pfx(ip_addr, prefix_len=None):
    if prefix_len:
        ip_addr = "%s/%s" % (ip_addr, prefix_len)
    res = prov.lookup(ip_addr)
    if len(res) == 1:
        res = res[0]
    return flask.jsonify(res)


def main():
    parser = argparse.ArgumentParser(description="""
    Simple HTTP API for performing IP/Prefix geolocation
    """)
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

    app.run()
