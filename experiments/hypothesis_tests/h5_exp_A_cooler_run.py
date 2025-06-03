#!/usr/bin/env python3
"""
H5 Experiment A: Cooler Run Re-confirmation
Based on h5_critical_destabilization_test.py
This script attempts to reproduce the conditions of the original H5 experiment
where CV peaks were observed, by using lower iteration/instance counts and
implementing cool-down periods between testing different defect counts.
"""

import time
import statistics
import random
import copy
import subprocess
import os
import re # For get_current_package_temp_from_sensors
from datetime import datetime # Added for precise timing

# --- Make @profile a no-op if line_profiler is not being used ---
try:
    # This will be defined if the script is run with kernprof -l -v script.py
    profile
except NameError:
    def profile(func):
        return func # Return the original function unchanged
# ------

# --- Configuration for Experiment A (Cooler Run) ---
GRID_SIZE = 50
BASE_CELL_WORK_UNITS = 1
DEFECT_CELL_WORK_UNITS = 101
BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000

NUM_ITERATIONS_PER_CONFIG = 5 # Lower, like original H5
NUM_INSTANCES_PER_COUNT = 3   # Consistent for all defect counts, including baseline

POINT_DEFECT_COUNTS = [] # Focus on line defects
LINE_DEFECT_COUNTS = [0, 1, 2, 3, 4, 5, 10] # Cover potential peaks and drop-off

# --- Paths for temperature logging ---
# Assumes this script is in 'experiments/hypothesis_tests/'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_LOGGER_SCRIPT = os.path.join(SCRIPT_DIR, "utils", "log_cpu_temps.py")
# The logger script (log_cpu_temps.py) places its flag and default log in its parent directory,
# which is SCRIPT_DIR (experiments/hypothesis_tests/)
TEMP_LOGGER_STOP_FLAG = os.path.join(SCRIPT_DIR, "stop_temp_logging.flag")
DEFAULT_TEMP_LOG_BY_LOGGER = os.path.join(SCRIPT_DIR, "temperature_log.csv")
TEMP_LOG_OUTPUT = os.path.join(SCRIPT_DIR, "temperature_log_h5_exp_A_cool.csv")
# New timing log file for work phase markers
TIMING_LOG_FILE = os.path.join(SCRIPT_DIR, "timing_log_exp_A.csv")
# New experiment results output file
EXPERIMENT_RESULTS_FILE = os.path.join(SCRIPT_DIR, "experiment_results_exp_A.csv")

# --- Cool-down Configuration ---
COOL_DOWN_TARGET_TEMP_C = 45.0
COOL_DOWN_CHECK_INTERVAL_S = 10
COOL_DOWN_MAX_WAIT_MINUTES = 10

# --- Crystal and Defect Implementation (from H5) ---
class CrystalGrid:
    def __init__(self, size, base_work_units):
        self.size = size
        self.base_work_units = base_work_units
        self.grid = [[base_work_units for _ in range(size)] for _ in range(size)]
        self.total_cells = size * size

    def get_work_units(self, r, c):
        return self.grid[r][c]

    def introduce_point_defects_by_count(self, num_defects, defect_work_units):
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
                # This condition might be too strict if num_defects is large
                print(f"    DEBUG: Warning: Could only place {len(defected_cells)} unique point defects out of {num_defects} requested.")
                break

    def introduce_line_defects_by_count(self, num_lines, defect_work_units):
        if num_lines == 0: return
        defected_rows = set(); defected_cols = set()
        for i in range(num_lines):
            is_row_defect = random.choice([True, False]); attempts = 0; placed_this_line = False
            max_placement_attempts = 2 * self.size # Max unique lines
            while attempts < max_placement_attempts:
                if is_row_defect:
                    r = random.randrange(self.size)
                    if r not in defected_rows or len(defected_rows) + len(defected_cols) >= (self.size * 2): # Allow re-defect if all lines somehow are already unique and defected
                        for c_idx in range(self.size): self.grid[r][c_idx] = defect_work_units
                        defected_rows.add(r); placed_this_line = True; break
                else: # Column defect
                    c = random.randrange(self.size)
                    if c not in defected_cols or len(defected_rows) + len(defected_cols) >= (self.size * 2):
                        for r_idx in range(self.size): self.grid[r_idx][c] = defect_work_units
                        defected_cols.add(c); placed_this_line = True; break
                
                # Smart switch if one type is exhausted
                if (is_row_defect and len(defected_rows) == self.size and len(defected_cols) < self.size):
                    is_row_defect = not is_row_defect
                elif (not is_row_defect and len(defected_cols) == self.size and len(defected_rows) < self.size):
                    is_row_defect = not is_row_defect
                attempts +=1
            if not placed_this_line and i < num_lines -1 : # If we couldn't place this line and it's not the last one requested
                # This might occur if num_lines > total unique lines possible (2*size)
                # print(f"    DEBUG: Warning: Could only place {i} unique line defects out of {num_lines} requested.")
                break 
    
    def reset(self):
        self.grid = [[self.base_work_units for _ in range(self.size)] for _ in range(self.size)]

# --- Helper function for temperature check ---
def get_current_package_temp_from_sensors():
    """Runs 'sensors' and returns the current Package ID 0 temperature, or a high value on error."""
    try:
        result = subprocess.run(["sensors"], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            # print(f"Warning: 'sensors' command exited with code {result.returncode}. stderr: {result.stderr.strip()}")
            return 999.0 # Indicate error or non-parsable output
        output = result.stdout
        # Standard 'Package id 0:  +45.0°C  (high = +100.0°C, crit = +100.0°C)'
        package_match = re.search(r"Package id 0:\s*\+?([\d\.]+)", output)
        if package_match:
            return float(package_match.group(1))
        else:
            # Fallback for other common CPU temperature lines if 'Package id 0' is not found
            # Example: 'CPU Temperature:   +40.0 C' or 'temp1: ... Tdie: ...'
            # This regex is a bit more generic.
            generic_package_match = re.search(r"(?:CPU Temp|Core Temp|Composite|Tdie|temp1_input):\s*\+?([\d\.]+)", output, re.IGNORECASE)
            if generic_package_match:
                 # print("Warning: 'Package id 0' not found, using generic CPU/Package temperature.")
                 return float(generic_package_match.group(1))
            # print("Warning: Could not parse Package temperature from 'sensors' output.")
            # For debugging: print(f"Sensors output for temp parsing failure:\\n{output}")
            return 999.0 # Indicate error
    except FileNotFoundError:
        print("Warning: 'sensors' command not found. Cool-down check skipped (returning 0.0).")
        return 0.0 # Return low value to effectively bypass cool-down if sensors isn't available
    except Exception as e:
        print(f"Warning: Error getting current temperature for cool-down: {e}")
        return 999.0 # Indicate error

# --- Algorithm to Test (from H5) ---
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

# --- Experiment Execution Logic (from H5) ---
def run_single_config_test(crystal, defect_type, defect_count, defect_work_units, 
                           algorithm, busy_work_iter_per_unit, 
                           num_iterations, num_instances):
    actual_timings_ns = []
    for i_instance in range(num_instances):
        crystal.reset()
        if defect_count > 0:
            # This script only calls with defect_type="line"
            if defect_type == "line":
                crystal.introduce_line_defects_by_count(defect_count, defect_work_units)
            # No point defects in this script
        for i_iter in range(num_iterations):
            start_time = time.perf_counter_ns()
            algorithm(crystal, busy_work_iter_per_unit)
            end_time = time.perf_counter_ns()
            actual_timings_ns.append(end_time - start_time)
            
    if not actual_timings_ns or len(actual_timings_ns) < 2: # Need at least 2 for stdev
        return 0, 0 
    
    mean_time_ns = statistics.mean(actual_timings_ns)
    stdev_time_ns = statistics.stdev(actual_timings_ns)
    cv = stdev_time_ns / mean_time_ns if mean_time_ns > 0 else 0
    return mean_time_ns, cv

def run_experiment():
    print("🔬 H5 Experiment A: Cooler Run Re-confirmation")
    print(f"Grid Size: {GRID_SIZE}x{GRID_SIZE}, Base Work Units: {BASE_CELL_WORK_UNITS}")
    print(f"Defect Work Units: {DEFECT_CELL_WORK_UNITS}")
    print(f"Busy Work Iterations per Unit: {BUSY_WORK_ITERATIONS_PER_WORK_UNIT}")
    print(f"Iterations per config: {NUM_ITERATIONS_PER_CONFIG}, Instances per count: {NUM_INSTANCES_PER_COUNT}")
    print(f"Cool-down target: Package Temp < {COOL_DOWN_TARGET_TEMP_C}°C (Max wait: {COOL_DOWN_MAX_WAIT_MINUTES} min)")
    print("-" * 80)
    print("Defect Type,Defect Count,Mean Exec Time (ms),CV")

    logger_process = None
    
    # Ensure clean state for logging output files
    if os.path.exists(TEMP_LOG_OUTPUT):
        try: os.remove(TEMP_LOG_OUTPUT); print(f"Removed existing specific temp log: {TEMP_LOG_OUTPUT}")
        except OSError as e: print(f"Warning: Could not remove old specific temp log {TEMP_LOG_OUTPUT}: {e}")
    if os.path.exists(DEFAULT_TEMP_LOG_BY_LOGGER): # Default name logger script uses
        try: os.remove(DEFAULT_TEMP_LOG_BY_LOGGER); print(f"Removed existing default temp log by logger: {DEFAULT_TEMP_LOG_BY_LOGGER}")
        except OSError as e: print(f"Warning: Could not remove old default temp log {DEFAULT_TEMP_LOG_BY_LOGGER}: {e}")
    if os.path.exists(TEMP_LOGGER_STOP_FLAG): # Ensure no old stop flag
         try: os.remove(TEMP_LOGGER_STOP_FLAG); print(f"Removed pre-existing stop flag: {TEMP_LOGGER_STOP_FLAG}")
         except OSError as e: print(f"Warning: Could not remove old stop flag {TEMP_LOGGER_STOP_FLAG}: {e}")

    # Initialize the new timing log file
    try:
        with open(TIMING_LOG_FILE, 'w', newline='') as f_timing:
            f_timing.write("Timestamp,DefectType,DefectCount,PhaseEvent\n")
        print(f"Initialized timing log: {TIMING_LOG_FILE}")
    except IOError as e:
        print(f"ERROR: Could not initialize timing log file {TIMING_LOG_FILE}: {e}")
        # Optionally, decide if you want to exit or continue without timing log
        # return 

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
        # Optionally, decide if you want to exit or continue
        # return

    if not os.path.exists(TEMP_LOGGER_SCRIPT):
        print(f"ERROR: Temperature logger script not found at {TEMP_LOGGER_SCRIPT}. Logging skipped.")
    else:
        print(f"Starting temperature logger: {TEMP_LOGGER_SCRIPT}")
        # Determine Python executable (prefer venv)
        python_executable = "python3" # System default
        # Assuming .venv is at the project root, two levels up from SCRIPT_DIR
        project_root = os.path.join(SCRIPT_DIR, "..", "..")
        venv_python = os.path.join(project_root, ".venv", "bin", "python3")
        if os.path.exists(venv_python):
            python_executable = venv_python
            print(f"Using venv python: {python_executable}")
        else:
            print(f"Using system python: {python_executable} (venv not found at {venv_python})")
        
        try:
            # The logger script (log_cpu_temps.py) determines its paths relative to itself.
            # It will place 'stop_temp_logging.flag' and 'temperature_log.csv'
            # in its parent directory (SCRIPT_DIR, i.e., 'experiments/hypothesis_tests/').
            logger_process = subprocess.Popen([python_executable, TEMP_LOGGER_SCRIPT])
            print(f"Temperature logger process started (PID: {logger_process.pid}).")
            print(f"Logger will create {DEFAULT_TEMP_LOG_BY_LOGGER} and look for {TEMP_LOGGER_STOP_FLAG}")
            time.sleep(3) # Give logger a moment to start up, create files, and write header
        except Exception as e:
            print(f"Failed to start temperature logger: {e}")
            logger_process = None
    
    crystal = CrystalGrid(GRID_SIZE, BASE_CELL_WORK_UNITS)

    try:
        print("\nStarting: Line Defects Loop (Experiment A - Cooler Run)")
        for count_idx, count in enumerate(LINE_DEFECT_COUNTS):
            # Cool-down logic *before* each defect count test (except the very first one, if count_idx is 0)
            if count_idx > 0: # No cool-down needed before the first test (usually baseline)
                print(f"\n--- Cooling down before testing Line Defect Count: {count} ---")
                cool_down_start_time = time.time()
                initial_temp_check = get_current_package_temp_from_sensors()
                print(f"Initial temperature before cool-down attempt: {initial_temp_check:.1f}°C")

                while True:
                    current_temp = get_current_package_temp_from_sensors()
                    if current_temp <= COOL_DOWN_TARGET_TEMP_C : # Use <= for target
                        print(f"Cooled down to {current_temp:.1f}°C. Proceeding.")
                        break
                    print(f"Current package temperature: {current_temp:.1f}°C. Waiting to cool below/at {COOL_DOWN_TARGET_TEMP_C}°C...")
                    
                    if (time.time() - cool_down_start_time) > (COOL_DOWN_MAX_WAIT_MINUTES * 60):
                        print(f"Warning: Max cool-down time ({COOL_DOWN_MAX_WAIT_MINUTES} min) reached. Current temp: {current_temp:.1f}°C. Proceeding anyway.")
                        break
                    time.sleep(COOL_DOWN_CHECK_INTERVAL_S)
                print("------------------------------------------------------------")

            defect_type_str = "Baseline_Line" if count == 0 else "Line"
            print(f"Starting: {defect_type_str}, Defect Count: {count}")

            # Log WORK_PHASE_START
            try:
                with open(TIMING_LOG_FILE, 'a', newline='') as f_timing:
                    f_timing.write(f"{datetime.now().isoformat()},{defect_type_str},{count},WORK_PHASE_START\n")
            except IOError as e:
                print(f"Warning: Could not write WORK_PHASE_START to timing log: {e}")
            
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
        import traceback
        traceback.print_exc()
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    finally:
        if logger_process:
            print("Signaling temperature logger to stop...")
            try:
                with open(TEMP_LOGGER_STOP_FLAG, 'w') as f_stop:
                    f_stop.write('stop') # Create the stop flag in SCRIPT_DIR
                print(f"Stop flag created at {TEMP_LOGGER_STOP_FLAG}")
            except IOError as e_flag:
                print(f"Error creating stop flag {TEMP_LOGGER_STOP_FLAG}: {e_flag}")

            print("Waiting for temperature logger to terminate...")
            try:
                logger_process.wait(timeout=10) # Wait for up to 10 seconds
                if logger_process.poll() is None: # Check if still running
                    print("Temperature logger did not terminate in time, attempting to kill.")
                    logger_process.kill()
                    logger_process.wait(timeout=5) # Wait for kill
                print("Temperature logger process finished.")
            except subprocess.TimeoutExpired:
                print("Timeout waiting for logger to stop. It might still be running.")
            except Exception as e_proc:
                print(f"Error managing logger process shutdown: {e_proc}")
            
            # Rename the generic log file (temperature_log.csv in SCRIPT_DIR) to the specific one for this run
            if os.path.exists(DEFAULT_TEMP_LOG_BY_LOGGER):
                try:
                    os.rename(DEFAULT_TEMP_LOG_BY_LOGGER, TEMP_LOG_OUTPUT)
                    print(f"Temperature log saved to: {TEMP_LOG_OUTPUT}")
                except OSError as e_rename:
                    print(f"Error renaming default temperature log {DEFAULT_TEMP_LOG_BY_LOGGER} to {TEMP_LOG_OUTPUT}: {e_rename}")
            else:
                print(f"Warning: Expected default temperature log {DEFAULT_TEMP_LOG_BY_LOGGER} not found for renaming.")
        
        # Final cleanup of stop flag if it still exists (e.g. if logger failed to remove it)
        if os.path.exists(TEMP_LOGGER_STOP_FLAG):
            try:
                os.remove(TEMP_LOGGER_STOP_FLAG)
                print(f"Cleaned up stop flag: {TEMP_LOGGER_STOP_FLAG}")
            except OSError as e_clean:
                print(f"Warning: Could not clean up stop flag {TEMP_LOGGER_STOP_FLAG}: {e_clean}")


    print("-" * 80)
    print("H5 Experiment A (Cooler Run Re-confirmation) finished.")

if __name__ == "__main__":
    run_experiment() 