from scanners import get_wifi_history, get_system_info, get_network_scan


def merge_all_data() -> dict:
    """
    Calls all three scanners and merges their output into one unified dataset.
    This is the single object passed to both exporters.
    """

    wifi_data = get_wifi_history()
    system_data = get_system_info()
    network_data = get_network_scan()

    merged = {
        "device": system_data.get("device", {}),
        "ip_info": system_data.get("ip_info", {}),
        "adapters": system_data.get("adapters", []),
        "saved_wifi_profiles": wifi_data.get("saved_profiles", []),
        "wifi_connection_events": wifi_data.get("connection_events", []),
        "subnet": network_data.get("subnet", ""),
        "live_devices": network_data.get("devices", []),
        "arp_table": network_data.get("arp_table", [])
    }

    print(f"[data_merger] Merge complete.")
    print(f"  Device: {merged['device'].get('hostname', 'Unknown')}")
    print(f"  Saved WiFi profiles: {len(merged['saved_wifi_profiles'])}")
    print(f"  WiFi connection events: {len(merged['wifi_connection_events'])}")
    print(f"  Live devices found: {len(merged['live_devices'])}")
    print(f"  ARP entries: {len(merged['arp_table'])}")

    return merged


if __name__ == "__main__":
    data = merge_all_data()

    print("\n--- Merged Data Keys ---")
    for key, value in data.items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} entries")
        elif isinstance(value, dict):
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")