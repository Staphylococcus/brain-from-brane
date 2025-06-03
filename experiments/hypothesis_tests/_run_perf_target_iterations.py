import time
import json
import argparse
import sys
import random # Needed for CrystalGrid

# --- Copied and Adapted from H5 experiment script ---
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
                # print(f"    DEBUG: Warning: Could only place {len(defected_cells)} unique point defects out of {num_defects} requested.", file=sys.stderr)
                break

    def introduce_line_defects_by_count(self, num_lines, defect_work_units):
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
                # print(f"    DEBUG: Warning: Could only place {i} lines out of {num_lines} requested due to saturation.", file=sys.stderr)
                break 
    
    def reset(self):
        self.grid = [[self.base_work_units for _ in range(self.size)] for _ in range(self.size)]

# --- Algorithm to Test ---
def busy_work(iterations):
    s = 0
    for i in range(iterations):
        s = (s + i) * (i % 3 + 1) 
        s = s % 1000000 
    return s

def process_crystal(crystal, busy_work_iter_per_unit):
    volatile_sum = 0 
    for r in range(crystal.size):
        for c in range(crystal.size):
            work_units_for_cell = crystal.get_work_units(r,c)
            volatile_sum += busy_work(work_units_for_cell * busy_work_iter_per_unit)
    return volatile_sum
# --- End of Copied and Adapted Code ---


def main():
    parser = argparse.ArgumentParser(description="Run cellular automata simulation iterations for timing, using internal CrystalGrid.")
    parser.add_argument("--grid_size", type=int, required=True)
    parser.add_argument("--base_cell_work_units", type=int, required=True)
    parser.add_argument("--defect_type", type=str, choices=["Line", "Point", "Baseline"], required=True)
    parser.add_argument("--defect_count", type=int, required=True, help="Number of defects. Ignored if defect_type is Baseline.")
    parser.add_argument("--defect_cell_work_units", type=int, required=True)
    parser.add_argument("--busy_work_iterations_per_work_unit", type=int, required=True)
    parser.add_argument("--num_timing_iterations", type=int, required=True, help="Number of simulation runs to time for this instance.")
    
    args = parser.parse_args()

    grid_obj = CrystalGrid(args.grid_size, args.base_cell_work_units)
    grid_obj.reset() # Ensure a clean state before applying defects for this instance

    if args.defect_type == "Line":
        if args.defect_count > 0:
            grid_obj.introduce_line_defects_by_count(args.defect_count, args.defect_cell_work_units)
    elif args.defect_type == "Point":
        if args.defect_count > 0:
            grid_obj.introduce_point_defects_by_count(args.defect_count, args.defect_cell_work_units)
    # For "Baseline", defect_count is effectively 0 or ignored, grid remains pristine.

    iteration_times_ns = []
    for _ in range(args.num_timing_iterations):
        start_time = time.perf_counter_ns()
        process_crystal(grid_obj, args.busy_work_iterations_per_work_unit)
        end_time = time.perf_counter_ns()
        iteration_times_ns.append(end_time - start_time)

    print(json.dumps(iteration_times_ns))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled exception in _run_perf_target_iterations.py: {e}", file=sys.stderr)
        sys.exit(1) 