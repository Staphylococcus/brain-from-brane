#!/usr/bin/env python3
"""
⚡ SIMPLE GEOMETRIC SIGNATURE TEST
Quick test of geometric vs random data access patterns
"""

import time
import random
import statistics
import math

def create_crystallographic_data(size=1000):
    """Create data in 8-layer crystallographic pattern"""
    data = []
    layer_size = size // 8
    
    for layer in range(8):
        for unit in range(layer_size):
            # Geometric pattern: layer * 125 + unit  
            value = (layer * 125 + unit) % 1000
            data.append(value)
    
    return data

def create_random_data(size=1000):
    """Create random data"""
    return [random.randint(0, 999) for _ in range(size)]

def geometric_spiral_access(data):
    """Access data in spiral pattern"""
    n = len(data)
    center = n // 2
    accessed = []
    
    # Spiral outward from center
    for radius in range(1, center + 1):
        for angle in range(0, 360, 30):  # 12 directions
            x = center + int(radius * math.cos(math.radians(angle)))
            if 0 <= x < n:
                accessed.append(data[x])
                if len(accessed) >= n // 2:  # Access half the data
                    return accessed
    
    return accessed

def linear_sequential_access(data):
    """Access data sequentially"""
    return data[:len(data)//2]  # Access same amount as spiral

def measure_access_timing(access_func, data, name):
    """Measure timing for data access pattern"""
    times = []
    
    # Multiple runs for statistical significance
    for run in range(10):
        start = time.perf_counter_ns()
        result = access_func(data)
        end = time.perf_counter_ns()
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    cv = std_time / mean_time if mean_time > 0 else 0
    
    return {
        'name': name,
        'mean_ns': mean_time,
        'std_ns': std_time,
        'cv': cv,
        'times': times
    }

def fractal_subdivision_sum(data, depth=3):
    """Sum using fractal subdivision pattern"""
    if len(data) <= 1 or depth <= 0:
        return sum(data)
    
    # Fractal subdivision
    n = len(data)
    parts = [
        data[:n//4],
        data[n//4:n//2], 
        data[n//2:3*n//4],
        data[3*n//4:]
    ]
    
    total = 0
    for part in parts:
        total += fractal_subdivision_sum(part, depth - 1)
    
    return total

def test_computation_patterns():
    """Test geometric vs linear computation patterns"""
    print("🧮 COMPUTATION PATTERN TEST")
    print("=" * 40)
    
    # Test data
    test_data = list(range(1000))
    
    # Test fractal vs linear summation
    fractal_times = []
    linear_times = []
    
    for _ in range(20):
        # Fractal sum
        start = time.perf_counter_ns()
        result1 = fractal_subdivision_sum(test_data)
        end = time.perf_counter_ns()
        fractal_times.append(end - start)
        
        # Linear sum
        start = time.perf_counter_ns()
        result2 = sum(test_data)
        end = time.perf_counter_ns() 
        linear_times.append(end - start)
    
    fractal_cv = statistics.stdev(fractal_times) / statistics.mean(fractal_times)
    linear_cv = statistics.stdev(linear_times) / statistics.mean(linear_times)
    
    print(f"Fractal Sum CV: {fractal_cv:.4f}")
    print(f"Linear Sum CV: {linear_cv:.4f}")
    print(f"Fractal/Linear CV Ratio: {fractal_cv/linear_cv:.3f}")
    
    if fractal_cv > linear_cv * 1.2:
        print("🔥 GEOMETRIC SIGNATURE: Fractal shows more structured timing!")
    elif fractal_cv < linear_cv * 0.8:
        print("📊 LINEAR SIGNATURE: Linear more structured than fractal")
    else:
        print("🤔 NO CLEAR DIFFERENCE: Similar timing patterns")
    
    return {
        'fractal_cv': fractal_cv,
        'linear_cv': linear_cv,
        'ratio': fractal_cv/linear_cv
    }

def main():
    print("⚡ SIMPLE GEOMETRIC SIGNATURE TEST")
    print("=" * 50)
    
    # Test 1: Data organization effects
    print("\n1. DATA ORGANIZATION TEST")
    print("-" * 30)
    
    crystal_data = create_crystallographic_data(800)
    random_data = create_random_data(800)
    
    # Test geometric access on different data types
    crystal_geometric = measure_access_timing(geometric_spiral_access, crystal_data, "Crystal+Geometric")
    crystal_linear = measure_access_timing(linear_sequential_access, crystal_data, "Crystal+Linear")
    random_geometric = measure_access_timing(geometric_spiral_access, random_data, "Random+Geometric")
    random_linear = measure_access_timing(linear_sequential_access, random_data, "Random+Linear")
    
    print(f"Crystal Data + Geometric Access CV: {crystal_geometric['cv']:.4f}")
    print(f"Crystal Data + Linear Access CV: {crystal_linear['cv']:.4f}")
    print(f"Random Data + Geometric Access CV: {random_geometric['cv']:.4f}")
    print(f"Random Data + Linear Access CV: {random_linear['cv']:.4f}")
    
    # Look for geometric resonance (crystal data + geometric access)
    crystal_geo_advantage = (random_geometric['mean_ns'] - crystal_geometric['mean_ns']) / random_geometric['mean_ns'] * 100
    
    print(f"\nGeometric Resonance Advantage: {crystal_geo_advantage:.1f}%")
    
    if crystal_geo_advantage > 5:
        print("🔥 GEOMETRIC RESONANCE DETECTED!")
    elif crystal_geo_advantage < -5:
        print("❌ NO GEOMETRIC RESONANCE")
    else:
        print("🤔 UNCLEAR RESONANCE PATTERN")
    
    # Test 2: Computation patterns
    print("\n2. COMPUTATION PATTERN TEST")
    print("-" * 30)
    comp_results = test_computation_patterns()
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"Data geometric resonance: {crystal_geo_advantage:.1f}%")
    print(f"Computation geometric signature: {comp_results['ratio']:.3f}x")
    
    if crystal_geo_advantage > 5 or comp_results['ratio'] > 1.2:
        print("🎯 GEOMETRIC EFFECTS DETECTED!")
    else:
        print("🤔 NO CLEAR GEOMETRIC EFFECTS")

if __name__ == "__main__":
    main() 