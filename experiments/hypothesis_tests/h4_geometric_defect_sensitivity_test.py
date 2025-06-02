#!/usr/bin/env python3
"""
H4: GEOMETRIC DEFECT SENSITIVITY TEST (Refined)
Tests Hypothesis 4: "Geometric Defect Sensitivity" in Information Structures.
This experiment investigates if the CV of *actual execution time* for processing a 
regular "information crystal" (e.g., a simulated 2D grid with CPU-bound work per cell)
shows distinct responses to different types and densities of "geometric defects."
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
BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000 # Calibrate this for reasonable execution time

NUM_ITERATIONS_PER_CONFIG = 3 # Runs per defect configuration (reduced for longer execution)
NUM_INSTANCES_PER_DEFECT_DENSITY = 2 # Different defect placements for same density

# Defect densities to test (as a fraction of total cells for point, or fraction of lines for line)
DEFECT_DENSITIES = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1]

# --- Crystal and Defect Implementation ---
class CrystalGrid:
    def __init__(self, size, base_work_units):
        self.size = size
        self.base_work_units = base_work_units
        # Grid now stores the work multiplier for each cell
        self.grid = [[base_work_units for _ in range(size)] for _ in range(size)]
        self.total_cells = size * size

    def get_work_units(self, r, c):
        return self.grid[r][c]

    def introduce_point_defects(self, density, defect_work_units):
        """Introduces random point defects by setting their work units."""
        num_defects = int(density * self.total_cells)
        if num_defects == 0 and density > 0:
             if self.total_cells > 0: num_defects = 1 

        # Ensure we place unique defects if possible, for low counts
        defected_cells = set()
        for _ in range(num_defects):
            attempts = 0
            while attempts < self.total_cells: # Max attempts to find a new cell
                r, c = random.randrange(self.size), random.randrange(self.size)
                if (r,c) not in defected_cells:
                    self.grid[r][c] = defect_work_units
                    defected_cells.add((r,c))
                    break
                attempts += 1
            if attempts == self.total_cells and len(defected_cells) < num_defects:
                # print(f"Warning: Could only place {len(defected_cells)} unique point defects out of {num_defects}")
                break # Stop if we can't find new cells easily

    def introduce_line_defects(self, density, defect_work_units):
        """Introduces random line (row or column) defects by setting their work units."""
        num_defective_lines = int(density * (2 * self.size))
        if num_defective_lines == 0 and density > 0:
            if (2 * self.size) > 0: num_defective_lines = 1
        
        # Keep track of lines already made defective to try for unique lines
        defected_rows = set()
        defected_cols = set()

        for i in range(num_defective_lines):
            is_row_defect = random.choice([True, False])
            attempts = 0
            placed_this_line = False
            while attempts < (2*self.size): # Max attempts to find a new line
                if is_row_defect:
                    r = random.randrange(self.size)
                    if r not in defected_rows:
                        for c in range(self.size):
                            self.grid[r][c] = defect_work_units
                        defected_rows.add(r)
                        placed_this_line = True
                        break
                else: # Column defect
                    c = random.randrange(self.size)
                    if c not in defected_cols:
                        for r in range(self.size):
                            self.grid[r][c] = defect_work_units
                        defected_cols.add(c)
                        placed_this_line = True
                        break
                is_row_defect = not is_row_defect # Alternate if first choice is taken
                attempts +=1
            # if not placed_this_line and i < num_defective_lines:
            #     print(f"Warning: Could only place {i} unique line defects out of {num_defective_lines}")
            #     break # Stop if we run out of unique lines to defect
    
    def reset(self):
        self.grid = [[self.base_work_units for _ in range(self.size)] for _ in range(self.size)]

# --- Algorithm to Test ---
@profile # If line_profiler is available, for checking where time is spent.
        # Will not affect script if line_profiler is not used to run it.
def busy_work(iterations):
    """A simple CPU-bound task."""
    s = 0
    for i in range(iterations):
        s = (s + i) * (i % 3 + 1) # Some arbitrary computation
        s = s % 1000000 # Keep s bounded to prevent very large numbers slowing it down
    return s

@profile
def process_crystal(crystal, busy_work_iter_per_unit):
    """Processes the crystal by performing busy work proportional to cell work units."""
    # volatile_sum just to ensure busy_work is not optimized away entirely by some compilers
    volatile_sum = 0 
    for r in range(crystal.size):
        for c in range(crystal.size):
            work_units_for_cell = crystal.get_work_units(r,c)
            volatile_sum += busy_work(work_units_for_cell * busy_work_iter_per_unit)
    return volatile_sum

# --- Experiment Execution ---
def run_single_config_test(crystal, defect_type, density, defect_work_units, 
                           algorithm, busy_work_iter_per_unit, 
                           num_iterations, num_instances):
    """Runs tests for a single defect type and density, measuring actual execution time."""
    actual_timings_ns = []

    for i_instance in range(num_instances):
        crystal.reset()
        if defect_type == "point" and density > 0:
            crystal.introduce_point_defects(density, defect_work_units)
        elif defect_type == "line" and density > 0:
            crystal.introduce_line_defects(density, defect_work_units)

        for i_iter in range(num_iterations):
            start_time = time.perf_counter_ns()
            algorithm(crystal, busy_work_iter_per_unit)
            end_time = time.perf_counter_ns()
            actual_timings_ns.append(end_time - start_time)
            
    if not actual_timings_ns or len(actual_timings_ns) < 2:
        return 0, 0 # Mean, CV
    
    mean_time_ns = statistics.mean(actual_timings_ns)
    stdev_time_ns = statistics.stdev(actual_timings_ns)
    cv = stdev_time_ns / mean_time_ns if mean_time_ns > 0 else 0
    return mean_time_ns, cv

def run_experiment():
    """Runs the full experiment for Hypothesis 4 (Refined)."""
    print("🔬 HYPOTHESIS 4: GEOMETRIC DEFECT SENSITIVITY TEST (Refined)")
    print(f"Grid Size: {GRID_SIZE}x{GRID_SIZE}, Base Work Units: {BASE_CELL_WORK_UNITS}")
    print(f"Defect Work Units: {DEFECT_CELL_WORK_UNITS}")
    print(f"Busy Work Iterations per Unit: {BUSY_WORK_ITERATIONS_PER_WORK_UNIT}")
    print(f"Iterations per config: {NUM_ITERATIONS_PER_CONFIG}, Instances per density: {NUM_INSTANCES_PER_DEFECT_DENSITY}")
    print("-" * 80)
    print("Defect Type,Defect Density (approx),Mean Exec Time (ms),CV") # Time in ms for readability

    crystal = CrystalGrid(GRID_SIZE, BASE_CELL_WORK_UNITS)

    try:
        # Test Baseline (No Defects)
        print("Starting: Baseline (No Defects)")
        mean_ns_none, cv_none = run_single_config_test(crystal, "none", 0.0, DEFECT_CELL_WORK_UNITS, 
                                                        process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                        NUM_ITERATIONS_PER_CONFIG, 1) 
        print(f"None,0.000,{mean_ns_none / 1e6:.3f},{cv_none:.6f}")
        print("Finished: Baseline (No Defects)")

        # Test Point Defects
        print("\nStarting: Point Defects Loop")
        for density in DEFECT_DENSITIES:
            if density == 0.0: continue 
            print(f"Starting: Point Defects, Density: {density:.3f}")
            mean_ns, cv = run_single_config_test(crystal, "point", density, DEFECT_CELL_WORK_UNITS, 
                                                    process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT,
                                                    NUM_ITERATIONS_PER_CONFIG, NUM_INSTANCES_PER_DEFECT_DENSITY)
            print(f"Point,{density:.3f},{mean_ns / 1e6:.3f},{cv:.6f}")
            print(f"Finished: Point Defects, Density: {density:.3f}")
        print("Finished: Point Defects Loop")

        # Test Line Defects
        print("\nStarting: Line Defects Loop")
        for density in DEFECT_DENSITIES:
            if density == 0.0: continue
            print(f"Starting: Line Defects, Density: {density:.3f}")
            mean_ns, cv = run_single_config_test(crystal, "line", density, DEFECT_CELL_WORK_UNITS, 
                                                    process_crystal, BUSY_WORK_ITERATIONS_PER_WORK_UNIT, 
                                                    NUM_ITERATIONS_PER_CONFIG, NUM_INSTANCES_PER_DEFECT_DENSITY)
            print(f"Line,{density:.3f},{mean_ns / 1e6:.3f},{cv:.6f}")
            print(f"Finished: Line Defects, Density: {density:.3f}")
        print("Finished: Line Defects Loop")

    except Exception as e:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR: An exception occurred during run_experiment:")
        import traceback
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

    print("-" * 80)
    print("Experiment finished (or terminated due to an error if an error message is shown above).")

if __name__ == "__main__":
    # Simple calibration hint for BUSY_WORK_ITERATIONS_PER_WORK_UNIT
    # Aim for a baseline (no defect) process_crystal run to be e.g. 10-100ms.
    # Grid_size^2 * base_cell_work_units * busy_work_iter_per_unit * (time_per_busy_op)
    # 50*50 * 1 * X * (say 5ns/op) = 50ms = 50,000,000 ns
    # 2500 * X * 5 = 50,000,000
    # X = 50,000,000 / 12500 = 4000. So BUSY_WORK_ITERATIONS_PER_WORK_UNIT around a few thousands.
    # We used 50, might be too short. Let's adjust it based on a quick mental check.
    # If each busy_work op is ~5ns, 50 ops is 250ns. Total for 2500 cells is 2500*250ns = 625,000 ns = 0.625ms.
    # This is probably too fast for NUM_ITERATIONS_PER_CONFIG = 30 to get stable CVs above system noise.
    # Let's assume BUSY_WORK_ITERATIONS_PER_WORK_UNIT should be higher, e.g. 1000-5000.
    # The value 50 in the script is likely too low for robust timing. For the sake of this edit,
    # I will leave it as it was in the prompt, but this is a key tuning parameter.
    # The @profile decorators are for use with kernprof -l -v script.py if line_profiler is installed.
    run_experiment() 