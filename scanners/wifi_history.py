import subprocess
import re
from datetime import datetime

def get_saved_profiles() -> list[dict]:
    """Pull all saved WiFi profiles from Windows using netsh."""
    profiles = []

    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "profiles"],
            capture_output=True,
            text=True
        )
        names = re.findall(r"All User Profile\s*:\s*(.+)", result.stdout)

        for name in names:
            name = name.strip()
            profile = _get_profile_details(name)
            profiles.append(profile)

    except Exception as e:
        print(f"[wifi_history] Error fetching profiles: {e}")

    return profiles

def _get_profile_details(name: str) -> dict:
    """Pull details for a single WiFi profile."""
    profile = {
        "ssid": name,
        "auth_type": "Unknown",
        "encryption": "Unknown",
        "password": "Hidden"
    }

    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "profile", f"name={name}", "key=clear"],
            capture_output=True,
            text=True
        )
        output = result.stdout

        auth_match = re.search(r"Authentication\s*:\s*(.+)", output)
        if auth_match:
            profile["auth_type"] = auth_match.group(1).strip()

        enc_match = re.search(r"Cipher\s*:\s*(.+)", output)
        if enc_match:
            profile["encryption"] = enc_match.group(1).strip()

        pwd_match = re.search(r"Key Content\s*:\s*(.+)", output)
        if pwd_match:
            profile["password"] = pwd_match.group(1).strip()

    except Exception as e:
        print(f"[wifi_history] Error fetching details for {name}: {e}")

    return profile

def get_connection_events() -> list[dict]:
    """
    Pull WiFi connect and disconnect events from Windows Event Viewer.
    Event ID 8001 = connected, Event ID 8003 = disconnected.
    """
    events = []

    query = (
        "*[System[Provider[@Name='Microsoft-Windows-WLAN-AutoConfig'] "
        "and (EventID=8001 or EventID=8003)]]"
    )

    try:
        result = subprocess.run(
            [
                "wevtutil", "qe", "Microsoft-Windows-WLAN-AutoConfig/Operational",
                f"/q:{query}",
                "/f:text",
                "/rd:false"
            ],
            capture_output=True,
            text=True
        )

        raw = result.stdout
        blocks = raw.strip().split("\n\n")

        for block in blocks:
            event = _parse_event_block(block)
            if event:
                events.append(event)

    except Exception as e:
        print(f"[wifi_history] Error fetching event logs: {e}")

    return events

def _parse_event_block(block: str) -> dict | None:
    """Parse a single event log text block into a dict."""
    try:
        event_id_match = re.search(r"Event ID:\s*(\d+)", block)
        time_match = re.search(r"Date:\s*(.+)", block)
        ssid_match = re.search(r"SSID\s*[:\s]+([^\s].+)", block)

        if not event_id_match or not time_match:
            return None

        event_id = int(event_id_match.group(1).strip())
        raw_time = time_match.group(1).strip()
        ssid = ssid_match.group(1).strip() if ssid_match else "Unknown"

        try:
            timestamp = datetime.strptime(raw_time, "%m/%d/%Y %I:%M:%S %p")
        except ValueError:
            timestamp = raw_time

        event_type = "Connected" if event_id == 8001 else "Disconnected"

        return {
            "ssid": ssid,
            "event": event_type,
            "timestamp": timestamp
        }

    except Exception:
        return None

def get_wifi_history() -> dict:
    """
    Main function called by data_merger.py.
    Returns saved profiles and connection event history.
    """
    print("[wifi_history] Collecting saved WiFi profiles...")
    profiles = get_saved_profiles()

    print("[wifi_history] Collecting connection event history...")
    events = get_connection_events()

    print(f"[wifi_history] Found {len(profiles)} saved profiles and {len(events)} events.")

    return {
        "saved_profiles": profiles,
        "connection_events": events
    }
if __name__ == "__main__":
    data = get_wifi_history()

    print("\n--- Saved Profiles ---")
    for p in data["saved_profiles"]:
        print(p)

    print("\n--- Connection Events ---")
    for e in data["connection_events"][:10]:
        print(e)