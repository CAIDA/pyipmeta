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
