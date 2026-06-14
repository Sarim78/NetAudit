import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


OUTPUT_DIR = "output/reports"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontSize=24,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontSize=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#555555"),
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=20,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="BodySmall",
        fontSize=9,
        fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        spaceAfter=4
    ))

    return styles


def section_header(text, styles):
    return [
        Paragraph(text, styles["SectionHeader"]),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceAfter=8)
    ]


def build_table(headers: list, rows: list, col_widths: list = None):
    data = [headers] + rows

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f9f9f9"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(style)
    return table


def export_pdf(data: dict) -> str:
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"netaudit_report_{timestamp}.pdf"
    path = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = build_styles()
    story = []

    # Title
    generated_at = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph("NetAudit", styles["ReportTitle"]))
    story.append(Paragraph(f"Network Audit Report generated on {generated_at}", styles["ReportSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e"), spaceAfter=20))

    # Device Info
    story += section_header("Device Information", styles)
    device = data.get("device", {})
    ip_info = data.get("ip_info", {})
    device_rows = [
        ["Hostname", device.get("hostname", "N/A")],
        ["Operating System", device.get("os", "N/A")],
        ["OS Version", device.get("os_version", "N/A")],
        ["Processor", device.get("processor", "N/A")],
        ["Architecture", device.get("architecture", "N/A")],
        ["MAC Address", device.get("mac_address", "N/A")],
        ["Local IP", ip_info.get("local_ip", "N/A")],
        ["Public IP", ip_info.get("public_ip", "N/A")],
        ["Gateway", ip_info.get("gateway", "N/A")],
        ["DNS Servers", ", ".join(ip_info.get("dns_servers", []))],
    ]
    story.append(build_table(["Field", "Value"], device_rows, col_widths=[2 * inch, 5 * inch]))
    story.append(Spacer(1, 12))

    # Saved WiFi Profiles
    story += section_header("Saved WiFi Profiles", styles)
    profiles = data.get("saved_wifi_profiles", [])
    if profiles:
        profile_rows = [[p.get("ssid", ""), p.get("auth_type", ""), p.get("encryption", "")] for p in profiles]
        story.append(build_table(["SSID", "Auth Type", "Encryption"], profile_rows, col_widths=[3 * inch, 2 * inch, 2 * inch]))
    else:
        story.append(Paragraph("No saved WiFi profiles found.", styles["BodySmall"]))
    story.append(Spacer(1, 12))

    # WiFi Connection History
    story += section_header("WiFi Connection History", styles)
    events = data.get("wifi_connection_events", [])
    if events:
        event_rows = [
            [
                e.get("ssid", ""),
                e.get("event", ""),
                str(e.get("timestamp", ""))
            ]
            for e in events[:50]
        ]
        story.append(build_table(["SSID", "Event", "Timestamp"], event_rows, col_widths=[2.5 * inch, 1.5 * inch, 3 * inch]))
        if len(events) > 50:
            story.append(Paragraph(f"Showing 50 of {len(events)} events. Full data available in CSV export.", styles["BodySmall"]))
    else:
        story.append(Paragraph("No connection events found.", styles["BodySmall"]))
    story.append(Spacer(1, 12))

    # Live Devices
    story += section_header("Live Network Devices", styles)
    devices = data.get("live_devices", [])
    if devices:
        device_rows = [
            [
                d.get("ip", ""),
                d.get("hostname", ""),
                d.get("mac", ""),
                d.get("vendor", ""),
                ", ".join([str(p["port"]) for p in d.get("open_ports", [])])
            ]
            for d in devices
        ]
        story.append(build_table(
            ["IP Address", "Hostname", "MAC", "Vendor", "Open Ports"],
            device_rows,
            col_widths=[1.2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.3 * inch]
        ))
    else:
        story.append(Paragraph("No live devices found.", styles["BodySmall"]))
    story.append(Spacer(1, 12))

    # ARP Table
    story += section_header("ARP Table", styles)
    arp = data.get("arp_table", [])
    if arp:
        arp_rows = [[e.get("ip", ""), e.get("mac", ""), e.get("vendor", ""), e.get("type", "")] for e in arp]
        story.append(build_table(["IP Address", "MAC Address", "Vendor", "Type"], arp_rows, col_widths=[1.75 * inch, 2 * inch, 2.5 * inch, 1.25 * inch]))
    else:
        story.append(Paragraph("No ARP entries found.", styles["BodySmall"]))

    doc.build(story)
    print(f"[pdf_report] PDF report exported: {path}")
    return path


if __name__ == "__main__":
    sample = {
        "device": {"hostname": "TestPC", "os": "Windows 11", "os_version": "10.0.22631", "processor": "AMD Ryzen 5", "architecture": "AMD64", "mac_address": "AA:BB:CC:DD:EE:FF"},
        "ip_info": {"local_ip": "192.168.1.5", "public_ip": "8.8.8.8", "gateway": "192.168.1.1", "dns_servers": ["8.8.8.8", "8.8.4.4"]},
        "saved_wifi_profiles": [{"ssid": "HomeNetwork", "auth_type": "WPA2", "encryption": "CCMP"}],
        "wifi_connection_events": [{"ssid": "HomeNetwork", "event": "Connected", "timestamp": "2024-01-01 10:00:00"}],
        "live_devices": [{"ip": "192.168.1.1", "hostname": "router", "mac": "AA:BB:CC:DD:EE:FF", "vendor": "Cisco", "status": "up", "open_ports": [{"port": 80, "protocol": "tcp", "service": "http", "version": ""}]}],
        "arp_table": [{"ip": "192.168.1.1", "mac": "AA:BB:CC:DD:EE:FF", "type": "dynamic", "vendor": "Cisco"}]
    }
    export_pdf(sample)