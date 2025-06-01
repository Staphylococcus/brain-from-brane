#!/usr/bin/env python3
"""
SSD Crystallographic Experiment - Simple Access Pattern Tester
Measures timing signatures for different access patterns (no external dependencies)
"""

import time
import random
import statistics
import json
import os
from pathlib import Path
import argparse
from create_test_structures import get_file_lists

class SimpleAccessTester:
    def __init__(self, base_path="ssd_crystal_test"):
        self.base_path = Path(base_path)
        self.file_lists = get_file_lists(base_path)
        self.results = {}
        print(f"🔬 Initialized tester with {len(self.file_lists)} structures")
    
    def measure_access_time(self, filepath):
        """Measure microsecond-precision file access time"""
        try:
            start_time = time.perf_counter()
            with open(filepath, 'rb') as f:
                _ = f.read(1024)  # Read first 1KB for timing
            end_time = time.perf_counter()
            
            return (end_time - start_time) * 1_000_000  # Convert to microseconds
        except Exception as e:
            print(f"⚠️  Error reading {filepath}: {e}")
            return None
    
    def geometric_access_order(self, structure_type, file_list):
        """Generate geometric access order based on structure type"""
        if structure_type == 'crystallographic':
            # Access in crystallographic lattice order (layer by layer)
            return file_list  # Already organized by creation function
        elif structure_type == 'fractal':
            # Access in fractal depth-first order
            return file_list  # Already organized by creation function
        elif structure_type == 'linear':
            # Access in sequential order
            return sorted(file_list)
        elif structure_type == 'random':
            # For random, "geometric" order is just sorted
            return sorted(file_list)
    
    def random_access_order(self, file_list):
        """Generate random access order"""
        random_list = list(file_list)
        random.shuffle(random_list)
        return random_list
    
    def run_access_test(self, structure_type, access_pattern, num_files=50):
        """Run access timing test for specific structure/pattern combination"""
        print(f"\n🔬 Testing {structure_type} structure with {access_pattern} access...")
        
        file_list = list(self.file_lists[structure_type])[:num_files]  # Limit for faster testing
        print(f"  📁 Testing {len(file_list)} files")
        
        # Determine access order
        if access_pattern == 'geometric':
            access_order = self.geometric_access_order(structure_type, file_list)
        elif access_pattern == 'random':
            access_order = self.random_access_order(file_list)
        elif access_pattern == 'sequential':
            access_order = sorted(file_list)
        else:
            raise ValueError(f"Unknown access pattern: {access_pattern}")
        
        # Run access timing test
        access_times = []
        start_total = time.perf_counter()
        
        for i, filepath in enumerate(access_order):
            if i % 10 == 0:
                print(f"  📊 Progress: {i}/{len(access_order)} files...")
            
            access_time = self.measure_access_time(filepath)
            if access_time is not None:
                access_times.append(access_time)
        
        end_total = time.perf_counter()
        total_time = end_total - start_total
        
        # Calculate statistics
        if access_times:
            stats = {
                'mean_access_time_us': statistics.mean(access_times),
                'median_access_time_us': statistics.median(access_times),
                'stdev_access_time_us': statistics.stdev(access_times) if len(access_times) > 1 else 0,
                'min_access_time_us': min(access_times),
                'max_access_time_us': max(access_times),
                'total_time_sec': total_time,
                'files_accessed': len(access_times),
                'throughput_files_per_sec': len(access_times) / total_time,
                'access_times_raw': access_times  # For detailed analysis
            }
        else:
            stats = {'error': 'No successful file accesses'}
        
        test_key = f"{structure_type}_{access_pattern}"
        self.results[test_key] = stats
        
        print(f"  ✅ Mean access time: {stats.get('mean_access_time_us', 'N/A'):.2f} μs")
        print(f"  📊 Files processed: {stats.get('files_accessed', 0)}")
        print(f"  ⚡ Throughput: {stats.get('throughput_files_per_sec', 0):.2f} files/sec")
        print(f"  🎯 Std deviation: {stats.get('stdev_access_time_us', 0):.2f} μs")
        
        return stats
    
    def analyze_geometric_effects(self):
        """Analyze results for geometric signatures"""
        print("\n🔍 ANALYZING GEOMETRIC SIGNATURES...")
        print("=" * 50)
        
        analysis = {
            'geometric_effects': {},
            'structure_efficiency': {}
        }
        
        # Look for geometric access advantages
        for structure in ['crystallographic', 'fractal', 'linear']:
            geometric_key = f"{structure}_geometric"
            random_key = f"{structure}_random"
            
            if geometric_key in self.results and random_key in self.results:
                geometric_time = self.results[geometric_key]['mean_access_time_us']
                random_time = self.results[random_key]['mean_access_time_us']
                
                # Calculate performance difference
                if random_time > 0:
                    performance_diff = (random_time - geometric_time) / random_time * 100
                    
                    analysis['geometric_effects'][structure] = {
                        'geometric_access_time': geometric_time,
                        'random_access_time': random_time,
                        'performance_advantage_percent': performance_diff,
                        'significant': abs(performance_diff) > 5  # 5% threshold
                    }
                    
                    significance = "🔥 SIGNIFICANT" if abs(performance_diff) > 5 else "📊 modest"
                    print(f"  {structure.capitalize():>15}: {performance_diff:+6.1f}% geometric advantage ({significance})")
        
        # Look for crystallographic periodicity
        if 'crystallographic_geometric' in self.results:
            crystal_times = self.results['crystallographic_geometric']['access_times_raw']
            if len(crystal_times) >= 40:  # Need enough data for 8-layer analysis
                layer_size = len(crystal_times) // 8
                layer_means = []
                for i in range(8):
                    start_idx = i * layer_size
                    end_idx = min((i + 1) * layer_size, len(crystal_times))
                    if end_idx > start_idx:
                        layer_mean = statistics.mean(crystal_times[start_idx:end_idx])
                        layer_means.append(layer_mean)
                
                if len(layer_means) >= 8:
                    cv = statistics.stdev(layer_means) / statistics.mean(layer_means)
                    analysis['crystallographic_periodicity'] = {
                        'layer_means': layer_means,
                        'coefficient_of_variation': cv,
                        'periodic_structure': cv < 0.2  # Low variation suggests periodicity
                    }
                    print(f"  Crystallographic periodicity: CV = {cv:.3f} ({'DETECTED' if cv < 0.2 else 'not detected'})")
        
        return analysis
    
    def run_quick_test(self):
        """Run a quick test of key predictions"""
        print("🧪 RUNNING QUICK CRYSTALLOGRAPHIC TEST")
        print("=" * 50)
        
        # Test crystallographic structure first (our key prediction)
        self.run_access_test('crystallographic', 'geometric', 50)
        self.run_access_test('crystallographic', 'random', 50)
        
        # Test random structure as control
        self.run_access_test('random', 'geometric', 50)
        self.run_access_test('random', 'random', 50)
        
        # Analyze results
        analysis = self.analyze_geometric_effects()
        
        print("\n🎯 QUICK TEST RESULTS:")
        print("=" * 50)
        
        # Check key prediction: crystallographic geometric advantage
        if 'crystallographic' in analysis.get('geometric_effects', {}):
            crystal_effect = analysis['geometric_effects']['crystallographic']
            advantage = crystal_effect['performance_advantage_percent']
            
            if advantage > 15:
                print(f"🔥 STRONG EVIDENCE: {advantage:.1f}% crystallographic advantage!")
                print("   This supports geometric information theory!")
            elif advantage > 5:
                print(f"📊 MODERATE EVIDENCE: {advantage:.1f}% crystallographic advantage")
                print("   Suggests geometric effects may be real")
            elif advantage > -5:
                print(f"🤔 MINIMAL EFFECT: {advantage:.1f}% difference")
                print("   No clear evidence for geometric properties")
            else:
                print(f"❌ NEGATIVE RESULT: {advantage:.1f}% disadvantage")
                print("   This challenges geometric information theory")
        
        return analysis
    
    def save_results(self, filename=None):
        """Save detailed results to JSON file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"ssd_crystal_results_{timestamp}.json"
        
        output = {
            'timestamp': time.time(),
            'test_configuration': {
                'base_path': str(self.base_path),
                'structures_tested': list(self.file_lists.keys())
            },
            'raw_results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Results saved to {filename}")
        return filename

def main():
    parser = argparse.ArgumentParser(description='Simple SSD Crystallographic Test')
    parser.add_argument('--structure', choices=['random', 'crystallographic', 'fractal', 'linear'],
                        help='Test specific structure type')
    parser.add_argument('--pattern', choices=['geometric', 'random', 'sequential'],
                        help='Test specific access pattern')
    parser.add_argument('--files', type=int, default=50,
                        help='Number of files to test (default: 50)')
    parser.add_argument('--quick', action='store_true',
                        help='Run quick test of key predictions')
    
    args = parser.parse_args()
    
    tester = SimpleAccessTester()
    
    if args.quick:
        tester.run_quick_test()
        tester.save_results()
    elif args.structure and args.pattern:
        tester.run_access_test(args.structure, args.pattern, args.files)
        print("\n📊 Individual test completed")
    else:
        print("🤖 Usage examples:")
        print("  python run_access_test_simple.py --quick")
        print("  python run_access_test_simple.py --structure crystallographic --pattern geometric")

if __name__ == "__main__":
    main() 