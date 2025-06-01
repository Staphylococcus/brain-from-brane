#!/usr/bin/env python3
"""
🔄 ALGORITHM GEOMETRIC SIGNATURES TEST
Test if geometric algorithms create different computational patterns than linear ones
"""

import time
import psutil
import threading
import math
import random
import statistics
from typing import List, Dict, Callable

class AlgorithmGeometryTester:
    def __init__(self):
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = False
    
    def monitor_system_resources(self):
        """Monitor CPU and memory usage during algorithm execution"""
        while self.monitoring:
            cpu_percent = psutil.cpu_percent(interval=0.01)
            memory_info = psutil.virtual_memory()
            self.cpu_samples.append(cpu_percent)
            self.memory_samples.append(memory_info.percent)
            time.sleep(0.01)
    
    def geometric_spiral_sort(self, data: List[int]) -> List[int]:
        """Sort using geometric spiral pattern"""
        n = len(data)
        if n <= 1:
            return data
        
        # Create spiral access pattern
        spiral_indices = []
        center = n // 2
        radius = 1
        
        while len(spiral_indices) < n:
            for angle in range(0, 360, 45):  # 8 directions
                x = center + int(radius * math.cos(math.radians(angle)))
                if 0 <= x < n and x not in spiral_indices:
                    spiral_indices.append(x)
            radius += 1
        
        # Sort using spiral pattern
        result = [0] * n
        sorted_data = sorted(data)
        
        for i, spiral_idx in enumerate(spiral_indices[:n]):
            if i < len(sorted_data):
                result[spiral_idx] = sorted_data[i]
        
        return result
    
    def crystallographic_matrix_multiply(self, a: List[List[int]], b: List[List[int]]) -> List[List[int]]:
        """Matrix multiplication using crystallographic access pattern"""
        n = len(a)
        result = [[0] * n for _ in range(n)]
        
        # 8-layer crystallographic access pattern
        for layer in range(8):
            layer_start = (layer * n) // 8
            layer_end = ((layer + 1) * n) // 8
            
            for i in range(layer_start, min(layer_end, n)):
                for j in range(n):
                    for k in range(n):
                        # Geometric access pattern within layer
                        access_pattern = (layer * 125 + i * j + k) % n
                        real_k = (k + access_pattern) % n
                        result[i][j] += a[i][real_k] * b[real_k][j]
        
        return result
    
    def linear_bubble_sort(self, data: List[int]) -> List[int]:
        """Standard linear bubble sort"""
        data = data.copy()
        n = len(data)
        for i in range(n):
            for j in range(0, n - i - 1):
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
        return data
    
    def linear_matrix_multiply(self, a: List[List[int]], b: List[List[int]]) -> List[List[int]]:
        """Standard linear matrix multiplication"""
        n = len(a)
        result = [[0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    result[i][j] += a[i][k] * b[k][j]
        
        return result
    
    def fractal_tree_sum(self, data: List[int], depth: int = 4) -> int:
        """Sum using fractal tree pattern"""
        if len(data) <= 1:
            return sum(data)
        
        if depth <= 0:
            return sum(data)
        
        # Split into fractal pattern
        mid = len(data) // 2
        quarter = len(data) // 4
        
        # Fractal subdivisions
        parts = [
            data[:quarter],
            data[quarter:mid],
            data[mid:mid+quarter],
            data[mid+quarter:]
        ]
        
        total = 0
        for part in parts:
            total += self.fractal_tree_sum(part, depth - 1)
        
        return total
    
    def measure_algorithm_signature(self, algorithm: Callable, args: tuple, name: str) -> Dict:
        """Measure computational signature of algorithm"""
        print(f"🔍 Testing {name} algorithm...")
        
        # Reset monitoring
        self.cpu_samples = []
        self.memory_samples = []
        
        # Start monitoring
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_system_resources)
        monitor_thread.start()
        
        # Run algorithm
        start_time = time.perf_counter_ns()
        result = algorithm(*args)
        end_time = time.perf_counter_ns()
        
        # Stop monitoring
        self.monitoring = False
        monitor_thread.join()
        
        # Calculate signatures
        execution_time = (end_time - start_time) / 1_000_000  # ms
        
        cpu_cv = statistics.stdev(self.cpu_samples) / statistics.mean(self.cpu_samples) if self.cpu_samples and statistics.mean(self.cpu_samples) > 0 else 0
        memory_cv = statistics.stdev(self.memory_samples) / statistics.mean(self.memory_samples) if self.memory_samples and statistics.mean(self.memory_samples) > 0 else 0
        
        return {
            'name': name,
            'execution_time_ms': execution_time,
            'cpu_mean': statistics.mean(self.cpu_samples) if self.cpu_samples else 0,
            'cpu_cv': cpu_cv,
            'memory_mean': statistics.mean(self.memory_samples) if self.memory_samples else 0,
            'memory_cv': memory_cv,
            'cpu_samples': len(self.cpu_samples),
            'result_size': len(str(result))
        }
    
    def run_geometry_comparison(self) -> Dict:
        """Run comparison between geometric and linear algorithms"""
        print("🧪 ALGORITHM GEOMETRIC SIGNATURES TEST")
        print("=" * 50)
        
        # Test data
        sort_data = [random.randint(1, 1000) for _ in range(100)]
        matrix_size = 20
        matrix_a = [[random.randint(1, 10) for _ in range(matrix_size)] for _ in range(matrix_size)]
        matrix_b = [[random.randint(1, 10) for _ in range(matrix_size)] for _ in range(matrix_size)]
        sum_data = [random.randint(1, 100) for _ in range(200)]
        
        results = {}
        
        # Test sorting algorithms
        results['geometric_sort'] = self.measure_algorithm_signature(
            self.geometric_spiral_sort, (sort_data,), "Geometric Spiral Sort"
        )
        
        results['linear_sort'] = self.measure_algorithm_signature(
            self.linear_bubble_sort, (sort_data,), "Linear Bubble Sort"
        )
        
        # Test matrix multiplication
        results['geometric_matrix'] = self.measure_algorithm_signature(
            self.crystallographic_matrix_multiply, (matrix_a, matrix_b), "Crystallographic Matrix Multiply"
        )
        
        results['linear_matrix'] = self.measure_algorithm_signature(
            self.linear_matrix_multiply, (matrix_a, matrix_b), "Linear Matrix Multiply"
        )
        
        # Test fractal vs linear summation
        results['fractal_sum'] = self.measure_algorithm_signature(
            self.fractal_tree_sum, (sum_data,), "Fractal Tree Sum"
        )
        
        results['linear_sum'] = self.measure_algorithm_signature(
            sum, (sum_data,), "Linear Sum"
        )
        
        # Analysis
        print(f"\n📊 ALGORITHM SIGNATURE ANALYSIS:")
        print("=" * 50)
        
        geometric_cpu_cvs = [results['geometric_sort']['cpu_cv'], results['geometric_matrix']['cpu_cv'], results['fractal_sum']['cpu_cv']]
        linear_cpu_cvs = [results['linear_sort']['cpu_cv'], results['linear_matrix']['cpu_cv'], results['linear_sum']['cpu_cv']]
        
        geometric_mean_cv = statistics.mean([cv for cv in geometric_cpu_cvs if cv > 0])
        linear_mean_cv = statistics.mean([cv for cv in linear_cpu_cvs if cv > 0])
        
        print(f"Geometric Algorithm Mean CPU CV: {geometric_mean_cv:.4f}")
        print(f"Linear Algorithm Mean CPU CV: {linear_mean_cv:.4f}")
        print(f"Geometric/Linear CV Ratio: {geometric_mean_cv/linear_mean_cv:.3f}" if linear_mean_cv > 0 else "Undefined")
        
        if geometric_mean_cv > linear_mean_cv * 1.2:
            print("🔥 GEOMETRIC SIGNATURE DETECTED: Geometric algorithms show more structured CPU patterns!")
        elif geometric_mean_cv < linear_mean_cv * 0.8:
            print("📊 INVERSE SIGNATURE: Linear algorithms more structured than geometric")
        else:
            print("🤔 NO CLEAR SIGNATURE: Similar computational patterns")
        
        results['analysis'] = {
            'geometric_mean_cv': geometric_mean_cv,
            'linear_mean_cv': linear_mean_cv,
            'cv_ratio': geometric_mean_cv/linear_mean_cv if linear_mean_cv > 0 else 0
        }
        
        return results

if __name__ == "__main__":
    tester = AlgorithmGeometryTester()
    results = tester.run_geometry_comparison() 