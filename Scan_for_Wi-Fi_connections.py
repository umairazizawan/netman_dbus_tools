#!/usr/bin/env python3

from pydbus import SystemBus
from gi.repository import GLib
import time

from get_wifi_interface_name import get_wifi_interface_name

###################################################################################################
DEVICE_TYPE_WIFI_ID = 2

###################################################################################################
def scan_for_wifi_devices(interface_name):
    bus = SystemBus()
    network_manager = bus.get("org.freedesktop.NetworkManager")

    # Get all devices managed by NetworkManager
    devices = network_manager.GetDevices()

    # Find the Wi-Fi device
    wifi_device = None
    for device_path in devices:
        device = bus.get(".NetworkManager", device_path)
        if device.Interface == interface_name and device.DeviceType == DEVICE_TYPE_WIFI_ID:
            wifi_device = device
            break

    if not wifi_device:
        print(f"No Wi-Fi device found with interface '{interface_name}'")
        return

    # Get the current value of LastScan before triggering a new scan
    last_scan_timestamp_before = wifi_device.LastScan

    # Request a Wi-Fi scan
    wifi_device.RequestScan({})
    print("Scanning for available Wi-Fi networks...")

    # Poll for scan completion by checking if LastScan timestamp changes
    while True:
        GLib.MainContext().iteration(False)  # Run the main context iteration non-blocking
        last_scan_timestamp_after = wifi_device.LastScan
        if last_scan_timestamp_after != last_scan_timestamp_before:
            print("Wi-Fi scan complete. Available networks:")
            # Get available access points after scan completion
            access_points = wifi_device.GetAccessPoints()

            wifi_networks = []

            # get info for all found networks and store them in a dictionary
            for ap_path in access_points:
                access_point = bus.get(".NetworkManager", ap_path)
                ssid = bytearray(access_point.Ssid).decode()
                strength = access_point.Strength
                security = "None" if not access_point.WpaFlags and not access_point.RsnFlags else "WPA/WPA2"

                wifi_networks.append({
                    "SSID": ssid,
                    "Strength": strength,
                    "Security": security
                })
            return wifi_networks
        time.sleep(1)

###################################################################################################
if __name__ == "__main__":
    wifi_interface = get_wifi_interface_name()
    if wifi_interface:
        print(f"Found Wi-Fi Interface: {wifi_interface}")
        wifi_networks_info = scan_for_wifi_devices(wifi_interface)
        if wifi_networks_info:
            for network in wifi_networks_info:
                print(f"SSID: {network['SSID']}, Strength: {network['Strength']}%, Security: {network['Security']}")
    else:
        print(f"No Wi-Fi Interface found. Unable to scan")
