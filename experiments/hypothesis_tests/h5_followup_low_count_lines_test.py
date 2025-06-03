#!/usr/bin/env python3
"""
H5 Follow-up: INVESTIGATE LOW CV FOR 2 LINE DEFECTS
This experiment is a follow-up to H5 to specifically investigate the low CV observed
for 2 line defects with higher statistical confidence.
It focuses only on line defects with counts 0, 1, 2, 3, and 4,
using increased iterations and instances per configuration.

MODIFIED FOR TEMPERATURE LOGGING: This version will only run the baseline (0 defects)
configuration and log CPU temperatures during that run.

MODIFIED FOR FULL RUN: This version will run line defect counts [0, 1, 2, 3, 4, 5]
with higher iterations and instances. Temperature logging is disabled.
"""

import time
import statistics
import random
import copy
import subprocess
import os

# --- Make @profile a no-op if line_profiler is not being used ---
try:
    # This will be defined if the script is run with kernprof -l -v script.py
    profile
except NameError:
    def profile(func):
        return func # Return the original function unchanged
# ------

# --- Configuration ---
GRID_SIZE = 50  # Grid will be GRID_SIZE x GRID_SIZE
BASE_CELL_WORK_UNITS = 1 # Multiplier for busy work in a normal cell
DEFECT_CELL_WORK_UNITS = 101 # Multiplier for busy work in a defective cell (BASE + INCREASE)
BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000

NUM_ITERATIONS_PER_CONFIG = 25 
NUM_INSTANCES_PER_COUNT = 10   

# LINE_DEFECT_COUNTS = [0] # MODIFIED: Only baseline for this temp logging run
LINE_DEFECT_COUNTS = [0, 1, 2, 3, 4, 5] # Run full set of low line defect counts

# --- Paths for temperature logging ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_LOGGER_SCRIPT = os.path.join(SCRIPT_DIR, "utils", "log_cpu_temps.py")
TEMP_LOGGER_STOP_FLAG = os.path.join(SCRIPT_DIR, "stop_temp_logging.flag")
TEMP_LOG_OUTPUT = os.path.join(SCRIPT_DIR, "temperature_log_h5_followup_baseline.csv") # Specific name

# --- Crystal and Defect Implementation (Copied from H5, unchanged) ---
class CrystalGrid:
    def __init__(self, size, base_work_units):
        self.size = size
        self.base_work_units = base_work_units
        self.grid = [[base_work_units for _ in range(size)] for _ in range(size)]
        self.total_cells = size * size

    def get_work_units(self, r, c):
        return self.grid[r][c]

    def introduce_point_defects_by_count(self, num_defects, defect_work_units):
        """Introduces a specific count of random point defects."""
        # This method is kept for compatibility if CrystalGrid is shared, but not used by this script
        if num_defects == 0:
            return
        
        defected_cells = set()
        for _ in range(num_defects):
            attempts = 0
            max_placement_attempts = self.total_cells 
            while attempts < max_placement_attempts:
                r, c = random.randrange(self.size), random.randrange(self.size)
                if (r,c) not in defected_cells:
                    self.grid[r][c] = defect_work_units
                    defected_cells.add((r,c))
                    break
                attempts += 1
            if attempts == max_placement_attempts and len(defected_cells) < num_defects and _ < num_defects -1:
                print(f"    DEBUG: Warning: Could only place {len(defected_cells)} unique point defects out of {num_defects} requested.")
                break

    def introduce_line_defects_by_count(self, num_lines, defect_work_units):
        """Introduces a specific count of random line (row or column) defects."""
        if num_lines == 0:
            return

        defected_rows = set()
        defected_cols = set()

        for i in range(num_lines):
            is_row_defect = random.choice([True, False])
            attempts = 0
            placed_this_line = False
            max_placement_attempts = 2 * self.size 
            while attempts < max_placement_attempts:
                if is_row_defect:
                    r = random.randrange(self.size)
                    if r not in defected_rows or len(defected_rows) + len(defected_cols) >= (2*self.size):
                        for c_idx in range(self.size):
                            self.grid[r][c_idx] = defect_work_units
                        defected_rows.add(r)
                        placed_this_line = True
                        break
                else: # Column defect
                    c = random.randrange(self.size)
                    if c not in defected_cols or len(defected_rows) + len(defected_cols) >= (2*self.size):
                        for r_idx in range(self.size):
                            self.grid[r_idx][c] = defect_work_units
                        defected_cols.add(c)
                        placed_this_line = True
                        break
                
                if (is_row_defect and len(defected_rows) == self.size and len(defected_cols) < self.size) or \
                   (not is_row_defect and len(defected_cols) == self.size and len(defected_rows) < self.size):
                    is_row_defect = not is_row_defect
                
                attempts +=1
            
            if not placed_this_line and i < num_lines -1 :
                break 
    
    def reset(self):
        self.grid = [[self.base_work_units for _ in range(self.size)] for _ in range(self.size)]

# --- Algorithm to Test (Copied from H5, unchanged) ---
@profile 
def busy_work(iterations):
    """A simple CPU-bound task."""
    s = 0
    for i in range(iterations):
        s = (s + i) * (i % 3 + 1) 
        s = s % 1000000 
    return s

@profile
def process_crystal(crystal, busy_work_iter_per_unit):
    """Processes the crystal by performing busy work proportional to cell work units."""
    volatile_sum = 0 
    for r in range(crystal.size):
        for c in range(crystal.size):
            work_units_for_cell = crystal.get_work_units(r,c)
            volatile_sum += busy_work(work_units_for_cell * busy_work_iter_per_unit)
    return volatile_sum

# --- Experiment Execution (Modified for this follow-up) ---
def run_single_config_test(crystal, defect_type, defect_count, defect_work_units, 
                           algorithm, busy_work_iter_per_unit, 
                           num_iterations, num_instances):
    """Runs tests for a single defect type and count, measuring actual execution time."""
    actual_timings_ns = []

    if defect_count < 0:
        return 0,0 

    for i_instance in range(num_instances):
        crystal.reset()
        if defect_count > 0: 
            # This script only tests line defects
            if defect_type == "line":
                crystal.introduce_line_defects_by_count(defect_count, defect_work_units)
            else:
                # Should not happen in this script
                print(f"Warning: Unexpected defect_type '{defect_type}' in h5_followup script.")
                return 0,0 

        for i_iter in range(num_iterations):
            start_time = time.perf_counter_ns()
            algorithm(crystal, busy_work_iter_per_unit)
            end_time = time.perf_counter_ns()
            actual_timings_ns.append(end_time - start_time)
            
    if not actual_timings_ns or len(actual_timings_ns) < 2:
        return 0, 0 
    
    mean_time_ns = statistics.mean(actual_timings_ns)
    stdev_time_ns = statistics.stdev(actual_timings_ns)
    cv = stdev_time_ns / mean_time_ns if mean_time_ns > 0 else 0
    return mean_time_ns, cv

def run_experiment():
    """Runs the focused follow-up experiment."""
    print("🔬 H5 FOLLOW-UP (LOW COUNT LINE DEFECTS - FULL RUN)")
    print(f"Grid Size: {GRID_SIZE}x{GRID_SIZE}, Base Work Units: {BASE_CELL_WORK_UNITS}")
    print(f"Defect Work Units: {DEFECT_CELL_WORK_UNITS}")
    print(f"Busy Work Iterations per Unit: {BUSY_WORK_ITERATIONS_PER_WORK_UNIT}")
    print(f"Iterations per config: {NUM_ITERATIONS_PER_CONFIG}, Instances per count: {NUM_INSTANCES_PER_COUNT}")
    print("-" * 80)
    print("Defect Type,Defect Count,Mean Exec Time (ms),CV")

    # --- Start Temperature Logger ---
    logger_process = None
    # default_temp_log_path = os.path.join(SCRIPT_DIR, "temperature_log.csv")
    # if os.path.exists(default_temp_log_path):
    #     try:
    #         os.remove(default_temp_log_path)
    #         print(f"Removed existing default temp log: {default_temp_log_path}")
    #     except OSError as e:
    #         print(f"Error removing existing temp log {default_temp_log_path}: {e}") 
    # 
    # if os.path.exists(TEMP_LOGGER_STOP_FLAG):
    #      os.remove(TEMP_LOGGER_STOP_FLAG)
    # 
    # if not os.path.exists(TEMP_LOGGER_SCRIPT):
    #     print(f"ERROR: Temperature logger script not found at {TEMP_LOGGER_SCRIPT}")
    #     print("Skipping temperature logging.")
    # else:
    #     print(f"Starting temperature logger: {TEMP_LOGGER_SCRIPT}")
    #     python_executable = "python3"
    #     venv_python = os.path.join(SCRIPT_DIR, "..", ".venv", "bin", "python3") 
    #     if os.path.exists(venv_python):
    #         python_executable = venv_python
    #         print(f"Using venv python: {python_executable}")
    #     else:
    #         print(f"Using system python: {python_executable}")
    #     
    #     try:
    #         logger_process = subprocess.Popen([python_executable, TEMP_LOGGER_SCRIPT])
    #         print(f"Temperature logger process started (PID: {logger_process.pid}).")
    #         time.sleep(2) 
    #     except Exception as e:
    #         print(f"Failed to start temperature logger: {e}")
    #         logger_process = None
    # -------------------------------- (Temperature Logging Disabled)

    crystal = CrystalGrid(GRID_SIZE, BASE_CELL_WORK_UNITS)

    try:
        print("\nStarting: Focused Line Defects Loop (Full Run)")
        for count in LINE_DEFECT_COUNTS: 
            if count == 0:
                print(f"Starting: Line Defects, Count: {count} (Baseline)")
                current_instances = NUM_INSTANCES_PER_COUNT # Use full instances for baseline too
                
                mean_ns, cv = run_single_config_test(crystal, "line", count, DEFECT_CELL_WORK_UNITS, 
                                                        process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                        NUM_ITERATIONS_PER_CONFIG, current_instances)
                defect_type_str = "Baseline" # Keep "Baseline" for count 0 for clarity
                print(f"{defect_type_str},{count},{mean_ns / 1e6:.3f},{cv:.6f}")
                print(f"Finished: Line Defects, Count: {count}")
            else:
                print(f"Starting: Line Defects, Count: {count}")
                current_instances = NUM_INSTANCES_PER_COUNT
                
                mean_ns, cv = run_single_config_test(crystal, "line", count, DEFECT_CELL_WORK_UNITS, 
                                                        process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                        NUM_ITERATIONS_PER_CONFIG, current_instances)
                defect_type_str = "Line"
                print(f"{defect_type_str},{count},{mean_ns / 1e6:.3f},{cv:.6f}")
                print(f"Finished: Line Defects, Count: {count}")
        print("Finished: Focused Line Defects Loop (Full Run)")

    except Exception as e:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR: An exception occurred during run_experiment:")
        import traceback
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    finally:
        # --- Stop Temperature Logger ---
        if logger_process:
            print("Signaling temperature logger to stop...")
            # with open(TEMP_LOGGER_STOP_FLAG, 'w') as f_stop:
            #     f_stop.write('stop')
            # 
            # print("Waiting for temperature logger to terminate...")
            # try:
            #     logger_process.wait(timeout=10) 
            #     if logger_process.poll() is None:
            #         print("Temperature logger did not terminate in time, attempting to kill.")
            #         logger_process.kill()
            #         logger_process.wait(timeout=5)
            #     print("Temperature logger process finished.")
            # except subprocess.TimeoutExpired:
            #     print("Timeout waiting for logger to stop. It might still be running.")
            # except Exception as e:
            #     print(f"Error managing logger process: {e}")
            # 
            # if os.path.exists(default_temp_log_path):
            #     try:
            #         os.rename(default_temp_log_path, TEMP_LOG_OUTPUT)
            #         print(f"Temperature log saved to: {TEMP_LOG_OUTPUT}")
            #     except OSError as e:
            #         print(f"Error renaming temp log {default_temp_log_path} to {TEMP_LOG_OUTPUT}: {e}")
            # else:
            #     print(f"Warning: Expected temperature log {default_temp_log_path} not found for renaming.")
        
        # if os.path.exists(TEMP_LOGGER_STOP_FLAG):
        #      os.remove(TEMP_LOGGER_STOP_FLAG)
        # -------------------------------- (Temperature Logging Disabled)

    print("-" * 80)
    print("H5 Follow-up (Low Count Line Defects - Full Run) finished.")

if __name__ == "__main__":
    run_experiment() 