import psutil
import time
import csv
from datetime import datetime

OUTPUT_FILE = "system_metrics.csv"
INTERVAL = 10  # seconds

# limit numbers to 4 significant figures
def format_number(num):
    return float(f"{num:.4g}")

# limit percentages to 2 significant figures
def format_percent(num):
    return float(f"{num:.2g}")

# convert bytes to GB and limit to 4 significant figures
def bytes_to_gb(num):
    return float(f"{num / (1024**3):.4g}")

def get_cpu_info():
    return {
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "load_avg_1": psutil.getloadavg()[0],
        "load_avg_5": psutil.getloadavg()[1],
        "load_avg_15": psutil.getloadavg()[2]
    }

def get_memory_info():
    mem = psutil.virtual_memory()
    return {
        "total_memory": mem.total,
        "used_memory": mem.used,
        "available_memory": mem.available,
        "memory_usage_percent": mem.percent
    }

def get_disk_info():
    disk = psutil.disk_usage('/')
    return {
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "disk_usage_percent": disk.percent
    }

def get_uptime_info():
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    return {
        "system_uptime_seconds": int(uptime_seconds)
    }
    
def get_process_info():
    processes = list(psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']))

    running = sum(1 for p in processes if p.info['status'] == psutil.STATUS_RUNNING)
    sleeping = sum(1 for p in processes if p.info['status'] == psutil.STATUS_SLEEPING)

    top_cpu = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)[:3]
    top_mem = sorted(processes, key=lambda p: p.info['memory_percent'], reverse=True)[:3]

    return {
        "total_processes": len(processes),
        "running_processes": running,
        "sleeping_processes": sleeping,
        "top_cpu_processes": "; ".join([p.info['name'] for p in top_cpu]),
        "top_memory_processes": "; ".join([p.info['name'] for p in top_mem])
    }

def main():
    header_written = False

    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = None

        print("System monitoring started... Press CTRL+C to stop.")

        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                data = {"timestamp": timestamp}
                data.update(get_cpu_info())
                data.update(get_memory_info())
                data.update(get_disk_info())
                data.update(get_uptime_info())
                data.update(get_process_info())

                if not header_written:
                    writer = csv.DictWriter(file, fieldnames=data.keys())
                    writer.writeheader()
                    header_written = True

                writer.writerow(data)
                file.flush()

                print(f"[{timestamp}] Data collected.")
                time.sleep(INTERVAL)

        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()