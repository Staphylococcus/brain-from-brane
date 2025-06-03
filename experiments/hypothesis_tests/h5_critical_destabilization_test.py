#!/usr/bin/env python3
"""
H5: CRITICAL DESTABILIZATION BY LOW-COUNT CORRELATED GEOMETRIC DEFECTS
Tests Hypothesis 5: Critical Destabilization by Low-Count Correlated Geometric Defects.
This experiment investigates if the CV of actual execution time shows a localized peak
when a small, critical number of correlated geometric defects (lines) are introduced,
compared to point defects or different counts of line defects.

MODIFIED FOR TEMPERATURE LOGGING: This version will only run the baseline (0 defects)
configuration and log CPU temperatures during that run.
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
BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000 # Keep for H5, adjust if needed based on total runtime

NUM_ITERATIONS_PER_CONFIG = 5 # Original H5 value
NUM_INSTANCES_PER_COUNT = 3   # Original H5 value (1 for baseline as per original script logic)

# Defect counts to test directly
POINT_DEFECT_COUNTS = [0] # MODIFIED: Only baseline for this temp logging run
LINE_DEFECT_COUNTS = []   # MODIFIED: Skip line defects for this temp logging run

# --- Paths for temperature logging ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_LOGGER_SCRIPT = os.path.join(SCRIPT_DIR, "utils", "log_cpu_temps.py")
TEMP_LOGGER_STOP_FLAG = os.path.join(SCRIPT_DIR, "stop_temp_logging.flag")
TEMP_LOG_OUTPUT = os.path.join(SCRIPT_DIR, "temperature_log_h5_original_baseline.csv") # Specific name

# --- Crystal and Defect Implementation ---
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
        if num_defects == 0:
            return
        
        defected_cells = set()
        for _ in range(num_defects):
            attempts = 0
            # Max attempts to find a new cell, can be less than total_cells if many defects requested
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
                break # Stop if we can't find new cells easily for all requested defects

    def introduce_line_defects_by_count(self, num_lines, defect_work_units):
        """Introduces a specific count of random line (row or column) defects."""
        if num_lines == 0:
            return

        # print(f"    DEBUG: Introducing {num_lines} line defects.")
        defected_rows = set()
        defected_cols = set()

        for i in range(num_lines):
            is_row_defect = random.choice([True, False])
            attempts = 0
            placed_this_line = False
            # Max attempts to find a new line can be less than 2*size if many lines requested
            max_placement_attempts = 2 * self.size 
            while attempts < max_placement_attempts:
                if is_row_defect:
                    r = random.randrange(self.size)
                    if r not in defected_rows or len(defected_rows) + len(defected_cols) >= (2*self.size): # Allow re-defecting if all lines are already defected
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
                
                # Try to alternate if first choice was already fully defected and we have other options
                if (is_row_defect and len(defected_rows) == self.size and len(defected_cols) < self.size) or \
                   (not is_row_defect and len(defected_cols) == self.size and len(defected_rows) < self.size):
                    is_row_defect = not is_row_defect
                
                attempts +=1
            
            if not placed_this_line and i < num_lines -1 :
                # This warning might be noisy if num_lines > total available unique lines
                # print(f"    DEBUG: Warning: Could only place {i} unique line defects out of {num_lines} requested.")
                break 
    
    def reset(self):
        self.grid = [[self.base_work_units for _ in range(self.size)] for _ in range(self.size)]

# --- Algorithm to Test ---
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

# --- Experiment Execution ---
def run_single_config_test(crystal, defect_type, defect_count, defect_work_units, 
                           algorithm, busy_work_iter_per_unit, 
                           num_iterations, num_instances):
    """Runs tests for a single defect type and count, measuring actual execution time."""
    actual_timings_ns = []

    if defect_count < 0: # Should not happen with current lists
        return 0,0 

    for i_instance in range(num_instances):
        crystal.reset()
        if defect_count > 0: # Only introduce defects if count is positive
            if defect_type == "point":
                crystal.introduce_point_defects_by_count(defect_count, defect_work_units)
            elif defect_type == "line":
                crystal.introduce_line_defects_by_count(defect_count, defect_work_units)

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
    """Runs the full experiment for Hypothesis 5."""
    print("🔬 HYPOTHESIS 5: CRITICAL DESTABILIZATION (BASELINE TEMP LOGGING RUN)")
    print(f"Grid Size: {GRID_SIZE}x{GRID_SIZE}, Base Work Units: {BASE_CELL_WORK_UNITS}")
    print(f"Defect Work Units: {DEFECT_CELL_WORK_UNITS}")
    print(f"Busy Work Iterations per Unit: {BUSY_WORK_ITERATIONS_PER_WORK_UNIT}")
    print(f"Iterations per config: {NUM_ITERATIONS_PER_CONFIG}, Instances per count (baseline): 1")
    print("-" * 80)
    print("Defect Type,Defect Count,Mean Exec Time (ms),CV")

    # --- Start Temperature Logger ---
    logger_process = None
    # Rename old log if it exists, so logger script creates a fresh one
    # The logger script itself will use "temperature_log.csv" but we'll rename it after.
    default_temp_log_path = os.path.join(SCRIPT_DIR, "temperature_log.csv")
    if os.path.exists(default_temp_log_path):
        try:
            os.remove(default_temp_log_path)
            print(f"Removed existing default temp log: {default_temp_log_path}")
        except OSError as e:
            print(f"Error removing existing temp log {default_temp_log_path}: {e}") 

    if os.path.exists(TEMP_LOGGER_STOP_FLAG):
         os.remove(TEMP_LOGGER_STOP_FLAG) # Clean up old flag if any

    if not os.path.exists(TEMP_LOGGER_SCRIPT):
        print(f"ERROR: Temperature logger script not found at {TEMP_LOGGER_SCRIPT}")
        print("Skipping temperature logging.")
    else:
        print(f"Starting temperature logger: {TEMP_LOGGER_SCRIPT}")
        # Using .venv python if available, otherwise system python3
        python_executable = "python3"
        venv_python = os.path.join(SCRIPT_DIR, "..", ".venv", "bin", "python3") 
        if os.path.exists(venv_python):
            python_executable = venv_python
            print(f"Using venv python: {python_executable}")
        else:
            print(f"Using system python: {python_executable}")
        
        try:
            logger_process = subprocess.Popen([python_executable, TEMP_LOGGER_SCRIPT])
            print(f"Temperature logger process started (PID: {logger_process.pid}).")
            time.sleep(2) # Give logger a moment to start up and write header
        except Exception as e:
            print(f"Failed to start temperature logger: {e}")
            logger_process = None
    # --------------------------------

    crystal = CrystalGrid(GRID_SIZE, BASE_CELL_WORK_UNITS)
    baseline_mean_ns = -1
    baseline_cv = -1

    try:
        # Test Point Defects by count - MODIFIED to run only baseline
        print("\nStarting: Point Defects Loop (Baseline Only)")
        for count in POINT_DEFECT_COUNTS: # This will only be [0]
            if count == 0:
                print(f"Starting: Point Defects, Count: {count} (Baseline)")
                current_instances = 1 # As per original H5 script logic for baseline
                
                mean_ns, cv = run_single_config_test(crystal, "point", count, DEFECT_CELL_WORK_UNITS, 
                                                        process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                        NUM_ITERATIONS_PER_CONFIG, current_instances)
                defect_type_str = "Baseline"
                print(f"{defect_type_str},{count},{mean_ns / 1e6:.3f},{cv:.6f}")
                print(f"Finished: Point Defects, Count: {count}")
                baseline_mean_ns = mean_ns
                baseline_cv = cv
            else:
                print(f"Skipping Point Defects, Count: {count} for this focused run.")
        print("Finished: Point Defects Loop (Baseline Only)")

        # MODIFIED: Skip Line Defects Loop for this focused run
        print("\nSkipping: Line Defects Loop for this focused run.")

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
            with open(TEMP_LOGGER_STOP_FLAG, 'w') as f_stop:
                f_stop.write('stop') # Create the stop flag
            
            print("Waiting for temperature logger to terminate...")
            try:
                logger_process.wait(timeout=10) # Wait for up to 10 seconds
                if logger_process.poll() is None: # Check if still running
                    print("Temperature logger did not terminate in time, attempting to kill.")
                    logger_process.kill()
                    logger_process.wait(timeout=5)
                print("Temperature logger process finished.")
            except subprocess.TimeoutExpired:
                print("Timeout waiting for logger to stop. It might still be running.")
            except Exception as e:
                print(f"Error managing logger process: {e}")
            
            # Rename the generic log file to a specific one for this run
            if os.path.exists(default_temp_log_path):
                try:
                    os.rename(default_temp_log_path, TEMP_LOG_OUTPUT)
                    print(f"Temperature log saved to: {TEMP_LOG_OUTPUT}")
                except OSError as e:
                    print(f"Error renaming temperature log {default_temp_log_path} to {TEMP_LOG_OUTPUT}: {e}")
            else:
                print(f"Warning: Expected temperature log {default_temp_log_path} not found for renaming.")

        if os.path.exists(TEMP_LOGGER_STOP_FLAG):
             os.remove(TEMP_LOGGER_STOP_FLAG) # Clean up flag
        # --------------------------------

    print("-" * 80)
    print("Baseline temperature logging run finished.")

if __name__ == "__main__":
    run_experiment() 