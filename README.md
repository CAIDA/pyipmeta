PyIPMeta is a Python library that provides a high-level interface for
historical and realtime geolocation metadata lookups using Maxmind
GeoIP and/or NetAcuity (Digital Element) geolocation databases.

## Pre-requisites
Before installing PyIPMeta, you will need:
  - [libipmeta](https://github.com/CAIDA/libipmeta)
  - Python setuptools (`sudo apt install python-setuptools` on Ubuntu)
  - Python development headers (`sudo apt install python-dev` on Ubuntu)

## Install PyIPMeta

First, either clone this GitHub repo, or download the latest
[PyIPMeta release tarball](https://github.com/CAIDA/pyipmeta/releases)

Then,

 ```
 $ python setup.py build_ext
 # python setup.py install
 ```

_Note:_ use `python setup.py install --user` to install the library in
your home directory.

## Usage

A useful sample script for testing this module is available at
`./test/pyipmeta_test.py`.

_Note:_ if using the library outside CAIDA's network, you will need to
manually provide databases to use.

### Maxmind

1. If you have local maxmind database files (i.e.,
`*.GeoLiteCity-Blocks.csv.gz` and `*.GeoLiteCity-Location.csv.gz`),
then you can load them as follows:

```
ipm = pyipmeta.IpMeta(provider="maxmind",
                      provider_config="-b ./test/maxmind/2017-03-16.GeoLiteCity-Blocks.csv.gz -l ./test/maxmind/2017-03-16.GeoLiteCity-Location.csv.gz")
```

However, if you are on CAIDA's network, you can use the automatic
database download feature:

2. Simply specify `maxmind` as the provider, and provide the `time`
parameter:

```ipm = pyipmeta.IpMeta(provider="maxmind", time="Nov 11 2011")```

As far as the time is concerned, note that the parser is quite smart
and can support the format YYYYMMDD as well. That is to say, the
previous line also corresponds to the following one:

```ipm = pyipmeta.IpMeta(provider="maxmind", time="20111111")```

3. As initializing the IpMeta object will take some time (because it
has to load the database), it makes sense to load it once, and then
query many times.

As an example, the output obtained for the IP 192.172.226.97 (on Nov
11 2011) is a list under the following format, which can easily be
parsed:

```[{'connection_speed': '', 'city': '', 'asn_ip_count': 0, 'post_code': '', 'lat_long': (37.750999450683594, -97.8219985961914), 'region': '', 'area_code': 0, 'asns': [], 'continent_code': 'NA', 'metro_code': 0, 'matched_ip_count': 1, 'region_code': 0, 'country_code': 'US', 'id': 223, 'polygon_ids': []}]```

There is no thresholds on the number of IPs to geolocate after loading
IPMeta. For IPs that can not be geolocated, IPMeta returns a python
exception. We suggest that you catch these errors and pass in those
cases.


### Netacuity

In order to use netacuity for IP geolocation, you just need to change
the provider name from "maxmind" to "netacq-edge" and follow the
instructions listed above.
