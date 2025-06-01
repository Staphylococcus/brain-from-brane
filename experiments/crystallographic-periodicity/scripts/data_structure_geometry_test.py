#!/usr/bin/env python3
"""
🌲 DATA STRUCTURE GEOMETRY TEST
Test if geometric data structures show timing signatures
"""

import time
import random
import statistics
import math

class GeometricTree:
    """Binary tree with geometric node organization"""
    def __init__(self, value, layer=0):
        self.value = value
        self.layer = layer
        self.left = None
        self.right = None
        # Geometric property: layer * 125 + position
        self.geometric_id = layer * 125 + (value % 125)
    
    def insert(self, value):
        # Insert based on geometric property
        new_id = (self.layer + 1) * 125 + (value % 125)
        
        if new_id < self.geometric_id:
            if self.left is None:
                self.left = GeometricTree(value, self.layer + 1)
            else:
                self.left.insert(value)
        else:
            if self.right is None:
                self.right = GeometricTree(value, self.layer + 1)
            else:
                self.right.insert(value)
    
    def search(self, value):
        target_id = self.layer * 125 + (value % 125)
        
        if target_id == self.geometric_id:
            return True
        elif target_id < self.geometric_id and self.left:
            return self.left.search(value)
        elif target_id >= self.geometric_id and self.right:
            return self.right.search(value)
        return False

class LinearList:
    """Simple linear list for comparison"""
    def __init__(self):
        self.data = []
    
    def insert(self, value):
        self.data.append(value)
    
    def search(self, value):
        return value in self.data

def create_spiral_array(size=400):
    """Create array organized in spiral pattern"""
    array = [0] * size
    center = size // 2
    
    current = 1
    for radius in range(1, center):
        for angle in range(0, 360, 45):  # 8 directions
            x = center + int(radius * math.cos(math.radians(angle)))
            if 0 <= x < size:
                array[x] = current
                current += 1
    
    return array

def measure_structure_performance(structure, operations, structure_name):
    """Measure timing for data structure operations"""
    times = []
    
    for _ in range(5):  # 5 runs
        start = time.perf_counter_ns()
        
        for op in operations:
            op()
        
        end = time.perf_counter_ns()
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    cv = std_time / mean_time if mean_time > 0 else 0
    
    return {
        'name': structure_name,
        'mean_ns': mean_time,
        'cv': cv
    }

def test_search_patterns():
    """Test geometric vs linear search patterns"""
    print("🔍 SEARCH PATTERN TEST")
    print("=" * 30)
    
    # Create structures
    geometric_tree = GeometricTree(500, 0)
    linear_list = LinearList()
    
    # Add same data to both
    test_values = [random.randint(1, 1000) for _ in range(50)]
    
    for val in test_values:
        geometric_tree.insert(val)
        linear_list.insert(val)
    
    # Create search operations
    search_targets = random.sample(test_values, 20)
    
    geo_operations = [lambda target=t: geometric_tree.search(target) for t in search_targets]
    linear_operations = [lambda target=t: linear_list.search(target) for t in search_targets]
    
    # Measure performance
    geo_result = measure_structure_performance(geometric_tree, geo_operations, "Geometric Tree")
    linear_result = measure_structure_performance(linear_list, linear_operations, "Linear List")
    
    print(f"Geometric Tree Search CV: {geo_result['cv']:.4f}")
    print(f"Linear List Search CV: {linear_result['cv']:.4f}")
    
    cv_ratio = geo_result['cv'] / linear_result['cv'] if linear_result['cv'] > 0 else 0
    print(f"Geometric/Linear CV Ratio: {cv_ratio:.3f}")
    
    return {
        'geometric_cv': geo_result['cv'],
        'linear_cv': linear_result['cv'],
        'ratio': cv_ratio
    }

def test_array_access_patterns():
    """Test spiral vs sequential array access"""
    print("📊 ARRAY ACCESS PATTERN TEST")
    print("=" * 30)
    
    # Create arrays
    spiral_array = create_spiral_array(400)
    linear_array = list(range(400))
    
    # Test access patterns
    spiral_times = []
    linear_times = []
    
    for _ in range(10):
        # Spiral array access
        start = time.perf_counter_ns()
        total = sum(spiral_array[i] for i in range(0, 400, 8))  # Sample access
        end = time.perf_counter_ns()
        spiral_times.append(end - start)
        
        # Linear array access  
        start = time.perf_counter_ns()
        total = sum(linear_array[i] for i in range(0, 400, 8))
        end = time.perf_counter_ns()
        linear_times.append(end - start)
    
    spiral_cv = statistics.stdev(spiral_times) / statistics.mean(spiral_times)
    linear_cv = statistics.stdev(linear_times) / statistics.mean(linear_times)
    
    print(f"Spiral Array Access CV: {spiral_cv:.4f}")
    print(f"Linear Array Access CV: {linear_cv:.4f}")
    print(f"Spiral/Linear CV Ratio: {spiral_cv/linear_cv:.3f}")
    
    return {
        'spiral_cv': spiral_cv,
        'linear_cv': linear_cv,
        'ratio': spiral_cv/linear_cv
    }

def main():
    print("🌲 DATA STRUCTURE GEOMETRY TEST")
    print("=" * 50)
    
    # Test 1: Search patterns
    search_results = test_search_patterns()
    
    print()
    
    # Test 2: Array access patterns
    access_results = test_array_access_patterns()
    
    # Analysis
    print(f"\n📊 DATA STRUCTURE GEOMETRY ANALYSIS:")
    print("=" * 50)
    
    print(f"Search Structure Geometry Ratio: {search_results['ratio']:.3f}")
    print(f"Array Access Geometry Ratio: {access_results['ratio']:.3f}")
    
    geometric_signatures = 0
    
    if search_results['ratio'] > 1.5:
        print("🔥 GEOMETRIC SEARCH SIGNATURE DETECTED!")
        geometric_signatures += 1
    elif search_results['ratio'] < 0.7:
        print("📊 LINEAR SEARCH ADVANTAGE")
    else:
        print("🤔 NO CLEAR SEARCH SIGNATURE")
    
    if access_results['ratio'] > 1.5:
        print("🔥 GEOMETRIC ACCESS SIGNATURE DETECTED!")
        geometric_signatures += 1
    elif access_results['ratio'] < 0.7:
        print("📊 LINEAR ACCESS ADVANTAGE")
    else:
        print("🤔 NO CLEAR ACCESS SIGNATURE")
    
    print(f"\n🎯 SUMMARY: {geometric_signatures}/2 geometric signatures detected")
    
    if geometric_signatures >= 1:
        print("✅ GEOMETRIC DATA STRUCTURE EFFECTS CONFIRMED!")
    else:
        print("❌ NO GEOMETRIC DATA STRUCTURE EFFECTS")

if __name__ == "__main__":
    main() 