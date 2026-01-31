import os
import re
import csv
from datetime import datetime

# Configurable 
log_file = "directory_log.txt"
metrics_file = "system_metrics.csv"
report_file = "summary_report.txt"

def generate_report():
    if not os.path.exists(log_file):
        print(f"Error: {log_file} not found. Run the monitor first.")
        return

    # Tracking variables
    creations = 0
    deletions = 0
    modifications = 0
    file_sizes = []
    notable_events = []

    with open(log_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        # 1. Directory Change Logs Parsing
        if "FILE CREATED" in line:
            creations += 1
            # Extract size using regex (looks for Size= followed by numbers)
            size_match = re.search(r"Size=(\d+)", line)
            if size_match:
                file_sizes.append(int(size_match.group(1)))

        elif "FILE DELETED" in line:
            deletions += 1

        elif "FILE MODIFIED" in line:
            modifications += 1
            # Mark large modifications as "Notable"
            if "Size (Bytes)" in line:
                notable_events.append(f"Modification: {line.split('FILE MODIFIED:')[1].strip()}")

    # Key Statistics
    total_events = creations + deletions + modifications
    avg_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
    max_size = max(file_sizes) if file_sizes else 0

# --- UPDATED: SYSTEM PERFORMANCE ANALYTICS ---
    cpu_values = []
    ram_values = []

    if os.path.exists(metrics_file):
        with open(metrics_file, "r") as f:
            # We use DictReader because your monitor script writes headers!
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # We use the specific names from your monitor script
                    cpu_values.append(float(row["cpu_usage_percent"]))
                    ram_values.append(float(row["memory_usage_percent"]))
                except (KeyError, ValueError, TypeError):
                    # This skips the header and any bad data automatically
                    continue 

    # Calculate Stats (Same as before)
    avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
    max_cpu = max(cpu_values) if cpu_values else 0
    avg_ram = sum(ram_values) / len(ram_values) if ram_values else 0
    max_ram = max(ram_values) if ram_values else 0



    # Building the Summary Report String
    report = []
    report.append("="*50)
    report.append(f"CENTRALIZED SUMMARY REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("="*50)
    
    report.append("\n[1] DIRECTORY CHANGE LOGS SUMMARY")
    report.append(f"Total File Creations:    {creations}")
    report.append(f"Total File Deletions:    {deletions}")
    report.append(f"Total File Modifications: {modifications}")
    report.append(f"Total Events Logged:     {total_events}")

    report.append("\n[2] KEY STATISTICS")
    report.append(f"Average Created File Size: {avg_size:.2f} Bytes")
    report.append(f"Largest New File:         {max_size} Bytes")

    report.append("\n[3] NOTABLE EVENTS (Alerts/Significant Changes)")
    if notable_events:
        for event in notable_events[:5]: # Show last 5
            report.append(f"- {event}")
    else:
        report.append("- No significant metadata changes detected.")
    
    report.append("\n" + "="*50)

    # Building the System Performance section of the report
    report.append("\n[4] SYSTEM PERFORMANCE ANALYTICS")
    report.append(f"Average CPU Usage: {avg_cpu:.2f}%")
    report.append(f"Peak CPU Usage:    {max_cpu:.2f}%")
    report.append(f"Average RAM Usage: {avg_ram:.2f}%")
    report.append(f"Peak RAM Usage:    {max_ram:.2f}%")

    # Optional: Add a simple Logic/Alert
    if max_cpu > 80 or max_ram > 80:
        report.append("STATUS: Warning - High Resource Usage Detected")
    else:
        report.append("STATUS: Normal - System resources stable")


    # Output to file
    with open(report_file, "w") as f:
        f.write("\n".join(report))
    
    # Output to terminal
    print("\n".join(report))
    print(f"\nReport successfully saved to: {report_file}")

if __name__ == "__main__":
    generate_report()