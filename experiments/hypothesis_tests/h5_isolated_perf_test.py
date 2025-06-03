#!/usr/bin/env python3
"""
H5 ISOLATED PERF TEST
This experiment tests H5 (Critical Destabilization by Low-Count Correlated Geometric Defects)
using a helper script to run iterations on an isolated CPU core with perf stat logging.

It focuses on line defects with counts 0, 1, 2, 3, 4, 5,
using parameters from the h5_followup_low_count_lines_test.py script.
Results are logged to a JSONL file.
"""

import time
import statistics
import random # No longer needed directly if defect generation is handled by helper or simple logic here
import copy # No longer needed
import subprocess
import os
import tempfile
import csv
import json # For JSONL output and parsing helper script stdout
import sys # For sys.executable
import pathlib # For easier path handling
import datetime # For timestamp in metadata

# --- Make @profile a no-op if line_profiler is not being used ---
# (Keeping this as it's harmless, though local functions it decorated are removed)
try:
    profile
except NameError:
    def profile(func):
        return func
# ------

# --- Configuration (from h5_followup_low_count_lines_test.py) ---
GRID_SIZE = 50
BASE_CELL_WORK_UNITS = 1
DEFECT_CELL_WORK_UNITS = 101
BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000

NUM_ITERATIONS_PER_CONFIG = 25 # This is num_timing_iterations for the helper script (per instance)
NUM_INSTANCES_PER_COUNT = 10   

LINE_DEFECT_COUNTS_TO_TEST = [0, 1, 2, 3, 4, 5] # Defect counts for 'Line' type
# This script will focus on Line defects vs Baseline, as per original H5 followup.

# --- Scripting & Perf Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
HELPER_SCRIPT_PATH = str(SCRIPT_DIR / "_run_perf_target_iterations.py")
JSONL_OUTPUT_FILE = str(SCRIPT_DIR / "h5_isolated_perf_results.jsonl")
CPU_TO_PIN = 10 # The CPU core to pin perf and the python helper script to

PERF_EVENTS = [
    "cycles",
    "instructions",
    "cache-references",
    "cache-misses",
    "branch-instructions",
    "branch-misses",
    "mem_load_retired.l1_miss", 
    # "L1-icache-load-misses", # Known Omission
    "LLC-loads",
    "LLC-load-misses",
    "dTLB-load-misses", # Was <not counted> in short test, but is a valid event
    "iTLB-load-misses", # Was <not counted> in short test, but is a valid event
    # "stalled-cycles-frontend", # Removed - <not supported>
    # "stalled-cycles-backend",  # Removed - <not supported>
    "cpu-clock", 
    "task-clock",
]

# --- REMOVED LOCAL CrystalGrid, busy_work, process_crystal ---
# --- REMOVED TEMPERATURE LOGGING CODE ---

def parse_perf_output(perf_output_str: str) -> dict:
    """Parses the CSV output from 'perf stat -x,'."""
    perf_data = {}
    reader = csv.reader(perf_output_str.strip().splitlines(), delimiter=',')
    for row in reader:
        # Ensure row has enough columns: value, unit (can be empty), event_name
        if len(row) >= 3: 
            value_str = row[0].strip()
            # row[1] is the unit, which we currently ignore for raw counts.
            event_name = row[2].strip() # Corrected: event name is in the 3rd column (index 2)
            
            # Skip if event_name is empty, which can happen for some perf stat header/footer lines or malformed entries
            if not event_name:
                continue
            
            try:
                perf_data[event_name] = int(value_str)
            except ValueError:
                perf_data[event_name] = value_str
        # Silently ignore malformed rows that don't meet len(row) >= 3
    return perf_data

def run_instance_with_perf(defect_type_str: str, defect_count: int, instance_num: int) -> dict:
    """Runs a single instance using the helper script with perf stat and returns all results."""
    
    cmd = [
        "taskset", "-c", str(CPU_TO_PIN),
        "perf", "stat", "-x,", "-e", ",".join(PERF_EVENTS),
        # Perf output goes to a temporary file, specified by -o
        # Helper script stdout will be captured for its JSON timing data
        sys.executable, # Path to current python interpreter
        HELPER_SCRIPT_PATH,
        "--grid_size", str(GRID_SIZE),
        "--base_cell_work_units", str(BASE_CELL_WORK_UNITS),
        "--defect_type", defect_type_str,
        "--defect_count", str(defect_count),
        "--defect_cell_work_units", str(DEFECT_CELL_WORK_UNITS),
        "--busy_work_iterations_per_work_unit", str(BUSY_WORK_ITERATIONS_PER_WORK_UNIT),
        "--num_timing_iterations", str(NUM_ITERATIONS_PER_CONFIG) 
    ]

    perf_output_data = ""
    iteration_times_ns = []
    perf_counters = {}
    error_message = None

    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as temp_perf_file:
            perf_output_filename = temp_perf_file.name
        
        # Add perf output file to command AFTER creating it
        cmd.insert(cmd.index("-e") + 2, "-o")
        cmd.insert(cmd.index("-o") + 1, perf_output_filename)

        # print(f"  Executing: {' '.join(cmd)}") # For debugging command construction
        result = subprocess.run(cmd, capture_output=True, text=True, check=False) # check=False to handle errors manually

        if result.returncode != 0:
            error_message = f"Command failed with return code {result.returncode}. Stderr: {result.stderr.strip()}"
            # print(f"    ERROR: {error_message}", file=sys.stderr) # Log error
            # Fall through to return what we have, error_message will be in the dict
        else:
            try:
                iteration_times_ns = json.loads(result.stdout.strip())
            except json.JSONDecodeError as e:
                error_message = f"Failed to parse JSON from helper script stdout: {e}. Stdout: {result.stdout.strip()}"
                # print(f"    ERROR: {error_message}", file=sys.stderr)
        
        # Read perf data regardless of main command success, as perf might still write something
        try:
            with open(perf_output_filename, 'r') as f:
                perf_output_data = f.read()
            if perf_output_data:
                perf_counters = parse_perf_output(perf_output_data)
            elif not error_message: # If there was no other error, but perf file is empty
                error_message = "Perf output file was empty."
                # print(f"    WARNING: {error_message}", file=sys.stderr)

        except FileNotFoundError:
            if not error_message:
                 error_message = f"Perf output file not found: {perf_output_filename}"
            # print(f"    ERROR: {error_message}", file=sys.stderr)
        except Exception as e:
            if not error_message:
                error_message = f"Error reading/parsing perf output file: {e}"
            # print(f"    ERROR: {error_message}", file=sys.stderr)

    except subprocess.CalledProcessError as e:
        error_message = f"Subprocess execution failed: {e}. Stderr: {e.stderr.strip() if e.stderr else 'N/A'}"
        # print(f"    ERROR: {error_message}", file=sys.stderr)
    except FileNotFoundError as e: # For taskset or perf itself not found
        error_message = f"Execution failed, command not found (taskset, perf, or python likely): {e}"
        # print(f"    ERROR: {error_message}", file=sys.stderr)
    except Exception as e:
        error_message = f"An unexpected error occurred in run_instance_with_perf: {e}"
        # print(f"    ERROR: {error_message}", file=sys.stderr)
    finally:
        if 'perf_output_filename' in locals() and os.path.exists(perf_output_filename):
            os.remove(perf_output_filename) # Clean up temp file

    # Calculate CV and mean if timings were successfully retrieved
    mean_ns = 0
    cv = 0
    if iteration_times_ns and len(iteration_times_ns) >= 2:
        mean_ns = statistics.mean(iteration_times_ns)
        stdev_ns = statistics.stdev(iteration_times_ns)
        cv = stdev_ns / mean_ns if mean_ns > 0 else 0
    elif iteration_times_ns and len(iteration_times_ns) == 1:
        mean_ns = iteration_times_ns[0]
        cv = 0 # Cannot calculate stdev with one sample

    return {
        "defect_type": defect_type_str,
        "defect_count": defect_count,
        "instance_num": instance_num,
        "iteration_times_ns": iteration_times_ns,
        "mean_time_ns": mean_ns,
        "cv": cv,
        "perf_counters": perf_counters,
        "error": error_message # Will be None if no errors
    }

# --- Experiment Execution (Refactored) ---

# The old run_single_config_test is no longer used and will be removed.
# def run_single_config_test(crystal, defect_type, defect_count, defect_work_units, 
#                            algorithm, busy_work_iter_per_unit, 
#                            num_iterations, num_instances):
#     """Runs tests for a single defect type and count, measuring actual execution time."""
#     actual_timings_ns = []
# 
#     if defect_count < 0:
#         return 0,0 
# 
#     for i_instance in range(num_instances):
#         crystal.reset()
#         if defect_count > 0: 
#             if defect_type == "line":
#                 crystal.introduce_line_defects_by_count(defect_count, defect_work_units)
#             else:
#                 print(f"Warning: Unexpected defect_type '{defect_type}' in h5_followup script.")
#                 return 0,0 
# 
#         for i_iter in range(num_iterations):
#             start_time = time.perf_counter_ns()
#             algorithm(crystal, busy_work_iter_per_unit)
#             end_time = time.perf_counter_ns()
#             actual_timings_ns.append(end_time - start_time)
#             
#     if not actual_timings_ns or len(actual_timings_ns) < 2:
#         return 0, 0 
#     
#     mean_time_ns = statistics.mean(actual_timings_ns)
#     stdev_time_ns = statistics.stdev(actual_timings_ns)
#     cv = stdev_time_ns / mean_time_ns if mean_time_ns > 0 else 0
#     return mean_time_ns, cv

def run_experiment():
    """Runs the focused follow-up experiment."""
    print("🔬 H5 ISOLATED PERF TEST")
    print(f"Grid Size: {GRID_SIZE}x{GRID_SIZE}, Base Work Units: {BASE_CELL_WORK_UNITS}")
    print(f"Defect Work Units: {DEFECT_CELL_WORK_UNITS}")
    print(f"Busy Work Iterations per Unit: {BUSY_WORK_ITERATIONS_PER_WORK_UNIT}")
    print(f"Iterations per instance (helper): {NUM_ITERATIONS_PER_CONFIG}, Instances per count (main): {NUM_INSTANCES_PER_COUNT}")
    print(f"Pinning to CPU: {CPU_TO_PIN}")
    print(f"Outputting to: {JSONL_OUTPUT_FILE}")
    print("-" * 80)

    # crystal = CrystalGrid(GRID_SIZE, BASE_CELL_WORK_UNITS) # CrystalGrid is now in helper

    try:
        # Write a header/metadata object as the first line of the JSONL file
        # This helps in identifying the experiment parameters later.
        with open(JSONL_OUTPUT_FILE, 'w') as outfile: # 'w' to overwrite if exists
            experiment_metadata = {
                "type": "experiment_metadata",
                "experiment_name": "H5 Isolated Perf Test",
                "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
                "grid_size": GRID_SIZE,
                "base_cell_work_units": BASE_CELL_WORK_UNITS,
                "defect_cell_work_units": DEFECT_CELL_WORK_UNITS,
                "busy_work_iterations_per_work_unit": BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                "num_iterations_per_config_in_helper": NUM_ITERATIONS_PER_CONFIG,
                "num_instances_per_count_in_main": NUM_INSTANCES_PER_COUNT,
                "cpu_pinned_to": CPU_TO_PIN,
                "perf_events_monitored": PERF_EVENTS,
                "helper_script_path": HELPER_SCRIPT_PATH
            }
            outfile.write(json.dumps(experiment_metadata) + '\n')

        print("\nStarting: Focused Line Defects Loop (with perf)")
        
        # This script focuses on Line defects (and Baseline, which is Line defect_count 0)
        # The original script's LINE_DEFECT_COUNTS_TO_TEST = [0, 1, 2, 3, 4, 5]
        for defect_count in LINE_DEFECT_COUNTS_TO_TEST: 
            current_defect_type_for_helper = "Baseline" if defect_count == 0 else "Line"
            
            print(f"Processing Config: Type: {current_defect_type_for_helper}, Defect Count: {defect_count}")
            
            for i_instance in range(NUM_INSTANCES_PER_COUNT):
                print(f"  Instance {i_instance + 1}/{NUM_INSTANCES_PER_COUNT}", end='\r')
                
                instance_data = run_instance_with_perf(
                    defect_type_str=current_defect_type_for_helper, 
                    defect_count=defect_count, 
                    instance_num=i_instance + 1
                )
                
                with open(JSONL_OUTPUT_FILE, 'a') as outfile:
                    outfile.write(json.dumps(instance_data) + '\n')
                
                if instance_data.get("error"):
                    print(f"\n    ERROR encountered for instance {i_instance + 1}: {instance_data['error']}", file=sys.stderr)
            
            print(f"  Finished all instances for Type: {current_defect_type_for_helper}, Count: {defect_count}.      ") # Spaces to clear carriage return

        print("\nFinished: All configurations.")
        print(f"Results saved to {JSONL_OUTPUT_FILE}")

    except Exception as e:
        print(f"An error occurred during the experiment: {e}")
        import traceback
        print(traceback.format_exc())

    finally:
        print("Experiment script finished.")

if __name__ == "__main__":
    run_experiment() 