PyIPMeta is a Python library that provides a high-level interface for historical and realtime geolocation metadata lookups using Maxmind GeoIP and/or NetAcuity (Digital Element) geolocation databases.

Quick Start
-----------

To get started using PyIPMeta, first [install libipmeta v1.0.0](https://github.com/CAIDA/libipmeta/releases/tag/v1.0.0).

Then, you should be able to install ***PyIPMeta***.

## Installing PyIPMeta from source

1. Clone the project and execute:
```
$ cd pyipmeta
$ python setup.py build_ext
$ sudo python setup.py install
```
Use `python setup.py install --user` to install the library in your home directory.

## USAGE
A useful sample script for testing this module is available at `./test/pyipmeta_test.py`.

** Notice that if you want to use the library outside CAIDA's facility, you will need first to ask for permission to copy the geo-databases files you may need to perform any processing outside the building. **

### Maxmind
1- In case, the files "*.GeoLiteCity-Blocks.csv.gz" and "*.GeoLiteCity-Location.csv.gz" are available, you can adopt the explicit config.  On its line 6 i.e 
```
ipm = pyipmeta.IpMeta(provider="maxmind",
                      provider_config="-b ./test/maxmind/2017-03-16.GeoLiteCity-Blocks.csv.gz -l ./test/maxmind/2017-03-16.GeoLiteCity-Location.csv.gz")
```
you could specify the blocks of the GeoliteCity database saved on a date that is the closest to your considered date for IP geolocation.
However, this is not the only option. Instead, you can also use the explicit time option.
                      
2- Please make sure you specify "maxmind" as the provider (either on the previous line if the explicit config is adopted or on the following one when you choose the explicit time option):

```ipm = pyipmeta.IpMeta(provider="maxmind", time="Nov 11 2011")```

As far as the time is concerned, note that the parser is quite smart and can support the format YYYYMMDD as well. That is to say, the previous line also corresponds to the following one:

```ipm = pyipmeta.IpMeta(provider="maxmind", time="20111111")```

3- As initializing the IpMeta object will take some time (because it has to load the database), it makes sens to try and load it once, and then query many times. 

As an example, the output obtained for the IP 192.172.226.97 (on Nov 11 2011) is a list under the following format, which can easily be parsed:

```[{'connection_speed': '', 'city': '', 'asn_ip_count': 0, 'post_code': '', 'lat_long': (37.750999450683594, -97.8219985961914), 'region': '', 'area_code': 0, 'asns': [], 'continent_code': 'NA', 'metro_code': 0, 'matched_ip_count': 1, 'region_code': 0, 'country_code': 'US', 'id': 223, 'polygon_ids': []}]```

There is no thresholds on the number of IPs to geolocate after loading IPMeta. For IPs that can not be geolocated, IPMeta returns a python exception. We suggest that you catch these errors and pass in those cases.


### Netacuity
In order to use netacuity for IP geolocation, you just need to change the provider name from "maxmind" to "netacq-edge" and follow the instructions listed above.

