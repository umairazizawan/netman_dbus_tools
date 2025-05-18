#!/usr/bin/env python3
import dbus
import uuid


###################################################################################################
DEVICE_TYPE_WIFI_ID = 2


WIFI_SSID = "MYWIFI" # Replace with your Wi-Fi SSID and Password
WIFI_PASSWORD = "MYPASSWORD"

###################################################################################################

def create_wifi_connection(ssid, password):
    '''
    Create a Wi-Fi connection using NetworkManager.
    :param ssid: The SSID of the Wi-Fi network.
    :param password: The password for the Wi-Fi network.
    :return: A message indicating the connection status.
    NOTE: A very basic verification method is shown here.
    Please consider implementing a more robust solution based on your specific requirement.
    A detailed implementation is beyond the scope of this script as its primary focus is sending a 
    connection request.
    '''
    try:
        if ssid:
            bus = dbus.SystemBus()
            
            # Get NetworkManager's primary interface
            nm_proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
            nm = dbus.Interface(nm_proxy, "org.freedesktop.NetworkManager")
            
            # Find Wi-Fi device
            devices = nm.GetDevices()
            wifi_device_path = None
            for device_path in devices:
                device_proxy = bus.get_object("org.freedesktop.NetworkManager", device_path)
                
                # retrieve the device type
                device_type = device_proxy.Get(
                    "org.freedesktop.NetworkManager.Device", 
                    "DeviceType", 
                    dbus_interface="org.freedesktop.DBus.Properties"
                )
                
                if device_type == DEVICE_TYPE_WIFI_ID:
                    wifi_device_path = device_path
                    break
            
            if not wifi_device_path:
                raise Exception("No Wi-Fi device found.")

            # Access Wi-Fi device properties
            wifi_proxy = bus.get_object("org.freedesktop.NetworkManager", wifi_device_path)
            wifi_device = dbus.Interface(wifi_proxy, "org.freedesktop.NetworkManager.Device.Wireless")

            # Request scanning to update Wi-Fi networks
            # Note: This is not necessary but it is good practice
            wifi_device.RequestScan({})
            
            # Access settings to add a connection
            settings_proxy = bus.get_object(
                "org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Settings"
            )
            settings = dbus.Interface(settings_proxy, "org.freedesktop.NetworkManager.Settings")



            ##### Add and Activate Wi-Fi connection #####

            connection_name = f"WiFi-{ssid}"
            s_con = dbus.Dictionary(
                {"type": "802-11-wireless", "uuid": str(uuid.uuid4()), "id": connection_name}
            )
            s_wifi = dbus.Dictionary({"ssid": dbus.ByteArray(ssid.encode("utf-8"))})
            s_wifi_sec = dbus.Dictionary({"key-mgmt": "wpa-psk", "psk": password})
            s_ip4 = dbus.Dictionary({"method": "auto"})
            s_ip6 = dbus.Dictionary({"method": "ignore"})

            connection = dbus.Dictionary(
                {
                    "connection": s_con,
                    "802-11-wireless": s_wifi,
                    "802-11-wireless-security": s_wifi_sec,
                    "ipv4": s_ip4,
                    "ipv6": s_ip6,
                }
            )

            print(f"Creating Wi-Fi connection: {connection_name}")
            new_connection_path = settings.AddConnection(connection)
            print(f"New connection path: {new_connection_path}")

            # Activate the connection
            active_connection_path = nm.ActivateConnection(
                new_connection_path,  # Path to the new connection
                wifi_device_path,     # Wi-Fi device path
                "/"                   # Specific object path; use "/" for default
            )
            print(f"Activated connection path: {active_connection_path}")
            
            print(f"Sent Connection Request to Wi-Fi!")

            ##### Verify Results of Activation Request #####
            # NOTE: Below is a very basic verification method and not the most accurate.
            # For more accurate verification please consider implementing connection monitoring.
            # Some devices send an explicit failure incase of a wrong password. Others may not send any response.
            # Similarly behaviours can vary for successfully connection requests based on your Wi-Fi card.  
            # One reliable method is to continously check state of your Wi-Fi device to verify if request has succeeded or not
            # Again the exact implementation depends on your Wi-Fi device and the kind of routers/Hotspot connections you wish to 
            # connect this. Therefore, it is beyond the current scope of a Basic implementation.
            # As a starting point the states of the device can be the following:
            #     device_states = {
            #     30: "Disconnected",
            #     40: "Preparing to connect",
            #     50: "Configuring",
            #     70: "Connected (local only)",
            #     100: "Fully connected",
            #     120: "Authentication failure",
            # }

            # Verify connection is active            
            active_connections = nm_proxy.Get(
                "org.freedesktop.NetworkManager",
                "ActiveConnections",
                dbus_interface="org.freedesktop.DBus.Properties"
            )
            for ac_path in active_connections:
                ac_proxy = bus.get_object("org.freedesktop.NetworkManager", ac_path)
                ac_id = ac_proxy.Get(
                    "org.freedesktop.NetworkManager.Connection.Active",
                    "Id",
                    dbus_interface="org.freedesktop.DBus.Properties"
                )
                if ac_id == connection_name:
                    print(f"Successfully connected to '{ssid}'.")
                    return f"Successfully connected to '{ssid}'."

            return f"Failed to establish a stable connection to '{ssid}'."

        else:
            return "SSID is not specified."

    except dbus.DBusException as e:
        print(f"Failed to connect to Wi-Fi: {e}")
        return f"Failed to connect to Wi-Fi. Error: {e}"



###################################################################################################
if __name__ == "__main__":
    message = create_wifi_connection(WIFI_SSID, WIFI_PASSWORD)
    print(message)
