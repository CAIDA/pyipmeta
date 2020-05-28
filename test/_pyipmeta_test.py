#!/usr/bin/env python

import _pyipmeta
import json


ipm = _pyipmeta.IpMeta()
print(ipm)
print()

print("Asking for Maxmind backend by ID:")
# try getting a provider that exists
prov = ipm.get_provider_by_id(1)
print("Got provider: %d, %s (%s)" % (prov.id, prov.name, prov.enabled))
print()

# try to get one that does not exist
print("Asking for non-existent provider by ID (1000):")
prov = ipm.get_provider_by_id(1000)
print("This should be none: %s" % prov)
print()

# try to get all available providers
print("Getting all available providers:")
all_provs = ipm.get_all_providers()
print(all_provs)
print()

# try to get maxmind by name
print("Asking for Maxmind provider by name:")
prov = ipm.get_provider_by_name("maxmind")
print("Got provider: %d, %s (%s)" % (prov.id, prov.name, prov.enabled))
print()

# try to enable the maxmind provider with incorrect options
print("Enabling Maxmind provider (with incorrect options):")
print(ipm.enable_provider(prov, "invalid options"))
print(prov)
print()

# now enable maxmind provider with some test data
print("Enabling Maxmind provider (using included test data):")
print(ipm.enable_provider(prov, "-b ./test/maxmind/2017-03-16.GeoLiteCity-Blocks.csv.gz -l ./test/maxmind/2017-03-16.GeoLiteCity-Location.csv.gz"))
print(prov)
print()

# and then look up an IP address
print("Querying Maxmind for an IP address (192.172.226.97):")
(res,) = ipm.lookup("192.172.226.97")
print(res)
print("Result in JSON format:")
print(json.dumps(res))
print()

# and a prefix
print("Querying Maxmind for a prefix (44.0.0.0/8):")
results = ipm.lookup("44.0.0.0/8")
print(results)
print("Results in JSON format:")
print(json.dumps(results))
print()

# create a new ipm to test a different provider
del ipm
ipm = _pyipmeta.IpMeta()
print(ipm)
print()

# take the pfx2as provider for a spin
print("Getting/enabling pfx2as provider (using included test data)")
prov = ipm.get_provider_by_name("pfx2as")
print(prov)
print(ipm.enable_provider(prov, "-f ./test/pfx2as/routeviews-rv2-20170329-0200.pfx2as.gz"))
print()

# and look up an IP address
print("Querying pfx2as for an IP address (192.172.226.97):")
(res,) = ipm.lookup("192.172.226.97")
print(res)
print("Result in JSON format:")
print(json.dumps(res))
print()

# and a prefix
print("Querying pfx2as for a prefix (192.172.226.0/24):")
results = ipm.lookup("192.172.226.0/24")
print(results)
print("Results in JSON format:")
print(json.dumps(results))
print()

del ipm
