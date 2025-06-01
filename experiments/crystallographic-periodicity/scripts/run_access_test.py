#!/usr/bin/env python3
"""
SSD Crystallographic Experiment - Access Pattern Tester
Measures timing signatures for different access patterns on geometric file organizations
"""

import time
import random
import statistics
import json
import psutil
import os
from pathlib import Path
import argparse
from create_test_structures import get_file_lists

class AccessPatternTester:
    def __init__(self, base_path="ssd_crystal_test"):
        self.base_path = Path(base_path)
        self.file_lists = get_file_lists(base_path)
        self.results = {}
        
        # Clear filesystem cache before testing
        self.clear_caches()
    
    def clear_caches(self):
        """Clear filesystem caches for clean testing"""
        print("🧹 Clearing filesystem caches...")
        try:
            # Drop caches (Linux/Mac)
            if os.name == 'posix':
                os.system('sync')
                # Note: actual cache clearing requires sudo privileges
                # os.system('echo 3 > /proc/sys/vm/drop_caches')  # Linux only
        except:
            pass
    
    def measure_access_time(self, filepath):
        """Measure microsecond-precision file access time"""
        # Pre-read to ensure file is accessible
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
    
    def run_access_test(self, structure_type, access_pattern, num_files=100):
        """Run access timing test for specific structure/pattern combination"""
        print(f"🔬 Testing {structure_type} structure with {access_pattern} access...")
        
        file_list = self.file_lists[structure_type][:num_files]  # Limit for faster testing
        
        # Determine access order
        if access_pattern == 'geometric':
            access_order = self.geometric_access_order(structure_type, file_list)
        elif access_pattern == 'random':
            access_order = self.random_access_order(file_list)
        elif access_pattern == 'sequential':
            access_order = sorted(file_list)
        else:
            raise ValueError(f"Unknown access pattern: {access_pattern}")
        
        # Measure system resources before test
        cpu_before = psutil.cpu_percent()
        memory_before = psutil.virtual_memory().percent
        
        # Run access timing test
        access_times = []
        start_total = time.perf_counter()
        
        for filepath in access_order:
            access_time = self.measure_access_time(filepath)
            if access_time is not None:
                access_times.append(access_time)
        
        end_total = time.perf_counter()
        total_time = end_total - start_total
        
        # Measure system resources after test
        cpu_after = psutil.cpu_percent()
        memory_after = psutil.virtual_memory().percent
        
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
                'cpu_usage_change': cpu_after - cpu_before,
                'memory_usage_change': memory_after - memory_before,
                'access_times_raw': access_times  # For detailed analysis
            }
        else:
            stats = {'error': 'No successful file accesses'}
        
        test_key = f"{structure_type}_{access_pattern}"
        self.results[test_key] = stats
        
        print(f"  ✅ Mean access time: {stats.get('mean_access_time_us', 'N/A'):.2f} μs")
        print(f"  📊 Files processed: {stats.get('files_accessed', 0)}")
        print(f"  ⚡ Throughput: {stats.get('throughput_files_per_sec', 0):.2f} files/sec")
        
        return stats
    
    def detect_geometric_patterns(self, access_times, structure_type):
        """Analyze access times for geometric patterns"""
        if len(access_times) < 10:
            return {'pattern_detected': False, 'reason': 'insufficient_data'}
        
        patterns = {}
        
        # Look for periodic patterns
        if structure_type == 'crystallographic':
            # Check for 8-layer periodicity (our crystallographic structure has 8 layers)
            layer_size = len(access_times) // 8
            if layer_size > 1:
                layer_means = []
                for i in range(8):
                    start_idx = i * layer_size
                    end_idx = min((i + 1) * layer_size, len(access_times))
                    layer_mean = statistics.mean(access_times[start_idx:end_idx])
                    layer_means.append(layer_mean)
                
                patterns['layer_periodicity'] = {
                    'layer_means': layer_means,
                    'coefficient_of_variation': statistics.stdev(layer_means) / statistics.mean(layer_means)
                }
        
        # Look for fractal self-similarity
        elif structure_type == 'fractal':
            # Analyze variance at different scales
            scales = [10, 30, 100]
            scale_variances = []
            for scale in scales:
                if scale < len(access_times):
                    chunks = [access_times[i:i+scale] for i in range(0, len(access_times), scale)]
                    chunk_means = [statistics.mean(chunk) for chunk in chunks if len(chunk) == scale]
                    if len(chunk_means) > 1:
                        scale_variances.append(statistics.stdev(chunk_means))
            
            if len(scale_variances) > 1:
                patterns['fractal_scaling'] = {
                    'scale_variances': scale_variances,
                    'scaling_relationship': scale_variances
                }
        
        return patterns
    
    def run_full_test_suite(self, num_files=100):
        """Run complete test suite across all structure/pattern combinations"""
        print("🧪 RUNNING FULL SSD CRYSTALLOGRAPHIC TEST SUITE")
        print("=" * 60)
        
        structures = ['random', 'crystallographic', 'fractal', 'linear']
        patterns = ['geometric', 'random', 'sequential']
        
        total_tests = len(structures) * len(patterns)
        test_count = 0
        
        for structure in structures:
            print(f"\n📁 Testing {structure.upper()} structure:")
            
            for pattern in patterns:
                test_count += 1
                print(f"  [{test_count}/{total_tests}] {pattern} access pattern...")
                
                try:
                    self.run_access_test(structure, pattern, num_files)
                    time.sleep(1)  # Brief pause between tests
                except Exception as e:
                    print(f"    ❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("✅ FULL TEST SUITE COMPLETED")
        
        return self.analyze_results()
    
    def analyze_results(self):
        """Analyze results for geometric signatures"""
        print("\n🔍 ANALYZING GEOMETRIC SIGNATURES...")
        
        analysis = {
            'geometric_effects': {},
            'pattern_interference': {},
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
                performance_diff = (random_time - geometric_time) / random_time * 100
                
                analysis['geometric_effects'][structure] = {
                    'geometric_access_time': geometric_time,
                    'random_access_time': random_time,
                    'performance_advantage_percent': performance_diff,
                    'significant': abs(performance_diff) > 5  # 5% threshold
                }
                
                print(f"  📊 {structure.capitalize()}: {performance_diff:+.1f}% advantage for geometric access")
        
        # Look for cross-pattern interference
        for structure in ['crystallographic', 'fractal']:
            struct_results = {k: v for k, v in self.results.items() if k.startswith(structure)}
            if len(struct_results) >= 2:
                times = [v['mean_access_time_us'] for v in struct_results.values()]
                cv = statistics.stdev(times) / statistics.mean(times)
                analysis['pattern_interference'][structure] = {
                    'coefficient_of_variation': cv,
                    'high_interference': cv > 0.1  # 10% threshold
                }
        
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
            'raw_results': self.results,
            'analysis': self.analyze_results()
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Results saved to {filename}")
        return filename

def main():
    parser = argparse.ArgumentParser(description='SSD Crystallographic Access Test')
    parser.add_argument('--structure', choices=['random', 'crystallographic', 'fractal', 'linear'],
                        help='Test specific structure type')
    parser.add_argument('--pattern', choices=['geometric', 'random', 'sequential'],
                        help='Test specific access pattern')
    parser.add_argument('--files', type=int, default=100,
                        help='Number of files to test (default: 100)')
    parser.add_argument('--full-suite', action='store_true',
                        help='Run complete test suite')
    
    args = parser.parse_args()
    
    tester = AccessPatternTester()
    
    if args.full_suite:
        tester.run_full_test_suite(args.files)
        tester.save_results()
    elif args.structure and args.pattern:
        tester.run_access_test(args.structure, args.pattern, args.files)
        print("\n📊 Individual test completed")
    else:
        print("🤖 Usage: specify --full-suite OR both --structure and --pattern")
        print("Example: python run_access_test.py --structure crystallographic --pattern geometric")
        print("Example: python run_access_test.py --full-suite")

if __name__ == "__main__":
    main() 