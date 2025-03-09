#!/usr/bin/env python3

from pydbus import SystemBus
from gi.repository import GLib
import time

#import function to get name of Wi-Fi interface
from get_wifi_interface_name import get_wifi_interface_name

def scan_wifi(interface_name):
    bus = SystemBus()
    network_manager = bus.get("org.freedesktop.NetworkManager")

    # Get all devices managed by NetworkManager
    devices = network_manager.GetDevices()

    # Find the Wi-Fi device
    wifi_device = None
    for device_path in devices:
        device = bus.get(".NetworkManager", device_path)
        if device.Interface == interface_name and device.DeviceType == 2:  # 2 represents Wi-Fi
            wifi_device = device
            break

    if not wifi_device:
        print(f"No Wi-Fi device found with interface '{interface_name}'")
        return

    # Get the current value of LastScan before triggering a new scan
    # Rate Limiting
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
            for ap_path in access_points:
                access_point = bus.get(".NetworkManager", ap_path)
                ssid = bytearray(access_point.Ssid).decode()
                strength = access_point.Strength
                security = "None" if not access_point.WpaFlags and not access_point.RsnFlags else "WPA/WPA2"
                print(f"SSID: {ssid}, Strength: {strength}%, Security: {security}")
            break
        time.sleep(1)

if __name__ == "__main__":
    wifi_interface = get_wifi_interface_name()
    if wifi_interface:
        print(f"Found Wi-Fi Interface: {wifi_interface}")
        scan_wifi(wifi_interface)
    else:
        print(f"No Wi-Fi Interface found. Unable to scan")
