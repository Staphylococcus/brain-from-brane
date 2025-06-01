#!/usr/bin/env python3
"""
🧠 MEMORY ACCESS CRYSTALLOGRAPHY TEST
Test if geometric memory allocation creates timing signatures
"""

import time
import random
import statistics
from typing import List, Dict

class MemoryGeometryTester:
    def __init__(self, block_size=1024, num_blocks=1000):
        self.block_size = block_size
        self.num_blocks = num_blocks
        self.allocated_blocks = []
    
    def allocate_crystallographic_pattern(self) -> List[bytearray]:
        """Allocate memory in 8-layer crystallographic pattern"""
        print("🔷 Allocating memory in crystallographic pattern...")
        blocks = []
        
        # 8 layers, systematic allocation
        for layer in range(8):
            layer_blocks = []
            for unit in range(self.num_blocks // 8):
                # Create block with geometric pattern
                block = bytearray(self.block_size)
                # Fill with layer-specific pattern
                for i in range(0, self.block_size, 8):
                    block[i:i+8] = (layer * 125 + unit).to_bytes(8, 'little')
                layer_blocks.append(block)
            blocks.extend(layer_blocks)
        
        return blocks
    
    def allocate_random_pattern(self) -> List[bytearray]:
        """Allocate memory in random pattern"""
        print("🎲 Allocating memory in random pattern...")
        blocks = []
        
        for i in range(self.num_blocks):
            block = bytearray(self.block_size)
            # Fill with random data
            for j in range(0, self.block_size, 8):
                block[j:j+8] = random.randint(0, 2**64-1).to_bytes(8, 'little')
            blocks.append(block)
        
        return blocks
    
    def measure_access_timing(self, blocks: List[bytearray], pattern: str) -> Dict:
        """Measure memory access timing patterns"""
        print(f"⏱️ Measuring {pattern} access timing...")
        
        # Warm up
        for _ in range(100):
            random.choice(blocks)[random.randint(0, self.block_size-8):random.randint(0, self.block_size-8)+8]
        
        # Measure systematic access
        systematic_times = []
        for i in range(len(blocks)):
            start = time.perf_counter_ns()
            # Read specific pattern from block
            data = blocks[i][0:8]
            end = time.perf_counter_ns()
            systematic_times.append(end - start)
        
        # Measure random access  
        random_times = []
        indices = list(range(len(blocks)))
        random.shuffle(indices)
        for i in indices:
            start = time.perf_counter_ns()
            data = blocks[i][random.randint(0, self.block_size-8):random.randint(0, self.block_size-8)+8]
            end = time.perf_counter_ns()
            random_times.append(end - start)
        
        return {
            'systematic_mean': statistics.mean(systematic_times),
            'systematic_std': statistics.stdev(systematic_times) if len(systematic_times) > 1 else 0,
            'random_mean': statistics.mean(random_times),
            'random_std': statistics.stdev(random_times) if len(random_times) > 1 else 0,
            'systematic_times': systematic_times,
            'random_times': random_times,
            'pattern': pattern
        }
    
    def calculate_geometric_signature(self, timings: List[float]) -> float:
        """Calculate coefficient of variation as geometric signature"""
        if len(timings) < 2:
            return 0
        mean_time = statistics.mean(timings)
        if mean_time == 0:
            return 0
        std_time = statistics.stdev(timings)
        return std_time / mean_time
    
    def run_full_test(self) -> Dict:
        """Run complete memory geometry test"""
        print("🧪 MEMORY ACCESS CRYSTALLOGRAPHY TEST")
        print("=" * 50)
        
        # Test crystallographic allocation
        crystal_blocks = self.allocate_crystallographic_pattern()
        crystal_results = self.measure_access_timing(crystal_blocks, "crystallographic")
        crystal_cv = self.calculate_geometric_signature(crystal_results['systematic_times'])
        
        # Clean up
        del crystal_blocks
        
        # Test random allocation
        random_blocks = self.allocate_random_pattern() 
        random_results = self.measure_access_timing(random_blocks, "random")
        random_cv = self.calculate_geometric_signature(random_results['systematic_times'])
        
        # Clean up
        del random_blocks
        
        # Analysis
        crystal_advantage = ((random_results['systematic_mean'] - crystal_results['systematic_mean']) / 
                           random_results['systematic_mean']) * 100
        
        print(f"\n📊 MEMORY GEOMETRY RESULTS:")
        print(f"Crystallographic CV: {crystal_cv:.4f}")
        print(f"Random CV: {random_cv:.4f}")
        print(f"CV Ratio: {crystal_cv/random_cv:.3f}" if random_cv > 0 else "CV Ratio: undefined")
        print(f"Speed advantage: {crystal_advantage:.1f}%")
        
        if crystal_cv > random_cv * 1.1:
            print("🔥 GEOMETRIC SIGNATURE DETECTED: Crystallographic allocation shows structured timing!")
        elif abs(crystal_cv - random_cv) < 0.01:
            print("🤔 NO CLEAR SIGNATURE: Similar timing patterns")
        else:
            print("❌ NO GEOMETRIC SIGNATURE: Random allocation more structured")
        
        return {
            'crystallographic': crystal_results,
            'random': random_results,
            'crystal_cv': crystal_cv,
            'random_cv': random_cv,
            'speed_advantage_percent': crystal_advantage
        }

if __name__ == "__main__":
    tester = MemoryGeometryTester(block_size=1024, num_blocks=800)
    results = tester.run_full_test() 