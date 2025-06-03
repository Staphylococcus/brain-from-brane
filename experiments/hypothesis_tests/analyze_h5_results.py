#!/usr/bin/env python3
"""
Processes the H5 isolated perf test results to calculate averages for key metrics.
"""
import json
from collections import defaultdict
import statistics
import pathlib

def main():
    # Determine the script's directory to locate the data file
    script_dir = pathlib.Path(__file__).parent.resolve()
    file_path = script_dir / "h5_isolated_perf_results.jsonl"
    
    data = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                data.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: Results file not found at {file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. The file might be corrupted.")
        return

    if not data:
        print("Error: No data loaded from the file.")
        return

    # Skip metadata line
    if data and data[0].get("type") == "experiment_metadata":
        results_data = data[1:]
    else:
        results_data = data
        print("Warning: Metadata line not found at the beginning of the results file.")

    if not results_data:
        print("Error: No actual result records found after skipping metadata.")
        return

    # Group data by defect_count
    grouped_data = defaultdict(lambda: {
        "mean_times_ns": [],
        "cvs": [],
        "perf_counters_sum": defaultdict(float),
        "perf_counter_counts": defaultdict(int), # For averaging numeric counters
        "perf_counter_str_occurrences": defaultdict(lambda: defaultdict(int)), # For non-numeric like '<not counted>'
        "valid_instances": 0
    })

    for record in results_data:
        if record.get("error"):
            defect_count_str = str(record.get("defect_count", "N/A"))
            instance_num_str = str(record.get("instance_num", "N/A"))
            # print(f"Skipping record due to error: defect_count {defect_count_str}, instance {instance_num_str}")
            continue 

        defect_count = record["defect_count"]
        grouped_data[defect_count]["mean_times_ns"].append(record["mean_time_ns"])
        grouped_data[defect_count]["cvs"].append(record["cv"])
        
        perf_counters = record.get("perf_counters", {})
        for key, value in perf_counters.items():
            try:
                num_value = float(value)
                grouped_data[defect_count]["perf_counters_sum"][key] += num_value
                grouped_data[defect_count]["perf_counter_counts"][key] += 1
            except ValueError: # Handles strings like '<not counted>'
                grouped_data[defect_count]["perf_counter_str_occurrences"][key][str(value)] += 1
                # We still increment perf_counter_counts for the key to know it was seen,
                # even if only non-numeric values were encountered for it.
                # This helps later to decide if a key had *any* data at all.
                if key not in grouped_data[defect_count]["perf_counter_counts"]:
                     grouped_data[defect_count]["perf_counter_counts"][key] = 0 # Ensure key exists
                grouped_data[defect_count]["perf_counter_counts"][key] +=1


        grouped_data[defect_count]["valid_instances"] += 1

    # Calculate and print averages
    print("--- Aggregated Experiment Results ---")
    for defect_count in sorted(grouped_data.keys()):
        group = grouped_data[defect_count]
        num_valid_instances = group["valid_instances"]

        if num_valid_instances == 0:
            print(f"\nDefect Count: {defect_count} (No valid instances with perf data or all had errors)")
            continue

        avg_mean_time_ns = statistics.mean(group["mean_times_ns"]) if group["mean_times_ns"] else 0
        avg_cv = statistics.mean(group["cvs"]) if group["cvs"] else 0
        
        print(f"\nDefect Count: {defect_count} (Based on {num_valid_instances} valid instances)")
        print(f"  Avg Mean Time (ns): {avg_mean_time_ns:.2f}")
        print(f"  Avg CV:             {avg_cv:.6f}")

        avg_perf_counters = {}
        for key, total_sum in group["perf_counters_sum"].items():
            numeric_count_for_key = sum(1 for v in results_data if not v.get("error") and v["defect_count"] == defect_count and isinstance(v.get("perf_counters", {}).get(key), (int,float)))
            try: #check if value for key in any instance under this defect_count is numeric
                # This check is a bit redundant now due to try-except in loop above, but keeping for safety
                float(next(r["perf_counters"][key] for r in results_data if not r.get("error") and r["defect_count"] == defect_count and key in r["perf_counters"]))
                is_numeric_event = True
            except (StopIteration, ValueError, TypeError):
                is_numeric_event = False


            if key in group["perf_counter_counts"] and group["perf_counter_counts"][key] > 0 and is_numeric_event :
                 # Count only numeric occurrences for averaging numeric sums
                numeric_occurrences = sum(1 for r in results_data if not r.get("error") and r["defect_count"] == defect_count and key in r.get("perf_counters", {}) and isinstance(r["perf_counters"][key], (int, float)))
                if numeric_occurrences > 0:
                    avg_perf_counters[key] = total_sum / numeric_occurrences
                else: # All values were strings for this key for this defect_count
                     avg_perf_counters[key] = dict(group["perf_counter_str_occurrences"].get(key, {})) if key in group["perf_counter_str_occurrences"] else "<no numeric data>"

            # If it's primarily a string-valued counter (e.g. only <not counted>)
            elif key in group["perf_counter_str_occurrences"] and group["perf_counter_str_occurrences"][key]:
                 avg_perf_counters[key] = dict(group["perf_counter_str_occurrences"][key])
            else:
                avg_perf_counters[key] = "N/A (no data)"
        
        instructions_val = avg_perf_counters.get("cpu_core/instructions/")
        cycles_val = avg_perf_counters.get("cpu_core/cycles/")
        
        ipc = "N/A"
        if isinstance(instructions_val, (int, float)) and isinstance(cycles_val, (int, float)) and cycles_val > 0:
            ipc = instructions_val / cycles_val
        elif isinstance(instructions_val, str) or isinstance(cycles_val, str):
            if isinstance(instructions_val, dict) or isinstance(cycles_val, dict):
                 ipc = "N/A (counter was dict of strings)"
            else:
                ipc = "N/A (counter was string)"

        elif cycles_val == 0: #Should not happen with float conversion
            ipc = "N/A (cycles is zero)"
            
        print(f"  Avg IPC:            {ipc:.4f}" if isinstance(ipc, float) else f"  Avg IPC:            {ipc}")
        
        print("  Avg Perf Counters:")
        for key, value in sorted(avg_perf_counters.items()):
            if isinstance(value, float):
                print(f"    {key:<35}: {value:.2f}")
            else: # Handles strings or dicts of non-numeric counts
                print(f"    {key:<35}: {value}")

    print("\n--- End of Results ---")

if __name__ == "__main__":
    main() 