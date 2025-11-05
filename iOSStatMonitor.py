import subprocess
import time
import re
import os

PROCESS_NAME = "zrtc_demo_classi"   # <-- change to your process name
INTERVAL = 0                        # seconds between samples
DURATION = 120                      # total runtime (2 minutes)
CPU_FILE = "cpu.txt"
MEM_FILE = "mem.txt"

# --- Remove old log files if they exist ---
for f in (CPU_FILE, MEM_FILE):
    try:
        os.remove(f)
        print(f"Removed old file: {f}")
    except FileNotFoundError:
        pass

print(f"Monitoring '{PROCESS_NAME}' every {INTERVAL}s for {DURATION}s...")
print(f"Logging to {CPU_FILE} and {MEM_FILE}")

def convert_to_mb(mem_str):
    """Convert macOS top MEM string (e.g. '34M+', '4736K') to MB."""
    mem_str = mem_str.strip().replace("+", "").upper()
    if mem_str.endswith("G"):
        return float(mem_str[:-1]) * 1024
    elif mem_str.endswith("M"):
        return float(mem_str[:-1])
    elif mem_str.endswith("K"):
        return float(mem_str[:-1]) / 1024
    elif mem_str.endswith("B"):
        return float(mem_str[:-1]) / (1024 * 1024)
    else:
        try:
            return float(mem_str)
        except ValueError:
            return 0.0

start_time = time.time()

try:
    while True:
        elapsed = time.time() - start_time
        if elapsed >= DURATION:
            print("\n⏰ 2 minutes reached — stopping monitoring.")
            break

        # Use top -l 2 to get accurate CPU
        cmd = f"top -l 2 -o cpu | grep {PROCESS_NAME} | tail -1"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        line = result.stdout.strip()

        if line:
            parts = re.split(r"\s+", line)
            if len(parts) >= 8:
                cpu_val = parts[2].replace("%", "")
                mem_val_raw = parts[7]
                mem_mb = convert_to_mb(mem_val_raw)

                with open(CPU_FILE, "a") as f_cpu:
                    f_cpu.write(f"{cpu_val}\n")

                with open(MEM_FILE, "a") as f_mem:
                    f_mem.write(f"{mem_mb:.2f}\n")
        else:
            print(f"⚠️ Process '{PROCESS_NAME}' not found in top output.")

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\n🛑 Interrupted by user.")

# --- Kill the process after monitoring ---
print(f"💀 Killing process '{PROCESS_NAME}' with pkill...")
subprocess.run(["pkill", "-9", PROCESS_NAME])
print("✅ Process killed. Monitoring finished.")
