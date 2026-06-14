from processors import merge_all_data
from exporters import export_csv, export_pdf


def main():
    print("=" * 50)
    print("  NetAudit - Network Audit Tool")
    print("=" * 50)
    print()

    print("[main] Starting data collection...\n")
    data = merge_all_data()

    print("\n[main] Exporting results...\n")
    csv_path = export_csv(data)
    pdf_path = export_pdf(data)

    print()
    print("=" * 50)
    print("  Audit Complete")
    print("=" * 50)
    print(f"  PDF Report : {pdf_path}")
    print(f"  CSV Data   : {csv_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()