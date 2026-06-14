import socket
import platform
import subprocess
import re
import uuid


def get_device_info() -> dict:
    """Pull basic device and OS information."""
    try:
        hostname = socket.gethostname()
        os_name = platform.system()
        os_version = platform.version()
        os_release = platform.release()
        machine = platform.machine()
        processor = platform.processor()
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

        return {
            "hostname": hostname,
            "os": f"{os_name} {os_release}",
            "os_version": os_version,
            "architecture": machine,
            "processor": processor,
            "mac_address": mac
        }

    except Exception as e:
        print(f"[system_info] Error fetching device info: {e}")
        return {}


def get_ip_info() -> dict:
    """Pull local IP, public IP, gateway, and DNS servers."""
    info = {
        "local_ip": "Unknown",
        "public_ip": "Unknown",
        "gateway": "Unknown",
        "dns_servers": []
    }

    try:
        hostname = socket.gethostname()
        info["local_ip"] = socket.gethostbyname(hostname)
    except Exception as e:
        print(f"[system_info] Error fetching local IP: {e}")

    try:
        result = subprocess.run(
            ["ipconfig", "/all"],
            capture_output=True,
            text=True
        )
        output = result.stdout

        gateway_match = re.search(r"Default Gateway[.\s]*:\s*([\d.]+)", output)
        if gateway_match:
            info["gateway"] = gateway_match.group(1).strip()

        dns_matches = re.findall(r"DNS Servers[.\s]*:\s*([\d.]+)", output)
        if dns_matches:
            info["dns_servers"] = dns_matches

    except Exception as e:
        print(f"[system_info] Error fetching gateway/DNS: {e}")

    try:
        import urllib.request
        public_ip = urllib.request.urlopen("https://api.ipify.org").read().decode("utf-8")
        info["public_ip"] = public_ip
    except Exception as e:
        print(f"[system_info] Error fetching public IP: {e}")

    return info


def get_network_adapters() -> list[dict]:
    """List all active network adapters and their details."""
    adapters = []

    try:
        result = subprocess.run(
            ["ipconfig", "/all"],
            capture_output=True,
            text=True
        )
        output = result.stdout

        blocks = re.split(r"\n(?=\S)", output)

        for block in blocks:
            if "adapter" not in block.lower():
                continue

            adapter = {}

            name_match = re.match(r"(.+adapter .+?):", block)
            if name_match:
                adapter["name"] = name_match.group(1).strip()

            ip_match = re.search(r"IPv4 Address[.\s]*:\s*([\d.]+)", block)
            if ip_match:
                adapter["ipv4"] = ip_match.group(1).replace("(Preferred)", "").strip()

            mac_match = re.search(r"Physical Address[.\s]*:\s*([\w-]+)", block)
            if mac_match:
                adapter["mac"] = mac_match.group(1).strip()

            status_match = re.search(r"Media State[.\s]*:\s*(.+)", block)
            adapter["status"] = status_match.group(1).strip() if status_match else "Connected"

            if adapter.get("name"):
                adapters.append(adapter)

    except Exception as e:
        print(f"[system_info] Error fetching adapters: {e}")

    return adapters


def get_system_info() -> dict:
    """
    Main function called by data_merger.py.
    Returns device info, IP info, and adapter list.
    """
    print("[system_info] Collecting device information...")
    device = get_device_info()

    print("[system_info] Collecting IP and network info...")
    ip_info = get_ip_info()

    print("[system_info] Collecting network adapters...")
    adapters = get_network_adapters()

    print(f"[system_info] Found {len(adapters)} network adapters.")

    return {
        "device": device,
        "ip_info": ip_info,
        "adapters": adapters
    }


if __name__ == "__main__":
    data = get_system_info()

    print("\n--- Device Info ---")
    for k, v in data["device"].items():
        print(f"  {k}: {v}")

    print("\n--- IP Info ---")
    for k, v in data["ip_info"].items():
        print(f"  {k}: {v}")

    print("\n--- Adapters ---")
    for a in data["adapters"]:
        print(f"  {a}")