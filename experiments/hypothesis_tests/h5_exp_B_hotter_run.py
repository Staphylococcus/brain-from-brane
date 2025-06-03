#!/usr/bin/env python3
"""
H5 Experiment B: Hotter Run Re-confirmation
Based on h5_followup_low_count_lines_test.py
This script attempts to reproduce conditions of a sustained, higher-load run
(more iterations/instances) to observe system behavior and CV without cool-downs.
Temperature logging is active.
"""

import time
import statistics
import random
import copy
import subprocess
import os
from datetime import datetime # Added for precise timing

# --- Make @profile a no-op if line_profiler is not being used ---
try:
    profile
except NameError:
    def profile(func):
        return func
# ------

# --- Configuration for Experiment B (Hotter Run) ---
GRID_SIZE = 50
BASE_CELL_WORK_UNITS = 1
DEFECT_CELL_WORK_UNITS = 101
BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000

NUM_ITERATIONS_PER_CONFIG = 25 # Higher, like followup
NUM_INSTANCES_PER_COUNT = 10   # Higher, like followup

# Consistent with Experiment A for comparability
LINE_DEFECT_COUNTS = [0, 1, 2, 3, 4, 5, 10]

# --- Paths for temperature logging ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_LOGGER_SCRIPT = os.path.join(SCRIPT_DIR, "utils", "log_cpu_temps.py")
TEMP_LOGGER_STOP_FLAG = os.path.join(SCRIPT_DIR, "stop_temp_logging.flag")
DEFAULT_TEMP_LOG_BY_LOGGER = os.path.join(SCRIPT_DIR, "temperature_log.csv")
TEMP_LOG_OUTPUT = os.path.join(SCRIPT_DIR, "temperature_log_h5_exp_B_hot.csv")
# New timing log file for work phase markers
TIMING_LOG_FILE = os.path.join(SCRIPT_DIR, "timing_log_exp_B.csv")
# New experiment results output file
EXPERIMENT_RESULTS_FILE = os.path.join(SCRIPT_DIR, "experiment_results_exp_B.csv")

# --- Crystal and Defect Implementation (Copied from H5/followup, unchanged) ---
class CrystalGrid:
    def __init__(self, size, base_work_units):
        self.size = size
        self.base_work_units = base_work_units
        self.grid = [[base_work_units for _ in range(size)] for _ in range(size)]
        self.total_cells = size * size

    def get_work_units(self, r, c):
        return self.grid[r][c]

    def introduce_point_defects_by_count(self, num_defects, defect_work_units):
        # Not used in this script, but kept for CrystalGrid consistency
        if num_defects == 0: return
        defected_cells = set()
        for _ in range(num_defects):
            attempts = 0; max_placement_attempts = self.total_cells
            while attempts < max_placement_attempts:
                r, c = random.randrange(self.size), random.randrange(self.size)
                if (r,c) not in defected_cells:
                    self.grid[r][c] = defect_work_units
                    defected_cells.add((r,c)); break
                attempts += 1
            if attempts == max_placement_attempts and len(defected_cells) < num_defects and _ < num_defects -1:
                print(f"    DEBUG: Warning: Could only place {len(defected_cells)} point defects out of {num_defects}.")
                break

    def introduce_line_defects_by_count(self, num_lines, defect_work_units):
        if num_lines == 0: return
        defected_rows = set(); defected_cols = set()
        for i in range(num_lines):
            is_row_defect = random.choice([True, False]); attempts = 0; placed_this_line = False
            max_placement_attempts = 2 * self.size
            while attempts < max_placement_attempts:
                if is_row_defect:
                    r = random.randrange(self.size)
                    if r not in defected_rows or len(defected_rows) + len(defected_cols) >= (self.size * 2):
                        for c_idx in range(self.size): self.grid[r][c_idx] = defect_work_units
                        defected_rows.add(r); placed_this_line = True; break
                else: # Column defect
                    c = random.randrange(self.size)
                    if c not in defected_cols or len(defected_rows) + len(defected_cols) >= (self.size * 2):
                        for r_idx in range(self.size): self.grid[r_idx][c] = defect_work_units
                        defected_cols.add(c); placed_this_line = True; break
                if (is_row_defect and len(defected_rows) == self.size and len(defected_cols) < self.size):
                    is_row_defect = not is_row_defect
                elif (not is_row_defect and len(defected_cols) == self.size and len(defected_rows) < self.size):
                    is_row_defect = not is_row_defect
                attempts +=1
            if not placed_this_line and i < num_lines -1: break
    
    def reset(self):
        self.grid = [[self.base_work_units for _ in range(self.size)] for _ in range(self.size)]

# --- Algorithm to Test (Copied from H5/followup, unchanged) ---
@profile 
def busy_work(iterations):
    s = 0
    for i in range(iterations):
        s = (s + i) * (i % 3 + 1); s = s % 1000000 
    return s

@profile
def process_crystal(crystal, busy_work_iter_per_unit):
    volatile_sum = 0 
    for r in range(crystal.size):
        for c in range(crystal.size):
            work_units_for_cell = crystal.get_work_units(r,c)
            volatile_sum += busy_work(work_units_for_cell * busy_work_iter_per_unit)
    return volatile_sum

# --- Experiment Execution (Modified for this Hotter Run) ---
def run_single_config_test(crystal, defect_type, defect_count, defect_work_units, 
                           algorithm, busy_work_iter_per_unit, 
                           num_iterations, num_instances):
    actual_timings_ns = []
    for i_instance in range(num_instances):
        crystal.reset()
        if defect_count > 0: 
            if defect_type == "line": # This script only tests line defects
                crystal.introduce_line_defects_by_count(defect_count, defect_work_units)
            else: # Should not happen
                print(f"Warning: Unexpected defect_type '{defect_type}' in Experiment B script.")
                return 0,0
        for i_iter in range(num_iterations):
            start_time = time.perf_counter_ns()
            algorithm(crystal, busy_work_iter_per_unit)
            end_time = time.perf_counter_ns()
            actual_timings_ns.append(end_time - start_time)
    if not actual_timings_ns or len(actual_timings_ns) < 2: return 0, 0
    mean_time_ns = statistics.mean(actual_timings_ns)
    stdev_time_ns = statistics.stdev(actual_timings_ns)
    cv = stdev_time_ns / mean_time_ns if mean_time_ns > 0 else 0
    return mean_time_ns, cv

def run_experiment():
    print("🔬 H5 Experiment B: Hotter Run Re-confirmation")
    print(f"Grid Size: {GRID_SIZE}x{GRID_SIZE}, Base Work Units: {BASE_CELL_WORK_UNITS}")
    print(f"Defect Work Units: {DEFECT_CELL_WORK_UNITS}")
    print(f"Busy Work Iterations per Unit: {BUSY_WORK_ITERATIONS_PER_WORK_UNIT}")
    print(f"Iterations per config: {NUM_ITERATIONS_PER_CONFIG}, Instances per count: {NUM_INSTANCES_PER_COUNT}")
    print("NO COOL-DOWN PERIODS WILL BE ENFORCED FOR THIS RUN.")
    print("-" * 80)
    print("Defect Type,Defect Count,Mean Exec Time (ms),CV")

    logger_process = None
    if os.path.exists(TEMP_LOG_OUTPUT):
        try: os.remove(TEMP_LOG_OUTPUT); print(f"Removed existing specific temp log: {TEMP_LOG_OUTPUT}")
        except OSError as e: print(f"Warning: Could not remove old specific temp log {TEMP_LOG_OUTPUT}: {e}")
    if os.path.exists(DEFAULT_TEMP_LOG_BY_LOGGER):
        try: os.remove(DEFAULT_TEMP_LOG_BY_LOGGER); print(f"Removed existing default temp log: {DEFAULT_TEMP_LOG_BY_LOGGER}")
        except OSError as e: print(f"Warning: Could not remove old default temp log {DEFAULT_TEMP_LOG_BY_LOGGER}: {e}")
    if os.path.exists(TEMP_LOGGER_STOP_FLAG):
         try: os.remove(TEMP_LOGGER_STOP_FLAG); print(f"Removed pre-existing stop flag: {TEMP_LOGGER_STOP_FLAG}")
         except OSError as e: print(f"Warning: Could not remove old stop flag {TEMP_LOGGER_STOP_FLAG}: {e}")

    # Initialize the new timing log file
    try:
        with open(TIMING_LOG_FILE, 'w', newline='') as f_timing:
            f_timing.write("Timestamp,DefectType,DefectCount,PhaseEvent\n")
        print(f"Initialized timing log: {TIMING_LOG_FILE}")
    except IOError as e:
        print(f"ERROR: Could not initialize timing log file {TIMING_LOG_FILE}: {e}")
        # return # Decide if critical

    # Initialize the new experiment results file
    if os.path.exists(EXPERIMENT_RESULTS_FILE):
        try: os.remove(EXPERIMENT_RESULTS_FILE); print(f"Removed existing experiment results file: {EXPERIMENT_RESULTS_FILE}")
        except OSError as e: print(f"Warning: Could not remove old experiment results file {EXPERIMENT_RESULTS_FILE}: {e}")
    try:
        with open(EXPERIMENT_RESULTS_FILE, 'w', newline='') as f_results:
            f_results.write("DefectType,DefectCount,MeanExecTimeMS,CV\n")
        print(f"Initialized experiment results file: {EXPERIMENT_RESULTS_FILE}")
    except IOError as e:
        print(f"ERROR: Could not initialize experiment results file {EXPERIMENT_RESULTS_FILE}: {e}")
        # return # Decide if critical

    if not os.path.exists(TEMP_LOGGER_SCRIPT):
        print(f"ERROR: Temperature logger script not found at {TEMP_LOGGER_SCRIPT}. Logging skipped.")
    else:
        print(f"Starting temperature logger: {TEMP_LOGGER_SCRIPT}")
        python_executable = "python3"
        project_root = os.path.join(SCRIPT_DIR, "..", "..")
        venv_python = os.path.join(project_root, ".venv", "bin", "python3")
        if os.path.exists(venv_python):
            python_executable = venv_python
            print(f"Using venv python: {python_executable}")
        else:
            print(f"Using system python: {python_executable} (venv not found at {venv_python})")
        try:
            logger_process = subprocess.Popen([python_executable, TEMP_LOGGER_SCRIPT])
            print(f"Temperature logger process started (PID: {logger_process.pid}).")
            print(f"Logger will create {DEFAULT_TEMP_LOG_BY_LOGGER} and look for {TEMP_LOGGER_STOP_FLAG}")
            time.sleep(3)
        except Exception as e:
            print(f"Failed to start temperature logger: {e}"); logger_process = None

    crystal = CrystalGrid(GRID_SIZE, BASE_CELL_WORK_UNITS)
    try:
        print("\nStarting: Line Defects Loop (Experiment B - Hotter Run)")
        for count in LINE_DEFECT_COUNTS:
            # No cool-down logic in this version
            defect_type_str = "Baseline_Line" if count == 0 else "Line"
            print(f"Starting: {defect_type_str}, Defect Count: {count}")
            
            # Log WORK_PHASE_START
            try:
                with open(TIMING_LOG_FILE, 'a', newline='') as f_timing:
                    f_timing.write(f"{datetime.now().isoformat()},{defect_type_str},{count},WORK_PHASE_START\n")
            except IOError as e:
                print(f"Warning: Could not write WORK_PHASE_START to timing log: {e}")

            # All runs, including baseline, use the higher NUM_INSTANCES_PER_COUNT for this script
            mean_ns, cv = run_single_config_test(crystal, "line", count, DEFECT_CELL_WORK_UNITS, 
                                                    process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                    NUM_ITERATIONS_PER_CONFIG, NUM_INSTANCES_PER_COUNT)
            
            # Log WORK_PHASE_END
            try:
                with open(TIMING_LOG_FILE, 'a', newline='') as f_timing:
                    f_timing.write(f"{datetime.now().isoformat()},{defect_type_str},{count},WORK_PHASE_END\n")
            except IOError as e:
                print(f"Warning: Could not write WORK_PHASE_END to timing log: {e}")

            print(f"{defect_type_str},{count},{mean_ns / 1e6:.3f},{cv:.6f}")
            # Append results to the CSV file
            try:
                with open(EXPERIMENT_RESULTS_FILE, 'a', newline='') as f_results:
                    f_results.write(f"{defect_type_str},{count},{mean_ns / 1e6:.3f},{cv:.6f}\n")
            except IOError as e:
                print(f"Warning: Could not write to experiment results file {EXPERIMENT_RESULTS_FILE}: {e}")

            print(f"Finished: {defect_type_str}, Defect Count: {count}")
        print("\nFinished: Line Defects Loop")

    except Exception as e:
        print(f"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR: An exception occurred during run_experiment:")
        import traceback; traceback.print_exc()
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    finally:
        if logger_process:
            print("Signaling temperature logger to stop...")
            try:
                with open(TEMP_LOGGER_STOP_FLAG, 'w') as f_stop: f_stop.write('stop')
                print(f"Stop flag created at {TEMP_LOGGER_STOP_FLAG}")
            except IOError as e_flag: print(f"Error creating stop flag {TEMP_LOGGER_STOP_FLAG}: {e_flag}")
            print("Waiting for temperature logger to terminate...")
            try:
                logger_process.wait(timeout=10)
                if logger_process.poll() is None:
                    print("Temperature logger did not terminate in time, attempting to kill.")
                    logger_process.kill(); logger_process.wait(timeout=5)
                print("Temperature logger process finished.")
            except subprocess.TimeoutExpired: print("Timeout waiting for logger. It might still be running.")
            except Exception as e_proc: print(f"Error managing logger process shutdown: {e_proc}")
            
            if os.path.exists(DEFAULT_TEMP_LOG_BY_LOGGER):
                try:
                    os.rename(DEFAULT_TEMP_LOG_BY_LOGGER, TEMP_LOG_OUTPUT)
                    print(f"Temperature log saved to: {TEMP_LOG_OUTPUT}")
                except OSError as e_rename: print(f"Error renaming {DEFAULT_TEMP_LOG_BY_LOGGER} to {TEMP_LOG_OUTPUT}: {e_rename}")
            else: print(f"Warning: Expected default temp log {DEFAULT_TEMP_LOG_BY_LOGGER} not found for renaming.")
        if os.path.exists(TEMP_LOGGER_STOP_FLAG):
            try: os.remove(TEMP_LOGGER_STOP_FLAG); print(f"Cleaned up stop flag: {TEMP_LOGGER_STOP_FLAG}")
            except OSError as e_clean: print(f"Warning: Could not clean up stop flag {TEMP_LOGGER_STOP_FLAG}: {e_clean}")

    print("-" * 80)
    print("H5 Experiment B (Hotter Run Re-confirmation) finished.")

if __name__ == "__main__":
    run_experiment() 