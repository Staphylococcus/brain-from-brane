#!/usr/bin/env python3
"""
Analyzes results from H5 Experiments (Cooler or Hotter runs), correlating
CV and execution time data with CPU temperatures. 
Reads experiment data, timing logs, and temperature logs from CSV files.

This script requires the user to:
1.  Update the 'experiment_data' list with the CV/Mean Exec Time results
    from the console output of the experiment script (e.g., 'h5_exp_A_cooler_run.py').
2.  Configure the 'default_temp_log_filename' and 'default_timing_log_filename'
    or ensure the full paths in 'temp_log_file_path' and 'timing_log_file_path' are correct.
"""

import csv
from datetime import datetime
import statistics # Ensure statistics is imported
import os

# --- User Configuration ---
SCRIPT_DIR_ANALYSIS = os.path.dirname(os.path.abspath(__file__))

# 1. CHOOSE WHICH EXPERIMENT TO ANALYZE: "A" (Cooler) or "B" (Hotter)
EXPERIMENT_ID = "B" # Options: "A" or "B"

# 2. Define log file names based on EXPERIMENT_ID
if EXPERIMENT_ID == "A":
    exp_results_filename = "experiment_results_exp_A.csv"
    default_temp_log_filename = "temperature_log_h5_exp_A_cool.csv"
    default_timing_log_filename = "timing_log_exp_A.csv"
elif EXPERIMENT_ID == "B":
    exp_results_filename = "experiment_results_exp_B.csv"
    default_temp_log_filename = "temperature_log_h5_exp_B_hot.csv"
    default_timing_log_filename = "timing_log_exp_B.csv"
else:
    print(f"ERROR: Invalid EXPERIMENT_ID '{EXPERIMENT_ID}'. Choose 'A' or 'B'.")
    exit()

exp_results_file_path = os.path.join(SCRIPT_DIR_ANALYSIS, exp_results_filename)
temp_log_file_path = os.path.join(SCRIPT_DIR_ANALYSIS, default_temp_log_filename)
timing_log_file_path = os.path.join(SCRIPT_DIR_ANALYSIS, default_timing_log_filename)

# --- End User Configuration ---

def load_experiment_results_from_csv(file_path):
    """Loads experiment data (defect type, count, mean_ms, cv) from a CSV file."""
    data = []
    try:
        with open(file_path, 'r', newline='') as f_csv:
            reader = csv.DictReader(f_csv)
            for row in reader:
                try:
                    data.append({
                        "defect_type": row["DefectType"],
                        "count": int(row["DefectCount"]),
                        "mean_ms": float(row["MeanExecTimeMS"]),
                        "cv": float(row["CV"])
                    })
                except ValueError as ve:
                    print(f"Warning: Skipping row in {file_path} due to data conversion error: {row} - {ve}")
                    continue
                except KeyError as ke:
                    print(f"Warning: Skipping row in {file_path} due to missing key: {row} - {ke}")
                    continue
    except FileNotFoundError:
        print(f"ERROR: Experiment results file not found at '{file_path}'.")
        return None
    except Exception as e:
        print(f"Error reading or parsing experiment results file '{file_path}': {e}")
        return None
    
    if not data:
        print(f"No data loaded from experiment results file '{file_path}'. Ensure it's populated correctly.")
        return None
    return data

def parse_iso_timestamp(ts_str):
    """Parses an ISO format timestamp string into a datetime object."""
    try:
        # Python's isoformat() output can be directly parsed by fromisoformat
        return datetime.fromisoformat(ts_str)
    except ValueError:
        # Fallback for common CSV timestamp format if fromisoformat fails (e.g. from temp log)
        try:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            try:
                return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"Error: Could not parse timestamp '{ts_str}'.")
                return None

def get_temperature_stats(temp_data, start_time_dt, end_time_dt):
    """Calculates min, mean, max for Package_Temp and average of Core_Temps within a time window."""
    package_temps = []
    avg_core_temps = []
    num_cores = 0

    if not temp_data:
        return {"error": "No temperature data provided."}
    if not start_time_dt or not end_time_dt:
        return {"error": "Invalid start or end time for temperature analysis."}

    header = temp_data[0].keys() if temp_data else []
    core_temp_keys = [key for key in header if key.startswith("Core") and key.endswith("_Temp")]
    num_cores = len(core_temp_keys)

    for row in temp_data:
        # Use the more general parse_iso_timestamp for temperature log as well
        ts_dt = parse_iso_timestamp(row["Timestamp"])
        if ts_dt and start_time_dt <= ts_dt <= end_time_dt:
            try:
                if row["Package_Temp"] and row["Package_Temp"].lower() != 'nan':
                    package_temps.append(float(row["Package_Temp"]))
                
                if num_cores > 0:
                    current_core_temps = []
                    for core_key in core_temp_keys:
                        if row.get(core_key) and row[core_key].lower() != 'nan':
                            current_core_temps.append(float(row[core_key]))
                    if current_core_temps:
                        avg_core_temps.append(statistics.mean(current_core_temps))
            except ValueError:
                continue 

    if not package_temps:
        return {
            "pkg_min": "N/A", "pkg_mean": "N/A", "pkg_max": "N/A",
            "cores_min": "N/A", "cores_mean": "N/A", "cores_max": "N/A",
            "temp_sample_count": 0
        }

    return {
        "pkg_min": min(package_temps) if package_temps else "N/A",
        "pkg_mean": statistics.mean(package_temps) if package_temps else "N/A",
        "pkg_max": max(package_temps) if package_temps else "N/A",
        "cores_min": min(avg_core_temps) if avg_core_temps else "N/A",
        "cores_mean": statistics.mean(avg_core_temps) if avg_core_temps else "N/A",
        "cores_max": max(avg_core_temps) if avg_core_temps else "N/A",
        "temp_sample_count": len(package_temps)
    }

def load_timing_data(timing_log_path):
    """Loads timing data from the specified CSV log file."""
    timing_events = {}
    try:
        with open(timing_log_path, 'r', newline='') as f_timing:
            reader = csv.DictReader(f_timing)
            for row in reader:
                key = (row["DefectType"], int(row["DefectCount"]))
                event_time = parse_iso_timestamp(row["Timestamp"])
                if not event_time:
                    print(f"Warning: Could not parse timestamp in timing log for row: {row}")
                    continue
                
                if key not in timing_events:
                    timing_events[key] = {}
                timing_events[key][row["PhaseEvent"]] = event_time
    except FileNotFoundError:
        print(f"ERROR: Timing log file not found at '{timing_log_path}'.")
        return None
    except Exception as e:
        print(f"Error reading or parsing timing log file '{timing_log_path}': {e}")
        return None
    return timing_events

def main():
    print(f"--- Experiment Results Analysis for Experiment '{EXPERIMENT_ID}' ---")

    experiment_data = load_experiment_results_from_csv(exp_results_file_path)
    if experiment_data is None:
        print("Halting analysis due to issues with the experiment results file.")
        return

    if not os.path.exists(temp_log_file_path):
        print(f"ERROR: Temperature log file not found at '{temp_log_file_path}'. Please check the path.")
        return

    timing_events = load_timing_data(timing_log_file_path)
    if timing_events is None:
        print("Halting analysis due to issues with the timing log.")
        return

    all_temp_data = []
    try:
        with open(temp_log_file_path, 'r', newline='') as f_csv:
            reader = csv.DictReader(f_csv)
            for row in reader:
                all_temp_data.append(row)
    except Exception as e:
        print(f"Error reading or parsing temperature log file '{temp_log_file_path}': {e}")
        return

    if not all_temp_data:
        print(f"No data found in temperature log file '{temp_log_file_path}'.")
        return
        
    print(f"Using Experiment Results: {exp_results_file_path}")
    print(f"Using Temperature Log: {temp_log_file_path}")
    print(f"Using Timing Log: {timing_log_file_path}\n")
    
    results_with_temps = []

    for data_point in experiment_data:
        print(f"\nProcessing: Defect Type '{data_point['defect_type']}', Count: {data_point['count']}")
        print(f"  Mean Exec Time: {data_point['mean_ms']:.3f} ms, CV: {data_point['cv']:.6f}")
        
        current_key = (data_point["defect_type"], data_point["count"])
        if current_key not in timing_events:
            print(f"  Warning: No timing data found for {current_key} in '{timing_log_file_path}'. Skipping temperature analysis for this point.")
            stats = {"pkg_min": "N/A", "pkg_mean": "N/A", "pkg_max": "N/A", "cores_mean": "N/A", "temp_sample_count": 0}
        else:
            phase_times = timing_events[current_key]
            start_dt = phase_times.get("WORK_PHASE_START")
            end_dt = phase_times.get("WORK_PHASE_END")

            if not start_dt or not end_dt:
                print(f"  Warning: Missing WORK_PHASE_START or WORK_PHASE_END for {current_key} in timing log. Skipping temperature analysis.")
                stats = {"pkg_min": "N/A", "pkg_mean": "N/A", "pkg_max": "N/A", "cores_mean": "N/A", "temp_sample_count": 0}
            elif end_dt < start_dt:
                print(f"  Warning: WORK_PHASE_END is before WORK_PHASE_START for {current_key} in timing log. Skipping temperature analysis.")
                stats = {"pkg_min": "N/A", "pkg_mean": "N/A", "pkg_max": "N/A", "cores_mean": "N/A", "temp_sample_count": 0}
            else:
                print(f"  Timing Log: WORK_PHASE_START={start_dt.isoformat()}, WORK_PHASE_END={end_dt.isoformat()}")
                stats = get_temperature_stats(all_temp_data, start_dt, end_dt)
        
        combined_result = {**data_point, **stats}
        results_with_temps.append(combined_result)

    print("\n--- Combined Results with Temperature Statistics (during work phases defined by timing log) ---")
    header = ["Defect Type", "Count", "MeanExec(ms)", "CV", 
              "Samples", "PkgMin(C)", "PkgMean(C)", "PkgMax(C)",
              "CoreMean(C)"]
    print("{:<15} {:<5} {:<12} {:<10} {:<7} {:<10} {:<10} {:<10} {:<10}".format(*header))
    print("-"*100)

    for res in results_with_temps:
        pkg_mean_str = f"{res['pkg_mean']:.1f}" if isinstance(res['pkg_mean'], float) else res['pkg_mean']
        core_mean_str = f"{res['cores_mean']:.1f}" if isinstance(res['cores_mean'], float) else res['cores_mean']
        pkg_min_str = f"{res['pkg_min']:.1f}" if isinstance(res['pkg_min'], float) else res['pkg_min']
        pkg_max_str = f"{res['pkg_max']:.1f}" if isinstance(res['pkg_max'], float) else res['pkg_max']

        print("{:<15} {:<5} {:<12.3f} {:<10.6f} {:<7} {:<10} {:<10} {:<10} {:<10}".format(
            res["defect_type"], res["count"], res["mean_ms"], res["cv"],
            res["temp_sample_count"],
            pkg_min_str, pkg_mean_str, pkg_max_str,
            core_mean_str
        ))

    print("\nAnalysis complete.")
    print("Consider using a library like matplotlib or pandas for more advanced plotting and analysis if needed.")

if __name__ == "__main__":
    main() 