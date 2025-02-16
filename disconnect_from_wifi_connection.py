#!/usr/bin/env python

import dbus

###################################################################################################
DEVICE_TYPE_WIFI_ID = 2

###################################################################################################
def deactivate_wifi_connection():
    '''
    Disconnect from the current Wi-Fi connection by deactivating it.
    This method allows the Wi-Fi to connect to another saved connection,
    if available, similar to how most UI tools behave.

    This is a better approach then disconnecting the Wi-Fi device,
    which requires the user to manually reconnect to another Wi-Fi.

    Returns:
        bool: Result of operation, True if successful else False
        str: Success or failure message
    '''
    try:
        bus = dbus.SystemBus()

        # get network manager object
        nm_proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        nm = dbus.Interface(nm_proxy, "org.freedesktop.NetworkManager")

        # get active connections
        active_connections = nm_proxy.Get("org.freedesktop.NetworkManager", "ActiveConnections", dbus_interface="org.freedesktop.DBus.Properties")

        # iterate over the connections and find active Wi-Fi connection
        for connection_path in active_connections:
            connection_proxy = bus.get_object("org.freedesktop.NetworkManager", connection_path)
            connection_props = dbus.Interface(connection_proxy, "org.freedesktop.DBus.Properties")

            # get devices associated with connection
            devices = connection_props.Get("org.freedesktop.NetworkManager.Connection.Active", "Devices")

            # get properties of each device
            for device_path in devices:
                # get device properties
                device_proxy = bus.get_object("org.freedesktop.NetworkManager", device_path)
                device_props = dbus.Interface(device_proxy, "org.freedesktop.DBus.Properties")

                device_type = device_props.Get("org.freedesktop.NetworkManager.Device", "DeviceType")

                # check if device is Wi-Fi
                if device_type == DEVICE_TYPE_WIFI_ID:

                    # Fetching SSID of connection we are about to deactivate from its properties
                    # This step can be skipped if you do not need to tell the user the name of the disconnected Connection
                    wifi_device = dbus.Interface(device_proxy, "org.freedesktop.NetworkManager.Device.Wireless")
                    active_ap_path = device_props.Get("org.freedesktop.NetworkManager.Device.Wireless", "ActiveAccessPoint")
                    if active_ap_path != "/":
                        ap_proxy = bus.get_object("org.freedesktop.NetworkManager", active_ap_path)
                        ap_props = dbus.Interface(ap_proxy, "org.freedesktop.DBus.Properties")
                        ssid = ap_props.Get("org.freedesktop.NetworkManager.AccessPoint", "Ssid")
                        ssid = "".join([chr(byte) for byte in ssid])  # Convert SSID from byte array to string

                    # Deactivate the connection
                    nm.DeactivateConnection(connection_path)

                    # Return success, operation with name of connection
                    return True, f"Deactivated Wi-Fi connection: {ssid if active_ap_path != '/' else 'Unknown'}"

        return False, "No active Wi-Fi connection found."
    except dbus.DBusException as e:
        return False, f"Failed to communicate with NetworkManager: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

###################################################################################################
if __name__ == "__main__":
    result, message = deactivate_wifi_connection()
    print(message)
