#!/usr/bin/env python3
"""
Focused Testing: Cache vs Directory Structure Effects
Isolates the two strongest explanations for crystallographic timing patterns
"""

import os
import time
import json
import statistics
import subprocess
import tempfile
from pathlib import Path
import psutil

class FocusedTester:
    def __init__(self):
        self.results = {}
        self.base_path = Path('./focused_tests')
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
        """Attempt to clear filesystem cache"""
        try:
            subprocess.run(['sudo', 'purge'], check=True, capture_output=True)
            time.sleep(2)
            return True
        except:
            self.log("⚠️  Could not clear filesystem cache (no sudo)")
            return False
    
    def test_1_pure_cache_effect(self):
        """Test 1: Pure cache effect with flat structure"""
        self.log("🧪 Test 1: Pure Cache Effect (Flat Structure)")
        
        test_dir = self.base_path / 'pure_cache'
        test_dir.mkdir(exist_ok=True)
        
        # Create files in completely flat structure
        test_files = []
        for i in range(100):
            file_path = test_dir / f'flat_{i:03d}.dat'
            with open(file_path, 'wb') as f:
                f.write(b'CACHE_TEST' * 1000)  # ~10KB files
            test_files.append(file_path)
        
        results = {}
        
        # Test cold cache (if possible)
        if self.clear_filesystem_cache():
            cold_times = []
            for file_path in test_files[:20]:
                times = self.measure_access_time(file_path, 30)
                cold_times.extend(times)
            
            results['cold_flat'] = {
                'mean': statistics.mean(cold_times),
                'cv': statistics.stdev(cold_times) / statistics.mean(cold_times)
            }
            self.log(f"  Cold cache (flat): {results['cold_flat']['mean']:.2f} μs (CV: {results['cold_flat']['cv']:.3f})")
        
        # Test warm cache - access each file twice
        warm_times = []
        for file_path in test_files[:20]:
            # First access (to warm cache)
            with open(file_path, 'rb') as f:
                f.read()
            
            # Second access (measure warm cache)
            times = self.measure_access_time(file_path, 30)
            warm_times.extend(times)
        
        results['warm_flat'] = {
            'mean': statistics.mean(warm_times),
            'cv': statistics.stdev(warm_times) / statistics.mean(warm_times)
        }
        self.log(f"  Warm cache (flat): {results['warm_flat']['mean']:.2f} μs (CV: {results['warm_flat']['cv']:.3f})")
        
        self.results['pure_cache'] = results
        return results
    
    def test_2_pure_directory_effect(self):
        """Test 2: Pure directory structure effect with cold cache"""
        self.log("🧪 Test 2: Pure Directory Structure Effect")
        
        test_dir = self.base_path / 'pure_directory'
        test_dir.mkdir(exist_ok=True)
        
        # Create hierarchical structure matching original "crystallographic" layout
        hier_files = []
        for layer in range(8):  # 8 layers like original
            layer_dir = test_dir / f'layer_{layer}'
            layer_dir.mkdir(exist_ok=True)
            
            for i in range(12):  # 12 files per layer like original
                file_path = layer_dir / f'file_{i:03d}.dat'
                with open(file_path, 'wb') as f:
                    f.write(b'DIRECTORY_TEST' * 1000)  # ~14KB files
                hier_files.append(file_path)
        
        # Test with cold cache (clear before each measurement)
        if self.clear_filesystem_cache():
            cold_hier_times = []
            for file_path in hier_files[:20]:
                # Clear cache before each file
                subprocess.run(['sudo', 'purge'], capture_output=True)
                time.sleep(0.5)
                
                times = self.measure_access_time(file_path, 20)
                cold_hier_times.extend(times)
            
            result = {
                'mean': statistics.mean(cold_hier_times),
                'cv': statistics.stdev(cold_hier_times) / statistics.mean(cold_hier_times)
            }
            
            self.log(f"  Cold cache (hierarchical): {result['mean']:.2f} μs (CV: {result['cv']:.3f})")
            self.results['pure_directory'] = result
        else:
            self.log("  Could not test pure directory effect without cache clearing")
        
        return self.results.get('pure_directory', {})
    
    def test_3_combined_effect(self):
        """Test 3: Combined cache + directory structure (recreate original)"""
        self.log("🧪 Test 3: Combined Effect - Recreating Original Pattern")
        
        test_dir = self.base_path / 'combined_effect'
        test_dir.mkdir(exist_ok=True)
        
        # Create EXACT structure from original experiment
        crystal_files = []
        for layer in range(8):
            layer_dir = test_dir / f'layer_{layer}'
            layer_dir.mkdir(exist_ok=True)
            
            for i in range(12):
                file_path = layer_dir / f'crystal_{i:03d}.dat'
                with open(file_path, 'wb') as f:
                    # Use same content pattern as original
                    f.write(b'CRYSTAL_DATA' * 1000)
                crystal_files.append(file_path)
        
        # Access pattern: hierarchical navigation with warm cache
        combined_times = []
        
        # First pass: warm up the cache by accessing all files
        for file_path in crystal_files:
            with open(file_path, 'rb') as f:
                f.read()
        
        # Second pass: measure with warm cache + hierarchical structure
        for file_path in crystal_files[:24]:  # Test subset
            times = self.measure_access_time(file_path, 30)
            combined_times.extend(times)
        
        result = {
            'mean': statistics.mean(combined_times),
            'cv': statistics.stdev(combined_times) / statistics.mean(combined_times)
        }
        
        self.log(f"  Combined effect: {result['mean']:.2f} μs (CV: {result['cv']:.3f})")
        self.log(f"  {'🎯 MATCHES ORIGINAL!' if 0.130 <= result['cv'] <= 0.170 else '❌ Different from original'}")
        
        self.results['combined_effect'] = result
        return result
    
    def test_4_layer_by_layer_analysis(self):
        """Test 4: Analyze timing by directory layer"""
        self.log("🧪 Test 4: Layer-by-Layer Analysis")
        
        test_dir = self.base_path / 'layer_analysis'
        test_dir.mkdir(exist_ok=True)
        
        layer_results = {}
        
        for layer in range(8):
            layer_dir = test_dir / f'layer_{layer}'
            layer_dir.mkdir(exist_ok=True)
            
            # Create files in this layer
            layer_files = []
            for i in range(12):
                file_path = layer_dir / f'layer{layer}_file_{i:03d}.dat'
                with open(file_path, 'wb') as f:
                    f.write(b'LAYER_TEST' * 1000)
                layer_files.append(file_path)
            
            # Warm cache for this layer
            for file_path in layer_files:
                with open(file_path, 'rb') as f:
                    f.read()
            
            # Measure this layer
            layer_times = []
            for file_path in layer_files:
                times = self.measure_access_time(file_path, 25)
                layer_times.extend(times)
            
            layer_results[f'layer_{layer}'] = {
                'mean': statistics.mean(layer_times),
                'cv': statistics.stdev(layer_times) / statistics.mean(layer_times),
                'depth': layer
            }
            
            self.log(f"  Layer {layer}: {layer_results[f'layer_{layer}']['mean']:.2f} μs (CV: {layer_results[f'layer_{layer}']['cv']:.3f})")
        
        self.results['layer_analysis'] = layer_results
        return layer_results
    
    def test_5_access_pattern_variation(self):
        """Test 5: Different access patterns on same structure"""
        self.log("🧪 Test 5: Access Pattern Variations")
        
        test_dir = self.base_path / 'access_patterns'
        test_dir.mkdir(exist_ok=True)
        
        # Create hierarchical structure
        all_files = []
        for layer in range(8):
            layer_dir = test_dir / f'layer_{layer}'
            layer_dir.mkdir(exist_ok=True)
            
            for i in range(12):
                file_path = layer_dir / f'pattern_{i:03d}.dat'
                with open(file_path, 'wb') as f:
                    f.write(b'PATTERN_TEST' * 1000)
                all_files.append(file_path)
        
        patterns = {}
        
        # Pattern 1: Layer-by-layer (depth-first)
        depth_first_times = []
        for layer in range(8):
            layer_files = [f for f in all_files if f'layer_{layer}' in str(f)]
            for file_path in layer_files[:6]:  # 6 files per layer
                with open(file_path, 'rb') as f:
                    f.read()  # Warm cache
                times = self.measure_access_time(file_path, 20)
                depth_first_times.extend(times)
        
        patterns['depth_first'] = {
            'mean': statistics.mean(depth_first_times),
            'cv': statistics.stdev(depth_first_times) / statistics.mean(depth_first_times)
        }
        
        # Pattern 2: Breadth-first (file index across layers)
        breadth_first_times = []
        for file_idx in range(6):  # First 6 files from each layer
            for layer in range(8):
                layer_files = [f for f in all_files if f'layer_{layer}' in str(f)]
                if file_idx < len(layer_files):
                    file_path = layer_files[file_idx]
                    with open(file_path, 'rb') as f:
                        f.read()  # Warm cache
                    times = self.measure_access_time(file_path, 20)
                    breadth_first_times.extend(times)
        
        patterns['breadth_first'] = {
            'mean': statistics.mean(breadth_first_times),
            'cv': statistics.stdev(breadth_first_times) / statistics.mean(breadth_first_times)
        }
        
        for pattern_name, data in patterns.items():
            self.log(f"  {pattern_name}: {data['mean']:.2f} μs (CV: {data['cv']:.3f})")
        
        self.results['access_patterns'] = patterns
        return patterns
    
    def run_all_focused_tests(self):
        """Run all focused tests"""
        self.log("🔬 FOCUSED CRYSTALLOGRAPHIC INVESTIGATION")
        self.log("=" * 60)
        
        start_time = time.time()
        
        tests = [
            self.test_1_pure_cache_effect,
            self.test_2_pure_directory_effect,
            self.test_3_combined_effect,
            self.test_4_layer_by_layer_analysis,
            self.test_5_access_pattern_variation
        ]
        
        for i, test_func in enumerate(tests, 1):
            self.log(f"\n--- Running Focused Test {i}/5 ---")
            try:
                test_func()
            except Exception as e:
                self.log(f"❌ Test {i} failed: {e}")
        
        # Save results
        results_file = f'focused_explanations_{int(time.time())}.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        elapsed = time.time() - start_time
        self.log(f"\n✅ All focused tests completed in {elapsed:.1f} seconds")
        self.log(f"📊 Results saved to: {results_file}")
        
        return self.results
    
    def analyze_crystallographic_mechanism(self):
        """Determine the primary mechanism behind crystallographic periodicity"""
        self.log("\n🔍 CRYSTALLOGRAPHIC MECHANISM ANALYSIS")
        self.log("=" * 50)
        
        original_cv = 0.150  # Target CV from original experiment
        
        self.log(f"Target CV from original 'crystallographic' experiment: {original_cv:.3f}")
        self.log("\nCandidate explanations:")
        
        candidates = []
        
        for test_name, results in self.results.items():
            if isinstance(results, dict):
                for condition, data in results.items():
                    if isinstance(data, dict) and 'cv' in data:
                        cv = data['cv']
                        cv_diff = abs(cv - original_cv)
                        match_score = max(0, 1 - (cv_diff / 0.1))  # Score 0-1
                        
                        candidates.append({
                            'test': test_name,
                            'condition': condition,
                            'cv': cv,
                            'cv_diff': cv_diff,
                            'match_score': match_score
                        })
        
        # Sort by match score
        candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        self.log("\nRanked explanations (best to worst):")
        for i, candidate in enumerate(candidates[:10], 1):
            match_quality = "🎯 EXCELLENT" if candidate['match_score'] > 0.8 else \
                           "✅ GOOD" if candidate['match_score'] > 0.5 else \
                           "⚠️  WEAK" if candidate['match_score'] > 0.2 else "❌ POOR"
            
            self.log(f"{i:2d}. {candidate['test']}/{candidate['condition']}: "
                    f"CV = {candidate['cv']:.3f} "
                    f"(diff: {candidate['cv_diff']:.3f}) {match_quality}")
        
        # Determine primary mechanism
        if candidates:
            best = candidates[0]
            self.log(f"\n🏆 PRIMARY MECHANISM: {best['test']}/{best['condition']}")
            self.log(f"   CV match: {best['cv']:.3f} vs target {original_cv:.3f}")
            
            if best['match_score'] > 0.8:
                self.log("   ✅ CONFIRMED: This explains the crystallographic periodicity!")
            elif best['match_score'] > 0.5:
                self.log("   ⚠️  LIKELY: This probably explains the periodicity")
            else:
                self.log("   ❓ UNCERTAIN: No strong match found")

if __name__ == "__main__":
    tester = FocusedTester()
    results = tester.run_all_focused_tests()
    tester.analyze_crystallographic_mechanism() 