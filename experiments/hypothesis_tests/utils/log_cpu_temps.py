#!/usr/bin/env python3
"""
CPU Temperature Logger Utility

This script periodically runs the 'sensors' command, parses CPU temperatures
(Package and individual cores), and logs them to a CSV file.

It stops when a 'stop_temp_logging.flag' file is detected in the parent directory.
"""

import subprocess
import time
import re
import os
from datetime import datetime

LOG_INTERVAL = 1  # Seconds
OUTPUT_CSV_FILE = "temperature_log.csv" # Will be created in the script's parent directory
STOP_FLAG_FILE = "stop_temp_logging.flag" # Will be checked in the script's parent directory

def get_cpu_temperatures():
    """Runs 'sensors' and parses Package and Core temperatures."""
    temps = {"Package": None}
    try:
        result = subprocess.run(["sensors"], capture_output=True, text=True, check=True)
        output = result.stdout

        # Regex to find Package temperature
        package_match = re.search(r"Package id 0:\s*\+?([\d\.]+)", output)
        if package_match:
            temps["Package"] = float(package_match.group(1))

        # Regex to find Core temperatures
        core_matches = re.finditer(r"Core (\d+):\s*\+?([\d\.]+)", output)
        for match in core_matches:
            core_id = int(match.group(1))
            temp_val = float(match.group(2))
            temps[f"Core{core_id}"] = temp_val
        
    except FileNotFoundError:
        print("Error: 'sensors' command not found. Please ensure lm-sensors is installed.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running 'sensors': {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while getting temperatures: {e}")
        return None
    
    return temps

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    output_file_path = os.path.join(parent_dir, OUTPUT_CSV_FILE)
    stop_flag_path = os.path.join(parent_dir, STOP_FLAG_FILE)

    # Ensure stop flag doesn't exist from a previous run
    if os.path.exists(stop_flag_path):
        os.remove(stop_flag_path)
        print(f"Removed pre-existing stop flag: {stop_flag_path}")

    print(f"Starting CPU temperature logging to: {output_file_path}")
    print(f"Logging interval: {LOG_INTERVAL} seconds")
    print(f"To stop logging, create a file named: {STOP_FLAG_FILE} in {parent_dir}")

    # Determine headers dynamically based on first successful read
    header_written = False
    num_cores = 0
    while not header_written:
        initial_temps = get_cpu_temperatures()
        if initial_temps:
            core_keys = sorted([key for key in initial_temps if key.startswith("Core")], key=lambda x: int(x[4:]))
            num_cores = len(core_keys)
            headers = ["Timestamp", "Package_Temp"] + [f"Core{i}_Temp" for i in range(num_cores)]
            try:
                with open(output_file_path, 'w', newline='') as f_out:
                    f_out.write(",".join(headers) + "\n")
                header_written = True
                print("CSV header written.")
            except IOError as e:
                print(f"Error writing header to CSV: {e}. Retrying...")
                time.sleep(LOG_INTERVAL)
        else:
            print("Failed to get initial temperatures for header. Retrying...")
            time.sleep(LOG_INTERVAL) # Wait before retrying
            if os.path.exists(stop_flag_path):
                print("Stop flag detected during header writing. Exiting.")
                return

    try:
        while not os.path.exists(stop_flag_path):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Millisecond precision
            temps = get_cpu_temperatures()

            if temps:
                row = [timestamp]
                row.append(str(temps.get("Package", "NaN")))
                for i in range(num_cores):
                    row.append(str(temps.get(f"Core{i}", "NaN")))
                
                try:
                    with open(output_file_path, 'a', newline='') as f_out:
                        f_out.write(",".join(row) + "\n")
                except IOError as e:
                    print(f"Error writing to CSV: {e}")
            else:
                print("Failed to retrieve temperatures. Skipping this interval.")

            time.sleep(LOG_INTERVAL)
    except KeyboardInterrupt:
        print("\nLogging interrupted by user (Ctrl+C).")
    finally:
        print(f"CPU temperature logging stopped. Log file: {output_file_path}")
        if os.path.exists(stop_flag_path):
            os.remove(stop_flag_path)
            print(f"Cleaned up stop flag: {stop_flag_path}")

if __name__ == "__main__":
    main() 