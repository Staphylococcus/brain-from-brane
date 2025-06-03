#!/usr/bin/env python3
import numpy as np
import time

def initialize_grid(size, seed_pattern=None, seed_pos=(0,0), random_fill_p=0.5):
    """
    Initializes a grid.
    - Fills randomly with 0s and 1s based on random_fill_p.
    - If seed_pattern is provided, it places this pattern at seed_pos.
    """
    grid = np.random.choice([0, 1], size=(size, size), p=[1-random_fill_p, random_fill_p])
    if seed_pattern is not None:
        pattern_rows, pattern_cols = seed_pattern.shape
        r_start, c_start = seed_pos
        r_end, c_end = r_start + pattern_rows, c_start + pattern_cols
        if r_end <= size and c_end <= size:
            grid[r_start:r_end, c_start:c_end] = seed_pattern
        else:
            print("Warning: Seed pattern extends beyond grid boundaries. Not placing seed.")
    return grid

def print_grid(grid, generation):
    """Prints the grid to the console, replacing 0s with '.' and 1s with '#'."""
    print(f"--- Generation {generation} ---")
    for row in grid:
        print(" ".join(['#' if cell == 1 else '.' for cell in row]))
    print("\n")

def get_moore_neighbors(grid, r, c):
    """Gets the states of the 8 Moore neighbors for a cell at (r, c)."""
    neighbors = []
    size = grid.shape[0]
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue # Skip the cell itself
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size: # Check bounds
                neighbors.append(grid[nr, nc])
    return neighbors

def apply_majority_rule(grid, defect_row_index=None, initial_sticky_states=None, defect_rule_type='force_zero'):
    """
    Applies the majority rule synchronously to update the grid for most cells.
    Cells on the defect_row_index follow a rule specified by defect_rule_type.
    Default majority rule: cell becomes the state of the majority of its 8 Moore neighbors.
                         Ties result in no change.
    Defect line rules:
    - 'force_zero': cells on defect_row_index are forced to 0.
    - 'sticky': cells on defect_row_index keep their state from initial_sticky_states.
    - 'minority_preference': cells on defect_row_index take the minority state of neighbors.
    """
    size = grid.shape[0]
    new_grid = np.copy(grid)

    for r in range(size):
        for c in range(size):
            neighbors = get_moore_neighbors(grid, r, c)
            # if not neighbors: # This check is actually not needed if grid size >=2, as corners will have 3 neighbors
            #     continue
            num_neighbors = len(neighbors)
            sum_neighbors = sum(neighbors)

            if defect_row_index is not None and r == defect_row_index:
                if defect_rule_type == 'force_zero':
                    new_grid[r, c] = 0
                elif defect_rule_type == 'sticky' and initial_sticky_states is not None:
                    new_grid[r, c] = initial_sticky_states[r, c]
                elif defect_rule_type == 'minority_preference':
                    if num_neighbors > 0: # Avoid division by zero for isolated cells (though unlikely here)
                        if sum_neighbors < num_neighbors / 2: # Minority is 1s
                            new_grid[r, c] = 1
                        elif sum_neighbors > num_neighbors / 2: # Minority is 0s
                            new_grid[r, c] = 0
                        # Else (tie for majority/minority): new_grid[r,c] remains current value
                    # else: cell remains its current value if it has no_neighbors (should not happen in connected grid)
                else: # Default or unknown defect rule for defect line -> apply majority rule
                    if sum_neighbors > num_neighbors / 2:
                        new_grid[r, c] = 1
                    elif sum_neighbors < num_neighbors / 2:
                        new_grid[r, c] = 0
            else: # Normal majority rule for non-defect-line cells
                if sum_neighbors > num_neighbors / 2:
                    new_grid[r, c] = 1
                elif sum_neighbors < num_neighbors / 2:
                    new_grid[r, c] = 0
            # Else (tie for majority rule, or no change for minority rule tie): new_grid[r,c] remains current
            
    return new_grid

def main():
    print("Starting main()...")
    GRID_SIZE = 20
    NUM_GENERATIONS = 30
    PRINT_EVERY_N_GENERATIONS = 5
    INITIAL_RANDOM_FILL_PROBABILITY = 0.2 # Hostile environment (mostly 0s)
    DEFECT_LINE_ROW = None # No defect line
    DEFECT_RULE = 'force_zero' # Irrelevant as DEFECT_LINE_ROW is None

    # Seed pattern with a corner defect
    seed = np.array([[0, 1, 1], # Corner defect at seed[0,0]
                     [1, 1, 1],
                     [1, 1, 1]])
    seed_position = (GRID_SIZE // 2 - 1, GRID_SIZE // 2 - 1)
    
    print("Initializing grid...")
    current_grid = initialize_grid(GRID_SIZE, seed_pattern=seed, seed_pos=seed_position, random_fill_p=INITIAL_RANDOM_FILL_PROBABILITY)
    initial_grid_snapshot = np.copy(current_grid) 
    print("Grid initialized.")
    print_grid(current_grid, 0)

    for gen in range(1, NUM_GENERATIONS + 1):
        print(f"Processing Generation {gen}...")
        current_grid = apply_majority_rule(current_grid, 
                                           defect_row_index=DEFECT_LINE_ROW, 
                                           initial_sticky_states=initial_grid_snapshot,
                                           defect_rule_type=DEFECT_RULE)
        if gen % PRINT_EVERY_N_GENERATIONS == 0:
            print_grid(current_grid, gen)
            
    print("Simulation finished.")

if __name__ == "__main__":
    main() 