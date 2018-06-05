## INSTALLATION
The installation of this module is quite straight forward: 

1- Download/clone the folder "pyipmeta-master"

2- Run "cd pyipmeta-master"

3- Run "python setup.py install"



## USAGE
A useful sample script for testing this module is available at ./test/pyipmeta_test.py.

# Maxmind
1- On its line 6 i.e 
```
ipm = pyipmeta.IpMeta(provider="maxmind",
                      provider_config="-b ./test/maxmind/2017-03-16.GeoLiteCity-Blocks.csv.gz -l ./test/maxmind/2017-03-16.GeoLiteCity-Location.csv.gz")
```
you could specify the blocks of the GeoliteCity database saved on a date that is the closest to your considered date for IP geolocation.
                      
2- Make sure you specify "maxmind" as the provider on the previous line. You can also use the explicit time option:

```ipm = pyipmeta.IpMeta(provider="maxmind", time="Nov 11 2011")```




