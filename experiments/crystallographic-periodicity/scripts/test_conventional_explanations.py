#!/usr/bin/env python3
"""
Systematic Testing of Conventional Explanations
Tests each proposed conventional explanation for the observed timing patterns
"""

import os
import time
import json
import statistics
import subprocess
import tempfile
from pathlib import Path
import psutil

class ConventionalExplanationTester:
    def __init__(self):
        self.results = {}
        self.base_path = Path('./conventional_tests')
        self.base_path.mkdir(exist_ok=True)
        
    def log(self, message):
        """Log with timestamp"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def measure_access_time(self, file_path, iterations=50):
        """Measure file access time with high precision"""
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            with open(file_path, 'rb') as f:
                data = f.read(1024)  # Read first 1KB
            end = time.perf_counter()
            times.append((end - start) * 1_000_000)  # Convert to microseconds
        return times
    
    def clear_filesystem_cache(self):
        """Attempt to clear filesystem cache (may require sudo)"""
        try:
            # macOS: purge command
            subprocess.run(['sudo', 'purge'], check=True, capture_output=True)
            time.sleep(2)  # Wait for cache clearing
            return True
        except:
            self.log("⚠️  Could not clear filesystem cache (no sudo)")
            return False
    
    def get_system_state(self):
        """Get current system performance state"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
            'load_average': os.getloadavg()
        }
    
    def test_1_filesystem_block_effects(self):
        """Test 1: Filesystem Block Structure Effects"""
        self.log("🧪 Test 1: Filesystem Block Structure Effects")
        
        test_dir = self.base_path / 'block_test'
        test_dir.mkdir(exist_ok=True)
        
        # Create files at different block boundaries
        block_sizes = [4096, 8192, 16384]  # Common block sizes
        results = {}
        
        for block_size in block_sizes:
            block_dir = test_dir / f'block_{block_size}'
            block_dir.mkdir(exist_ok=True)
            
            # Create files aligned to block boundaries
            aligned_files = []
            for i in range(100):
                file_path = block_dir / f'aligned_{i:03d}.dat'
                # Write exactly block_size bytes
                with open(file_path, 'wb') as f:
                    f.write(b'X' * block_size)
                aligned_files.append(file_path)
            
            # Measure access times
            all_times = []
            for file_path in aligned_files[:20]:  # Test subset
                times = self.measure_access_time(file_path, 30)
                all_times.extend(times)
            
            results[f'block_{block_size}'] = {
                'mean': statistics.mean(all_times),
                'stdev': statistics.stdev(all_times),
                'cv': statistics.stdev(all_times) / statistics.mean(all_times)
            }
            
            self.log(f"  Block {block_size}: {statistics.mean(all_times):.2f} μs (CV: {results[f'block_{block_size}']['cv']:.3f})")
        
        self.results['filesystem_blocks'] = results
        return results
    
    def test_2_cache_effects(self):
        """Test 2: Filesystem Cache Effects"""
        self.log("🧪 Test 2: Filesystem Cache Effects")
        
        test_dir = self.base_path / 'cache_test'
        test_dir.mkdir(exist_ok=True)
        
        # Create test files
        test_files = []
        for i in range(50):
            file_path = test_dir / f'cache_test_{i:03d}.dat'
            with open(file_path, 'wb') as f:
                f.write(b'TEST_DATA' * 1000)  # 9KB files
            test_files.append(file_path)
        
        results = {}
        
        # Test 1: Cold cache (after clearing)
        if self.clear_filesystem_cache():
            cold_times = []
            for file_path in test_files[:10]:
                times = self.measure_access_time(file_path, 20)
                cold_times.extend(times)
            
            results['cold_cache'] = {
                'mean': statistics.mean(cold_times),
                'cv': statistics.stdev(cold_times) / statistics.mean(cold_times)
            }
            self.log(f"  Cold cache: {statistics.mean(cold_times):.2f} μs (CV: {results['cold_cache']['cv']:.3f})")
        
        # Test 2: Warm cache (immediate re-access)
        warm_times = []
        for file_path in test_files[:10]:
            # Access once to warm cache
            with open(file_path, 'rb') as f:
                f.read()
            
            # Then measure
            times = self.measure_access_time(file_path, 20)
            warm_times.extend(times)
        
        results['warm_cache'] = {
            'mean': statistics.mean(warm_times),
            'cv': statistics.stdev(warm_times) / statistics.mean(warm_times)
        }
        self.log(f"  Warm cache: {statistics.mean(warm_times):.2f} μs (CV: {results['warm_cache']['cv']:.3f})")
        
        self.results['cache_effects'] = results
        return results
    
    def test_3_sequential_vs_random_access(self):
        """Test 3: Sequential vs Random Access Patterns"""
        self.log("🧪 Test 3: Sequential vs Random Access Patterns")
        
        test_dir = self.base_path / 'access_pattern_test'
        test_dir.mkdir(exist_ok=True)
        
        # Create files in flat directory (no hierarchical organization)
        test_files = []
        for i in range(200):
            file_path = test_dir / f'flat_{i:03d}.dat'
            with open(file_path, 'wb') as f:
                f.write(b'DATA_CONTENT' * 800)  # ~9.6KB files
            test_files.append(file_path)
        
        results = {}
        
        # Sequential access pattern
        sequential_times = []
        for file_path in test_files[:50]:  # Access in order
            times = self.measure_access_time(file_path, 20)
            sequential_times.extend(times)
        
        results['sequential'] = {
            'mean': statistics.mean(sequential_times),
            'cv': statistics.stdev(sequential_times) / statistics.mean(sequential_times)
        }
        
        # Random access pattern (same files, different order)
        import random
        random_order = test_files[:50].copy()
        random.shuffle(random_order)
        
        random_times = []
        for file_path in random_order:
            times = self.measure_access_time(file_path, 20)
            random_times.extend(times)
        
        results['random'] = {
            'mean': statistics.mean(random_times),
            'cv': statistics.stdev(random_times) / statistics.mean(random_times)
        }
        
        self.log(f"  Sequential: {results['sequential']['mean']:.2f} μs (CV: {results['sequential']['cv']:.3f})")
        self.log(f"  Random:     {results['random']['mean']:.2f} μs (CV: {results['random']['cv']:.3f})")
        
        self.results['access_patterns'] = results
        return results
    
    def test_4_directory_metadata_effects(self):
        """Test 4: Directory Structure vs Flat Organization"""
        self.log("🧪 Test 4: Directory Metadata Effects")
        
        base_test_dir = self.base_path / 'directory_test'
        base_test_dir.mkdir(exist_ok=True)
        
        results = {}
        
        # Flat organization
        flat_dir = base_test_dir / 'flat'
        flat_dir.mkdir(exist_ok=True)
        
        flat_files = []
        for i in range(100):
            file_path = flat_dir / f'file_{i:03d}.dat'
            with open(file_path, 'wb') as f:
                f.write(b'FLAT_DATA' * 1000)
            flat_files.append(file_path)
        
        flat_times = []
        for file_path in flat_files[:20]:
            times = self.measure_access_time(file_path, 25)
            flat_times.extend(times)
        
        results['flat'] = {
            'mean': statistics.mean(flat_times),
            'cv': statistics.stdev(flat_times) / statistics.mean(flat_times)
        }
        
        # Hierarchical organization (exactly matching our "crystallographic" structure)
        hier_dir = base_test_dir / 'hierarchical'
        hier_dir.mkdir(exist_ok=True)
        
        hier_files = []
        for layer in range(8):
            layer_dir = hier_dir / f'layer_{layer}'
            layer_dir.mkdir(exist_ok=True)
            
            for i in range(12):  # 12 files per layer like our original
                file_path = layer_dir / f'file_{i:03d}.dat'
                with open(file_path, 'wb') as f:
                    f.write(b'HIER_DATA' * 1000)
                hier_files.append(file_path)
        
        hier_times = []
        for file_path in hier_files[:20]:
            times = self.measure_access_time(file_path, 25)
            hier_times.extend(times)
        
        results['hierarchical'] = {
            'mean': statistics.mean(hier_times),
            'cv': statistics.stdev(hier_times) / statistics.mean(hier_times)
        }
        
        self.log(f"  Flat:         {results['flat']['mean']:.2f} μs (CV: {results['flat']['cv']:.3f})")
        self.log(f"  Hierarchical: {results['hierarchical']['mean']:.2f} μs (CV: {results['hierarchical']['cv']:.3f})")
        
        self.results['directory_structure'] = results
        return results
    
    def test_5_system_state_effects(self):
        """Test 5: System State and Background Process Effects"""
        self.log("🧪 Test 5: System State Effects")
        
        test_dir = self.base_path / 'system_state_test'
        test_dir.mkdir(exist_ok=True)
        
        # Create test file
        test_file = test_dir / 'system_test.dat'
        with open(test_file, 'wb') as f:
            f.write(b'SYSTEM_TEST' * 2000)
        
        results = {}
        
        # Measure under different system load conditions
        for condition in ['idle', 'loaded']:
            if condition == 'loaded':
                # Create artificial load
                self.log("  Creating artificial system load...")
                import threading
                
                def cpu_load():
                    end_time = time.time() + 10
                    while time.time() < end_time:
                        pass  # Busy wait
                
                # Start load threads
                load_threads = []
                for _ in range(2):  # 2 CPU cores worth of load
                    t = threading.Thread(target=cpu_load)
                    t.start()
                    load_threads.append(t)
                
                time.sleep(1)  # Let load stabilize
            
            # Record system state
            sys_state = self.get_system_state()
            
            # Measure access times
            times = self.measure_access_time(test_file, 100)
            
            results[condition] = {
                'mean': statistics.mean(times),
                'cv': statistics.stdev(times) / statistics.mean(times),
                'system_state': sys_state
            }
            
            self.log(f"  {condition.capitalize()}: {statistics.mean(times):.2f} μs (CV: {results[condition]['cv']:.3f})")
            self.log(f"    CPU: {sys_state['cpu_percent']:.1f}%, Memory: {sys_state['memory_percent']:.1f}%")
            
            if condition == 'loaded':
                # Wait for load threads to finish
                for t in load_threads:
                    t.join()
        
        self.results['system_state'] = results
        return results
    
    def test_6_storage_device_effects(self):
        """Test 6: Storage Device Characteristics"""
        self.log("🧪 Test 6: Storage Device Effects")
        
        # Get storage device info
        disk_info = psutil.disk_usage('/')
        
        results = {
            'device_info': {
                'total_gb': disk_info.total / (1024**3),
                'free_gb': disk_info.free / (1024**3),
                'used_percent': (disk_info.used / disk_info.total) * 100
            }
        }
        
        # Test access patterns on different areas of disk
        test_dir = self.base_path / 'storage_test'
        test_dir.mkdir(exist_ok=True)
        
        # Create files of different sizes to test SSD controller behavior
        file_sizes = [1024, 4096, 16384, 65536]  # 1KB to 64KB
        
        for size in file_sizes:
            size_times = []
            for i in range(20):
                file_path = test_dir / f'size_{size}_{i:03d}.dat'
                with open(file_path, 'wb') as f:
                    f.write(b'X' * size)
                
                times = self.measure_access_time(file_path, 30)
                size_times.extend(times)
            
            results[f'size_{size}'] = {
                'mean': statistics.mean(size_times),
                'cv': statistics.stdev(size_times) / statistics.mean(size_times)
            }
            
            self.log(f"  {size:5d} bytes: {statistics.mean(size_times):.2f} μs (CV: {results[f'size_{size}']['cv']:.3f})")
        
        self.results['storage_device'] = results
        return results
    
    def run_all_tests(self):
        """Run all conventional explanation tests"""
        self.log("🔬 SYSTEMATIC CONVENTIONAL EXPLANATION TESTING")
        self.log("=" * 60)
        
        start_time = time.time()
        
        # Run each test
        tests = [
            self.test_1_filesystem_block_effects,
            self.test_2_cache_effects,
            self.test_3_sequential_vs_random_access,
            self.test_4_directory_metadata_effects,
            self.test_5_system_state_effects,
            self.test_6_storage_device_effects
        ]
        
        for i, test_func in enumerate(tests, 1):
            self.log(f"\n--- Running Test {i}/6 ---")
            try:
                test_func()
            except Exception as e:
                self.log(f"❌ Test {i} failed: {e}")
        
        # Save results
        results_file = f'conventional_explanations_{int(time.time())}.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        elapsed = time.time() - start_time
        self.log(f"\n✅ All tests completed in {elapsed:.1f} seconds")
        self.log(f"📊 Results saved to: {results_file}")
        
        return self.results
    
    def analyze_results(self):
        """Analyze which conventional explanations explain the observed patterns"""
        self.log("\n📈 CONVENTIONAL EXPLANATION ANALYSIS")
        self.log("=" * 50)
        
        # Compare each test to our original "crystallographic" findings
        original_cv = 0.150  # Our original "crystallographic periodicity"
        
        for test_name, test_results in self.results.items():
            self.log(f"\n{test_name.upper()}:")
            
            if isinstance(test_results, dict):
                for condition, data in test_results.items():
                    if isinstance(data, dict) and 'cv' in data:
                        cv = data['cv']
                        cv_diff = abs(cv - original_cv)
                        match_quality = "STRONG" if cv_diff < 0.05 else "WEAK" if cv_diff < 0.1 else "NO"
                        
                        self.log(f"  {condition}: CV = {cv:.3f} ({match_quality} match to original)")

if __name__ == "__main__":
    tester = ConventionalExplanationTester()
    results = tester.run_all_tests()
    tester.analyze_results() 