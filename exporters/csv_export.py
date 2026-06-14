import pandas as pd
import os
from datetime import datetime


OUTPUT_DIR = "output/data"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def export_csv(data: dict) -> str:
    """
    Takes merged data from data_merger.py and exports structured CSVs for Power BI.
    Returns the path to the main output file.
    """
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    export_device_info(data, timestamp)
    export_wifi_profiles(data, timestamp)
    export_wifi_events(data, timestamp)
    export_live_devices(data, timestamp)
    export_arp_table(data, timestamp)

    print(f"[csv_export] All CSV files exported to {OUTPUT_DIR}/")
    return OUTPUT_DIR


def export_device_info(data: dict, timestamp: str):
    device = data.get("device", {})
    ip_info = data.get("ip_info", {})

    combined = {**device, **ip_info}
    combined["dns_servers"] = ", ".join(combined.get("dns_servers", []))

    df = pd.DataFrame([combined])
    path = os.path.join(OUTPUT_DIR, f"device_info_{timestamp}.csv")
    df.to_csv(path, index=False)
    print(f"[csv_export] Device info exported: {path}")


def export_wifi_profiles(data: dict, timestamp: str):
    profiles = data.get("saved_wifi_profiles", [])
    if not profiles:
        print("[csv_export] No saved WiFi profiles to export.")
        return

    df = pd.DataFrame(profiles)
    path = os.path.join(OUTPUT_DIR, f"wifi_profiles_{timestamp}.csv")
    df.to_csv(path, index=False)
    print(f"[csv_export] WiFi profiles exported: {path}")


def export_wifi_events(data: dict, timestamp: str):
    events = data.get("wifi_connection_events", [])
    if not events:
        print("[csv_export] No WiFi connection events to export.")
        return

    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp", ascending=True)

    path = os.path.join(OUTPUT_DIR, f"wifi_events_{timestamp}.csv")
    df.to_csv(path, index=False)
    print(f"[csv_export] WiFi events exported: {path}")


def export_live_devices(data: dict, timestamp: str):
    devices = data.get("live_devices", [])
    if not devices:
        print("[csv_export] No live devices to export.")
        return

    rows = []
    for device in devices:
        open_ports = device.get("open_ports", [])
        if open_ports:
            for port_info in open_ports:
                rows.append({
                    "ip": device.get("ip"),
                    "hostname": device.get("hostname"),
                    "mac": device.get("mac"),
                    "vendor": device.get("vendor"),
                    "status": device.get("status"),
                    "port": port_info.get("port"),
                    "protocol": port_info.get("protocol"),
                    "service": port_info.get("service"),
                    "version": port_info.get("version")
                })
        else:
            rows.append({
                "ip": device.get("ip"),
                "hostname": device.get("hostname"),
                "mac": device.get("mac"),
                "vendor": device.get("vendor"),
                "status": device.get("status"),
                "port": None,
                "protocol": None,
                "service": None,
                "version": None
            })

    df = pd.DataFrame(rows)
    path = os.path.join(OUTPUT_DIR, f"live_devices_{timestamp}.csv")
    df.to_csv(path, index=False)
    print(f"[csv_export] Live devices exported: {path}")


def export_arp_table(data: dict, timestamp: str):
    arp = data.get("arp_table", [])
    if not arp:
        print("[csv_export] No ARP entries to export.")
        return

    df = pd.DataFrame(arp)
    path = os.path.join(OUTPUT_DIR, f"arp_table_{timestamp}.csv")
    df.to_csv(path, index=False)
    print(f"[csv_export] ARP table exported: {path}")


if __name__ == "__main__":
    sample = {
        "device": {"hostname": "TestPC", "os": "Windows 11"},
        "ip_info": {"local_ip": "192.168.1.5", "public_ip": "8.8.8.8", "gateway": "192.168.1.1", "dns_servers": ["8.8.8.8"]},
        "saved_wifi_profiles": [{"ssid": "HomeNetwork", "auth_type": "WPA2", "encryption": "CCMP"}],
        "wifi_connection_events": [{"ssid": "HomeNetwork", "event": "Connected", "timestamp": "2024-01-01 10:00:00"}],
        "live_devices": [{"ip": "192.168.1.1", "hostname": "router", "mac": "AA:BB:CC:DD:EE:FF", "vendor": "Cisco", "status": "up", "open_ports": [{"port": 80, "protocol": "tcp", "service": "http", "version": ""}]}],
        "arp_table": [{"ip": "192.168.1.1", "mac": "AA:BB:CC:DD:EE:FF", "type": "dynamic", "vendor": "Cisco"}]
    }
    export_csv(sample)