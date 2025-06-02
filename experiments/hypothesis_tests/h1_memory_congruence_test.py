#!/usr/bin/env python3
"""
H1: MEMORY CONGRUENCE TEST
Tests Hypothesis 1: "Crystallographic Congruence" between Data Structure and Memory Hierarchy.
This experiment investigates if the Coefficient of Variation (CV) of memory access times
is minimized when the data block size used in processing aligns with hardware memory
features like L1 cache line size.
"""

import time
import statistics
import array

# --- Configuration ---
L1_CACHE_LINE_SIZE_BYTES = 64  # Common L1 cache line size
TOTAL_DATA_SIZE_MB = 8
ELEMENT_SIZE_BYTES = 4  # Assuming 4-byte integers
NUM_ITERATIONS_PER_BLOCK_SIZE = 100  # Number of times to run the test for each block size

# Block sizes to test (in bytes).
# Include multiples, sub-multiples, and values around the cache line size.
BLOCK_SIZES_BYTES = sorted(list(set([
    8, 16, 24, 32, 40, 48, 56,
    L1_CACHE_LINE_SIZE_BYTES - 16,
    L1_CACHE_LINE_SIZE_BYTES - 8,
    L1_CACHE_LINE_SIZE_BYTES,
    L1_CACHE_LINE_SIZE_BYTES + 8,
    L1_CACHE_LINE_SIZE_BYTES + 16,
    L1_CACHE_LINE_SIZE_BYTES * 2 - 8,
    L1_CACHE_LINE_SIZE_BYTES * 2,
    L1_CACHE_LINE_SIZE_BYTES * 3,
    L1_CACHE_LINE_SIZE_BYTES * 4,
    256, 512
])))


def create_data_array(total_size_bytes, element_size_bytes):
    """Creates a large array of integers."""
    num_elements = total_size_bytes // element_size_bytes
    # Using 'i' for signed int, or 'L' for unsigned long if more range needed
    # 'array.array' is more memory efficient than a Python list of ints.
    data = array.array('i', [i % 256 for i in range(num_elements)])
    print(f"Created data array: {len(data)} elements, approx {len(data) * data.itemsize / (1024*1024):.2f} MB")
    return data

def process_data_in_blocks(data_array, block_size_bytes, element_size_bytes):
    """
    Processes the data array by summing elements in contiguous blocks.
    Returns the total sum to ensure work is not optimized away.
    """
    total_sum = 0
    elements_per_block = block_size_bytes // element_size_bytes
    if elements_per_block == 0:
        # Handle cases where block_size_bytes < element_size_bytes if necessary,
        # or ensure block_size_bytes is always a multiple of element_size_bytes.
        # For simplicity, we assume it's a multiple or large enough.
        return 0 # Or raise an error

    num_elements = len(data_array)
    for i in range(0, num_elements, elements_per_block):
        end_index = min(i + elements_per_block, num_elements)
        block_sum = 0
        for j in range(i, end_index):
            block_sum += data_array[j]
        total_sum += block_sum
    return total_sum

def run_experiment():
    """Runs the full experiment for Hypothesis 1."""
    print("🔬 HYPOTHESIS 1: MEMORY CONGRUENCE TEST")
    print(f"Assuming L1 Cache Line Size: {L1_CACHE_LINE_SIZE_BYTES} bytes")
    print(f"Total data size for test: {TOTAL_DATA_SIZE_MB} MB")
    print(f"Element size: {ELEMENT_SIZE_BYTES} bytes")
    print(f"Iterations per block size: {NUM_ITERATIONS_PER_BLOCK_SIZE}")
    print("-" * 60)
    print("Block Size (Bytes),Mean Time (ns),CV (Coefficient of Variation)")

    data = create_data_array(TOTAL_DATA_SIZE_MB * 1024 * 1024, ELEMENT_SIZE_BYTES)

    for block_size_b in BLOCK_SIZES_BYTES:
        if block_size_b < ELEMENT_SIZE_BYTES or block_size_b % ELEMENT_SIZE_BYTES != 0:
            print(f"Skipping block size {block_size_b}B: not a multiple of element size {ELEMENT_SIZE_BYTES}B or too small.")
            continue

        timings_ns = []
        for _ in range(NUM_ITERATIONS_PER_BLOCK_SIZE):
            start_time = time.perf_counter_ns()
            # The actual work being timed
            process_data_in_blocks(data, block_size_b, ELEMENT_SIZE_BYTES)
            end_time = time.perf_counter_ns()
            timings_ns.append(end_time - start_time)

        if not timings_ns:
            continue

        mean_time_ns = statistics.mean(timings_ns)
        stdev_time_ns = statistics.stdev(timings_ns) if len(timings_ns) > 1 else 0
        
        cv = 0
        if mean_time_ns > 0:
            cv = stdev_time_ns / mean_time_ns
        
        print(f"{block_size_b},{mean_time_ns:.0f},{cv:.6f}")

    print("-" * 60)
    print("Experiment finished.")

if __name__ == "__main__":
    # Correcting a typo in BLOCK_SIZES_BYTES definition
    # L1_CACHE_LINE_S_BYTES should be L1_CACHE_LINE_SIZE_BYTES
    # This fix is applied directly here as the edit tool creates a new file.
    # This kind of direct fix in the __main__ block is not ideal for module code
    # but okay for a self-contained script where definition is just above.
    # Ideally, the list definition itself would be corrected.
    # For the purpose of this tool, let's reconstruct the list correctly.
    
    corrected_block_sizes = sorted(list(set([
        8, 16, 24, 32, 40, 48, 56,
        L1_CACHE_LINE_SIZE_BYTES - 16 if L1_CACHE_LINE_SIZE_BYTES > 16 else L1_CACHE_LINE_SIZE_BYTES, # ensure positive
        L1_CACHE_LINE_SIZE_BYTES - 8 if L1_CACHE_LINE_SIZE_BYTES > 8 else L1_CACHE_LINE_SIZE_BYTES,   # ensure positive
        L1_CACHE_LINE_SIZE_BYTES,
        L1_CACHE_LINE_SIZE_BYTES + 8,
        L1_CACHE_LINE_SIZE_BYTES + 16,
        L1_CACHE_LINE_SIZE_BYTES * 2 - 8 if L1_CACHE_LINE_SIZE_BYTES * 2 > 8 else L1_CACHE_LINE_SIZE_BYTES * 2, # ensure positive
        L1_CACHE_LINE_SIZE_BYTES * 2,
        L1_CACHE_LINE_SIZE_BYTES * 3,
        L1_CACHE_LINE_SIZE_BYTES * 4,
        256, 512
    ])))
    # Filter out any non-positive or duplicate sizes again due to corrections
    BLOCK_SIZES_BYTES = sorted(list(set(bs for bs in corrected_block_sizes if bs > 0)))

    run_experiment() 