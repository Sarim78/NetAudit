# NetAudit

A personal network audit tool that scans your device's full WiFi connection history, collects live network data, and exports everything into a PDF report and a Power BI ready CSV file.

---

## What It Does

NetAudit pulls two types of data from your Windows machine.

The first is historical data. Windows stores a record of every WiFi network you have ever connected to, along with connection and disconnection timestamps from the Event Viewer. NetAudit reads all of that and compiles it into a clean table.

The second is live network data. It scans your current network and collects your device info, IP addresses, DNS servers, gateway, and a breakdown of all connected devices with their open ports and vendor names.

Both datasets get combined and exported as a PDF audit report and a structured CSV file that loads directly into Power BI for interactive dashboards.

---

## Tech Stack

- Python 3.10+
- nmap + python-nmap (live network scanning)
- Scapy (packet level network data)
- ReportLab (PDF generation)
- pandas (data processing and CSV export)
- Windows Registry + Event Viewer (WiFi history collection)

---

## Project Structure

```
NetAudit/
├── main.py                  # Entry point, runs everything in order
├── scanners/
│   ├── __init__.py
│   ├── wifi_history.py      # Pulls saved WiFi profiles and event log timestamps
│   ├── network_scan.py      # Live nmap scan of current network
│   └── system_info.py       # Device info, IP, DNS, gateway, adapter details
├── processors/
│   ├── __init__.py
│   └── data_merger.py       # Combines all scanner output into one clean dataset
├── exporters/
│   ├── __init__.py
│   ├── pdf_report.py        # Generates the PDF audit report
│   └── csv_export.py        # Exports structured data for Power BI
├── output/
│   ├── reports/             # PDF files land here
│   └── data/                # CSV files for Power BI land here
├── requirements.txt
└── README.md
```

---

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/Sarim78/netaudit.git
cd netaudit
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Install nmap**

Download and install nmap from https://nmap.org/download.html and make sure it is added to your system PATH.

**4. Run the tool**

```bash
python main.py
```

> Note: Run as Administrator for full access to Event Viewer logs and network scanning capabilities.

---

## Output

After running, two files are generated inside the `output/` folder.

`output/reports/netaudit_report.pdf` is a formatted PDF containing your device summary, full WiFi connection history with timestamps, and a table of all devices found on your current network.

`output/data/netaudit_data.csv` is a structured CSV file ready to be loaded into Power BI. It contains all the same data in a flat format suitable for building charts and dashboards.

---

## Power BI Setup

1. Open Power BI Desktop
2. Click Get Data and select Text/CSV
3. Navigate to `output/data/netaudit_data.csv`
4. Load and start building visuals

Suggested visuals include a timeline of WiFi connections over time, a bar chart of most frequently connected networks, a table of live devices with open ports, and a vendor breakdown pie chart.

---

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or higher
- nmap installed and in PATH
- Administrator privileges recommended

---

## Use Case

This project was built for learning purposes to explore network engineering and cybersecurity fundamentals including network scanning, OS level data collection, and security reporting. It functions as a personal network audit tool and demonstrates skills in Python scripting, network analysis, and data visualization.

---
