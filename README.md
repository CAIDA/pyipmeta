## INSTALLATION
The installation of this module is quite straight forward: 

1- Download/clone the folder "pyipmeta-master"
2- Run "cd pyipmeta-master"
3- Run "python setup.py install"

## USAGE
A useful sample script for using this module is available at ./test/pyipmeta_test.py.
1- On its line 6 i.e 

```
ipm = pyipmeta.IpMeta(provider="maxmind",
                      provider_config="-b ./test/maxmind/2017-03-16.GeoLiteCity-Blocks.csv.gz -l ./test/maxmind/2017-03-16.GeoLiteCity-Location.csv.gz")
```
you could specify the blocks of the GeoliteCity database saved on a date that is the closest one to your considered date.
                      
2- 

