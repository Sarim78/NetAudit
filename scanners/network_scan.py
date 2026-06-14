import nmap
import socket
import re
import subprocess
from mac_vendor_lookup import MacLookup


mac_lookup = MacLookup()


def get_local_subnet() -> str:
    """Derive the local subnet from the machine's IP address."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        subnet = ".".join(local_ip.split(".")[:3]) + ".0/24"
        return subnet
    except Exception as e:
        print(f"[network_scan] Error detecting subnet: {e}")
        return "192.168.1.0/24"


def get_vendor(mac: str) -> str:
    """Look up the vendor name from a MAC address."""
    try:
        return mac_lookup.lookup(mac)
    except Exception:
        return "Unknown"


def scan_network(subnet: str = None) -> list[dict]:
    """
    Run an nmap scan on the local subnet.
    Returns a list of discovered devices with IP, MAC, hostname, open ports, and vendor.
    """
    if not subnet:
        subnet = get_local_subnet()

    print(f"[network_scan] Scanning subnet: {subnet}")

    devices = []

    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=subnet, arguments="-sn")

        host_list = nm.all_hosts()
        print(f"[network_scan] Found {len(host_list)} hosts, scanning ports...")

        for host in host_list:
            device = {
                "ip": host,
                "hostname": "Unknown",
                "mac": "Unknown",
                "vendor": "Unknown",
                "open_ports": [],
                "status": nm[host].state()
            }

            if "hostnames" in nm[host] and nm[host]["hostnames"]:
                device["hostname"] = nm[host]["hostnames"][0].get("name", "Unknown")

            if "mac" in nm[host].get("addresses", {}):
                device["mac"] = nm[host]["addresses"]["mac"]
                device["vendor"] = get_vendor(device["mac"])

            devices.append(device)

        print(f"[network_scan] Running port scan on discovered hosts...")
        for device in devices:
            device["open_ports"] = scan_ports(device["ip"])

    except Exception as e:
        print(f"[network_scan] Error during network scan: {e}")

    return devices


def scan_ports(ip: str, ports: str = "22,80,443,3389,8080,21,23,25,53,110") -> list[dict]:
    """
    Scan common ports on a single IP.
    Returns a list of open ports with service names.
    """
    open_ports = []

    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=ip, ports=ports, arguments="-sV --open")

        if ip in nm.all_hosts():
            for proto in nm[ip].all_protocols():
                port_list = nm[ip][proto].keys()
                for port in port_list:
                    port_info = nm[ip][proto][port]
                    if port_info["state"] == "open":
                        open_ports.append({
                            "port": port,
                            "protocol": proto,
                            "service": port_info.get("name", "Unknown"),
                            "version": port_info.get("version", "")
                        })

    except Exception as e:
        print(f"[network_scan] Error scanning ports on {ip}: {e}")

    return open_ports


def get_arp_table() -> list[dict]:
    """Pull the ARP table to get a quick snapshot of known local devices."""
    devices = []

    try:
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        for line in lines:
            match = re.match(r"\s*([\d.]+)\s+([\w-]+)\s+(\w+)", line)
            if match:
                ip = match.group(1).strip()
                mac = match.group(2).strip()
                entry_type = match.group(3).strip()

                if mac not in ("ff-ff-ff-ff-ff-ff",):
                    devices.append({
                        "ip": ip,
                        "mac": mac.replace("-", ":").upper(),
                        "type": entry_type,
                        "vendor": get_vendor(mac.replace("-", ":").upper())
                    })

    except Exception as e:
        print(f"[network_scan] Error fetching ARP table: {e}")

    return devices


def get_network_scan() -> dict:
    """
    Main function called by data_merger.py.
    Returns full network scan results and ARP table.
    """
    subnet = get_local_subnet()

    print("[network_scan] Starting live network scan...")
    devices = scan_network(subnet)

    print("[network_scan] Fetching ARP table...")
    arp_table = get_arp_table()

    print(f"[network_scan] Scan complete. {len(devices)} devices found.")

    return {
        "subnet": subnet,
        "devices": devices,
        "arp_table": arp_table
    }


if __name__ == "__main__":
    data = get_network_scan()

    print(f"\n--- Subnet: {data['subnet']} ---")

    print("\n--- Devices ---")
    for d in data["devices"]:
        print(f"  {d['ip']} | {d['hostname']} | {d['mac']} | {d['vendor']} | Ports: {[p['port'] for p in d['open_ports']]}")

    print("\n--- ARP Table ---")
    for entry in data["arp_table"][:10]:
        print(f"  {entry}")