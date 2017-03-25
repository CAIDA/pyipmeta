#!/usr/bin/env python

import _pyipmeta


ipm = _pyipmeta.IpMeta()
print ipm
print

print "Asking for Maxmind backend by ID:"
# try getting a provider that exists
prov = ipm.get_provider_by_id(1)
print "Got provider: %d, %s (%s)" % (prov.id, prov.name, prov.enabled)
print

# try to get one that does not exist
print "Asking for non-existent provider by ID (1000):"
prov = ipm.get_provider_by_id(1000)
print "This should be none: %s" % prov
print

# try to get all available providers
print "Getting all available providers:"
all_provs = ipm.get_all_providers()
print all_provs
print

# try to get maxmind by name
print "Asking for Maxmind provider by name:"
prov = ipm.get_provider_by_name("maxmind")
print "Got provider: %d, %s (%s)" % (prov.id, prov.name, prov.enabled)
print

# try to enable the maxmind provider with incorrect options
print "Enabling Maxmind provider (with incorrect options):"
print ipm.enable_provider(prov, "develop")
print prov
print
