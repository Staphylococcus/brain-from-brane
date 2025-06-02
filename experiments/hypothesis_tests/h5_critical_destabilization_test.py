#!/usr/bin/env python3
"""
H5: CRITICAL DESTABILIZATION BY LOW-COUNT CORRELATED GEOMETRIC DEFECTS
Tests Hypothesis 5: Critical Destabilization by Low-Count Correlated Geometric Defects.
This experiment investigates if the CV of actual execution time shows a localized peak
when a small, critical number of correlated geometric defects (lines) are introduced,
compared to point defects or different counts of line defects.
"""

import time
import statistics
import random
import copy

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

NUM_ITERATIONS_PER_CONFIG = 5 # Increase for more robust CV for H5's specific focus
NUM_INSTANCES_PER_COUNT = 3   # Increase for more robust CV

# Defect counts to test directly
# H5 predicts a peak at low N_l (e.g. 1,2,3), then CV decrease, then potential rise.
LINE_DEFECT_COUNTS = [0, 1, 2, 3, 4, 5, 7, 10, 15, 20] 
# For direct comparison with line defects causing CV spike
POINT_DEFECT_COUNTS = [0, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 50, 100, 125, 250] # 250 is 10% of 2500 cells

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
    print("🔬 HYPOTHESIS 5: CRITICAL DESTABILIZATION BY LOW-COUNT CORRELATED GEOMETRIC DEFECTS")
    print(f"Grid Size: {GRID_SIZE}x{GRID_SIZE}, Base Work Units: {BASE_CELL_WORK_UNITS}")
    print(f"Defect Work Units: {DEFECT_CELL_WORK_UNITS}")
    print(f"Busy Work Iterations per Unit: {BUSY_WORK_ITERATIONS_PER_WORK_UNIT}")
    print(f"Iterations per config: {NUM_ITERATIONS_PER_CONFIG}, Instances per count: {NUM_INSTANCES_PER_COUNT}")
    print("-" * 80)
    print("Defect Type,Defect Count,Mean Exec Time (ms),CV")

    crystal = CrystalGrid(GRID_SIZE, BASE_CELL_WORK_UNITS)

    try:
        # Test Point Defects by count
        print("\nStarting: Point Defects Loop (by count)")
        for count in POINT_DEFECT_COUNTS:
            print(f"Starting: Point Defects, Count: {count}")
            # The case of count = 0 is the baseline, run it once as part of this loop.
            # If count is 0, introduce_point_defects_by_count will do nothing.
            # For baseline (count=0), num_instances can be 1 to save time, or use NUM_INSTANCES_PER_COUNT
            current_instances = 1 if count == 0 else NUM_INSTANCES_PER_COUNT
            
            mean_ns, cv = run_single_config_test(crystal, "point", count, DEFECT_CELL_WORK_UNITS, 
                                                    process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                    NUM_ITERATIONS_PER_CONFIG, current_instances)
            defect_type_str = "Baseline" if count == 0 else "Point"
            print(f"{defect_type_str},{count},{mean_ns / 1e6:.3f},{cv:.6f}")
            print(f"Finished: Point Defects, Count: {count}")
            if count == 0: # So baseline is not repeated in line defect loop if it starts from 0
                baseline_mean_ns = mean_ns
                baseline_cv = cv
        print("Finished: Point Defects Loop (by count)")

        # Test Line Defects by count
        print("\nStarting: Line Defects Loop (by count)")
        for count in LINE_DEFECT_COUNTS:
            if count == 0: # Baseline already done by point defect loop if POINT_DEFECT_COUNTS started with 0
                if 0 in POINT_DEFECT_COUNTS: # Check if baseline was indeed run
                     print(f"Baseline (from Point Loop),0,{baseline_mean_ns / 1e6:.3f},{baseline_cv:.6f}")
                else: # Should not happen if configured correctly, but run baseline if not
                    print(f"Starting: Baseline (for Line Defects), Count: {count}")
                    mean_ns, cv = run_single_config_test(crystal, "line", 0, DEFECT_CELL_WORK_UNITS,
                                                            process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                            NUM_ITERATIONS_PER_CONFIG, 1)
                    print(f"Baseline,{count},{mean_ns / 1e6:.3f},{cv:.6f}")
                    print(f"Finished: Baseline, Count: {count}")
                continue # Skip to next count for line defects

            print(f"Starting: Line Defects, Count: {count}")
            mean_ns, cv = run_single_config_test(crystal, "line", count, DEFECT_CELL_WORK_UNITS, 
                                                    process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                    NUM_ITERATIONS_PER_CONFIG, NUM_INSTANCES_PER_COUNT)
            print(f"Line,{count},{mean_ns / 1e6:.3f},{cv:.6f}")
            print(f"Finished: Line Defects, Count: {count}")
        print("Finished: Line Defects Loop (by count)")

    except Exception as e:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR: An exception occurred during run_experiment:")
        import traceback
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

    print("-" * 80)
    print("Experiment finished.") # Simplified final message

if __name__ == "__main__":
    run_experiment() 