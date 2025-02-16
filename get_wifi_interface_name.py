
#!/usr/bin/env python

import dbus

###################################################################################################
DEVICE_TYPE_WIFI_ID = 2

###################################################################################################
def get_wifi_interface_name():
    '''
    Retrieves the name of the Wi-Fi network interface using python dbus.
    Returns:
        str or None: The name of the Wi-Fi interface, if a Wi-Fi device is found; otherwise, None.
    '''
    try:
        bus = dbus.SystemBus()
        # get network manager object
        nm_proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        nm = dbus.Interface(nm_proxy, "org.freedesktop.NetworkManager")

        # get list of network devices
        devices = nm.GetDevices()
        wifi_interface_name = None


        for dev_path in devices:
            # get device properties
            device_proxy = bus.get_object("org.freedesktop.NetworkManager", dev_path)
            device_properties = dbus.Interface(device_proxy, "org.freedesktop.DBus.Properties")

            # get the device type attribute
            dev_type = device_properties.Get("org.freedesktop.NetworkManager.Device", "DeviceType")

            # check if device is Wi-Fi
            if dev_type == DEVICE_TYPE_WIFI_ID:

                # fetch name of  Wi-Fi interface
                iface = device_properties.Get("org.freedesktop.NetworkManager.Device", "Interface")
                wifi_interface_name = iface
                break

        return wifi_interface_name

    except dbus.DBusException as e:
        print(f"Failed to communicate with NetworkManager: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

###################################################################################################
if __name__ == "__main__":

    wifi_interface = get_wifi_interface_name()
    if wifi_interface is not None:
        print(f"Detected Wi-Fi device :{wifi_interface}")
    else:
        print(f"No Wi-Fi device detected. Please check if your device Wi-Fi is active.")