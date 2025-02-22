# Network Manager DBUS Tools

This repository is intended to provide tools for performing basic network operation on a device with Linux Network Manager via DBUS.
These tools are intended to build upon th official examples provided in the official Network Manager repository
[Network Manager Python Dbus](https://github.com/NetworkManager/NetworkManager/tree/main/examples/python/dbus)


# Scripts

* get_wifi_interface_name
* disconnect_from_wifi_connection

## Supported Platforms

```
    Linux
```
NOTE: Scripts have been tested with Ubuntu 22 but it should work with Ubuntu 24

## Requirements

* Python: 3.8.10
* Following python modules need to be installed
    ```
    pydbus
    ```
## Supported NetworkManager Version

```
    1.22.10
```

NOTE: NetworkManager DBUS-API was updated about 4 years ago so you may face issue if you are using a significant older or newer version. But the core principles should stay the same. 
