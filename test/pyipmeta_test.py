#!/usr/bin/env python

import pyipmeta

print("Testing maxmind with explicit config...")
ipm = pyipmeta.IpMeta(providers=["maxmind "
    "-b ./test/maxmind/2017-03-16.GeoLiteCity-Blocks.csv.gz "
    "-l ./test/maxmind/2017-03-16.GeoLiteCity-Location.csv.gz"])

print(ipm.lookup("192.172.226.97"))
print("")

print("Testing maxmind with explicit time (Nov 11 2011)...")
ipm = pyipmeta.IpMeta(providers=["maxmind"], time="Nov 11 2011")
print(ipm.lookup("192.172.226.97"))
print("")

print("Testing netacq-edge with latest db...")
ipm = pyipmeta.IpMeta(providers=["netacq-edge"])
print(ipm.lookup("192.172.226.97"))
print("")

print("Testing netacq-edge with explicit time (Feb 1 2016)...")
ipm = pyipmeta.IpMeta(providers=["netacq-edge"], time="Feb 1 2016")
print(ipm.lookup("192.172.226.97"))
print("")
