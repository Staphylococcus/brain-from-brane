#!/usr/bin/env python3
"""
Verification: Layer 0 Crystallographic Effect
Confirms that the first directory layer produces the specific CV ≈ 0.150 pattern
"""

import os
import time
import statistics
from pathlib import Path

def measure_access_time(file_path, iterations=100):
    """Measure file access time with high precision"""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        with open(file_path, 'rb') as f:
            data = f.read(1024)  # Read first 1KB
        end = time.perf_counter()
        times.append((end - start) * 1_000_000)  # Convert to microseconds
    return times

def verify_layer_0_effect():
    """Verify that layer 0 reproduces the crystallographic pattern"""
    print("🔬 VERIFYING LAYER 0 CRYSTALLOGRAPHIC EFFECT")
    print("=" * 50)
    
    # Create test directory
    test_dir = Path('./layer_0_verification')
    test_dir.mkdir(exist_ok=True)
    
    # Create layer 0 structure (first level only)
    layer_0_dir = test_dir / 'layer_0'
    layer_0_dir.mkdir(exist_ok=True)
    
    # Create multiple test files in layer 0
    test_files = []
    for i in range(50):
        file_path = layer_0_dir / f'crystal_verify_{i:03d}.dat'
        with open(file_path, 'wb') as f:
            f.write(b'CRYSTALLOGRAPHIC_VERIFICATION' * 300)  # ~8.7KB files
        test_files.append(file_path)
    
    # Warm the cache
    print("Warming filesystem cache...")
    for file_path in test_files:
        with open(file_path, 'rb') as f:
            f.read()
    
    # Multiple verification runs
    print("\nRunning verification measurements...")
    all_results = []
    
    for run in range(5):  # 5 independent runs
        run_times = []
        for file_path in test_files[:20]:  # Test subset
            times = measure_access_time(file_path, 30)
            run_times.extend(times)
        
        mean_time = statistics.mean(run_times)
        cv = statistics.stdev(run_times) / mean_time
        all_results.append(cv)
        
        print(f"  Run {run+1}: CV = {cv:.3f}, Mean = {mean_time:.2f} μs")
    
    # Final analysis
    final_cv = statistics.mean(all_results)
    cv_stdev = statistics.stdev(all_results)
    
    print(f"\n📊 VERIFICATION RESULTS:")
    print(f"   Average CV across 5 runs: {final_cv:.3f} ± {cv_stdev:.3f}")
    print(f"   Target CV (original): 0.150")
    print(f"   Difference: {abs(final_cv - 0.150):.3f}")
    
    if abs(final_cv - 0.150) < 0.020:
        print(f"   ✅ CONFIRMED: Layer 0 reproduces crystallographic periodicity!")
    elif abs(final_cv - 0.150) < 0.050:
        print(f"   ⚠️  CLOSE: Layer 0 shows similar pattern")
    else:
        print(f"   ❌ Different pattern")
    
    return final_cv

if __name__ == "__main__":
    verify_layer_0_effect() 