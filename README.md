PyIPMeta is a Python library that provides a high-level interface for
historical and realtime geolocation metadata lookups using Maxmind
GeoIP and/or NetAcuity (Digital Element) geolocation databases.

## Pre-requisites
Before installing PyIPMeta, you will need:
  - [libipmeta (>= 3.1.0)](https://github.com/CAIDA/libipmeta)
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

1. If you have local database files (e.g., maxmind files
`*.GeoLiteCity-Blocks.csv.gz` and `*.GeoLiteCity-Location.csv.gz`),
then you can load them as follows:

```
ipm = pyipmeta.IpMeta(providers=["maxmind "
    "-b ./test/maxmind/2017-03-16.GeoLiteCity-Blocks.csv.gz "
    "-l ./test/maxmind/2017-03-16.GeoLiteCity-Location.csv.gz")
```

2.  However, if you have access to CAIDA's Swift store, you can use the
automatic database download feature.
Simply specify the provider name without the database file options, and
optionally provide the `time` parameter:

```ipm = pyipmeta.IpMeta(providers=["maxmind"], time="Dec 30 2019")```

Swift credentials can be in environment variables or stored in a `.env` file.

If time is omitted, IpMeta will choose the most recent data available, and
will load new data when it becomes available (checking every 10 minutes).

As far as the time is concerned, note that the parser is quite smart
and can support the format YYYYMMDD as well. That is to say, the
previous line also corresponds to the following one:

```ipm = pyipmeta.IpMeta(providers=["maxmind"], time="20191230")```

3. Multiple providers can be loaded.  For example:

```ipm = pyipmeta.IpMeta(providers=["maxmind ...", "netacq-edge ..."])```

4. As initializing the IpMeta object will take some time (because it
has to load the databases), it makes sense to load it once, and then
query many times.

The lookup function takes an IP address or prefix argument:

```ipm.lookup('192.172.226.97')```

or

```ipm.lookup('192.172.226.0/24')```

As an example, the output obtained for the IP 192.172.226.97 (on Nov
11 2011) is a list under the following format, which can easily be
parsed:

```[{'connection_speed': '', 'city': '', 'asn_ip_count': 0, 'post_code': '', 'lat_long': (37.750999450683594, -97.8219985961914), 'region': '', 'area_code': 0, 'asns': [], 'continent_code': 'NA', 'metro_code': 0, 'matched_ip_count': 1, 'region_code': 0, 'country_code': 'US', 'id': 223, 'polygon_ids': []}]```

There is no limit on the number of IPs to query after loading IPMeta. For IPs
that have no matches in the database(s), IPMeta returns a python exception. We
suggest that you catch these errors and pass in those cases.


### Providers

The available providers and their options are as follows:

- maxmind:  
  -l <file>   v1 or v2 locations file
  -b <file>   v1 or v2 blocks file (may be repeated)  

- netacq-edge:  
  -b <file>   ipv4 blocks file (must be used with -l)  
  -l <file>   ipv4 locations file (must be used with -b)  
  -6 <file>   ipv6 file  

- pfx2as:  
  -f          pfx2as file  

