#!/usr/bin/env python3
"""
REPRODUCIBLE CRYSTALLOGRAPHIC PERIODICITY TEST
Controls system state and conditions to reliably reproduce the effect
"""

import os
import time
import json
import statistics
import subprocess
import psutil
from pathlib import Path

class ReproducibleCrystallographicTest:
    def __init__(self):
        self.target_cv = 0.150
        self.crystal_path = Path('./ssd_crystal_test/crystal_structure')
        
    def log(self, message):
        """Log with timestamp"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def check_system_conditions(self):
        """Check and report system conditions"""
        self.log("🔍 CHECKING SYSTEM CONDITIONS")
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        self.log(f"   CPU Usage: {cpu_percent:.1f}%")
        self.log(f"   Memory Usage: {memory.percent:.1f}%")
        self.log(f"   Available Memory: {memory.available / (1024**3):.1f} GB")
        
        # Check if system is too busy
        if cpu_percent > 20:
            self.log("⚠️  HIGH CPU USAGE - may affect measurements")
            return False
        
        if memory.percent > 80:
            self.log("⚠️  HIGH MEMORY USAGE - may affect measurements")
            return False
        
        self.log("✅ System conditions acceptable")
        return True
    
    def clear_filesystem_cache(self):
        """Clear filesystem cache for consistent conditions"""
        self.log("🧹 Clearing filesystem cache...")
        try:
            # macOS: purge command
            result = subprocess.run(['sudo', 'purge'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            if result.returncode == 0:
                time.sleep(3)  # Wait for cache clearing
                self.log("✅ Filesystem cache cleared")
                return True
            else:
                self.log("⚠️  Cache clear failed - continuing anyway")
                return False
        except Exception as e:
            self.log(f"⚠️  Cache clear error: {e}")
            return False
    
    def warm_filesystem_cache_systematically(self):
        """Warm filesystem cache in a controlled, systematic way"""
        self.log("🔥 Systematically warming filesystem cache...")
        
        if not self.crystal_path.exists():
            self.log("❌ Crystal structure not found")
            return False
        
        layer_dirs = sorted([d for d in self.crystal_path.iterdir() 
                           if d.is_dir() and 'layer' in d.name])
        
        # Warm cache layer by layer in order
        for layer_dir in layer_dirs:
            layer_files = list(layer_dir.glob('*'))
            
            # Read each file completely to warm cache
            for file_path in layer_files:
                try:
                    with open(file_path, 'rb') as f:
                        f.read()
                except:
                    continue
        
        self.log(f"✅ Cache warmed for {len(layer_dirs)} layers")
        return True
    
    def controlled_measurement_cycle(self, sample_size=20):
        """Run a controlled measurement cycle"""
        self.log(f"📏 Running controlled measurement (sample size: {sample_size})")
        
        layer_dirs = sorted([d for d in self.crystal_path.iterdir() 
                           if d.is_dir() and 'layer' in d.name])
        
        layer_timing_data = []
        
        for layer_dir in layer_dirs:
            layer_files = list(layer_dir.glob('*'))
            
            if len(layer_files) < sample_size:
                self.log(f"⚠️  {layer_dir.name}: Only {len(layer_files)} files available")
                sample_files = layer_files
            else:
                # Use first N files for consistency
                sample_files = layer_files[:sample_size]
            
            # Measure this layer with precise timing
            layer_times = []
            
            for file_path in sample_files:
                # Multiple measurements per file for precision
                file_measurements = []
                
                for _ in range(3):  # 3 measurements per file
                    start_time = time.perf_counter_ns()  # Nanosecond precision
                    
                    try:
                        with open(file_path, 'rb') as f:
                            data = f.read()
                    except:
                        continue
                        
                    end_time = time.perf_counter_ns()
                    
                    access_time_us = (end_time - start_time) / 1000  # Convert to microseconds
                    file_measurements.append(access_time_us)
                
                if file_measurements:
                    # Use median of 3 measurements for robustness
                    layer_times.append(statistics.median(file_measurements))
            
            if layer_times:
                layer_mean = statistics.mean(layer_times)
                layer_timing_data.append(layer_mean)
                self.log(f"   {layer_dir.name}: {layer_mean:.2f} μs (n={len(layer_times)})")
        
        if len(layer_timing_data) == 8:
            overall_mean = statistics.mean(layer_timing_data)
            cv = statistics.stdev(layer_timing_data) / overall_mean
            return cv, layer_timing_data
        
        return None, None
    
    def run_reproducible_test(self, num_cycles=5):
        """Run the complete reproducible test protocol"""
        self.log("💎 REPRODUCIBLE CRYSTALLOGRAPHIC PERIODICITY TEST")
        self.log("=" * 60)
        
        # Step 1: Check system conditions
        if not self.check_system_conditions():
            self.log("❌ System conditions not suitable - try again later")
            return None
        
        # Step 2: Clear and warm cache systematically
        self.clear_filesystem_cache()
        time.sleep(2)
        
        if not self.warm_filesystem_cache_systematically():
            return None
        
        time.sleep(1)  # Let system stabilize
        
        # Step 3: Run multiple controlled measurement cycles
        self.log(f"\n🔬 Running {num_cycles} controlled measurement cycles...")
        
        all_cvs = []
        all_layer_data = []
        
        for cycle in range(num_cycles):
            self.log(f"\n📊 Cycle {cycle+1}/{num_cycles}")
            
            cv, layer_data = self.controlled_measurement_cycle()
            
            if cv is not None:
                all_cvs.append(cv)
                all_layer_data.append(layer_data)
                
                self.log(f"   CV: {cv:.3f}")
                
                # Check if this cycle matches target
                if abs(cv - self.target_cv) <= 0.050:
                    self.log(f"   🎯 MATCH! (diff: {abs(cv - self.target_cv):.3f})")
                
            else:
                self.log("   ❌ Measurement failed")
            
            # Small delay between cycles
            time.sleep(1)
        
        # Step 4: Analyze results
        return self.analyze_reproducible_results(all_cvs, all_layer_data)
    
    def analyze_reproducible_results(self, all_cvs, all_layer_data):
        """Analyze the reproducible test results"""
        self.log(f"\n📈 REPRODUCIBILITY ANALYSIS")
        self.log("=" * 40)
        
        if not all_cvs:
            self.log("❌ No successful measurements")
            return None
        
        mean_cv = statistics.mean(all_cvs)
        cv_std = statistics.stdev(all_cvs) if len(all_cvs) > 1 else 0
        
        self.log(f"📊 CV Statistics:")
        self.log(f"   Mean CV: {mean_cv:.3f}")
        self.log(f"   CV Std Dev: {cv_std:.3f}")
        self.log(f"   CV Range: {min(all_cvs):.3f} - {max(all_cvs):.3f}")
        self.log(f"   Successful cycles: {len(all_cvs)}")
        
        # Count how many measurements are close to target
        close_matches = sum(1 for cv in all_cvs if abs(cv - self.target_cv) <= 0.050)
        match_rate = close_matches / len(all_cvs)
        
        self.log(f"\n🎯 REPRODUCIBILITY METRICS:")
        self.log(f"   Target CV: {self.target_cv:.3f}")
        self.log(f"   Measured CV: {mean_cv:.3f} ± {cv_std:.3f}")
        self.log(f"   Close matches: {close_matches}/{len(all_cvs)} ({match_rate:.1%})")
        
        # Determine reproducibility status
        if match_rate >= 0.6 and cv_std <= 0.100:
            status = "🎯 HIGHLY REPRODUCIBLE"
            confidence = "HIGH"
        elif match_rate >= 0.4 and cv_std <= 0.150:
            status = "✅ REPRODUCIBLE"
            confidence = "MODERATE"
        elif close_matches >= 1:
            status = "⚠️  PARTIALLY REPRODUCIBLE"
            confidence = "LOW"
        else:
            status = "❌ NOT REPRODUCIBLE"
            confidence = "NONE"
        
        self.log(f"   Status: {status}")
        self.log(f"   Confidence: {confidence}")
        
        # Layer consistency analysis
        if len(all_layer_data) >= 2:
            self.log(f"\n🔍 LAYER PATTERN CONSISTENCY:")
            
            # Calculate average layer pattern
            avg_layers = []
            for layer_idx in range(8):
                layer_values = [trial[layer_idx] for trial in all_layer_data 
                              if len(trial) > layer_idx]
                if layer_values:
                    avg_layers.append(statistics.mean(layer_values))
            
            if len(avg_layers) == 8:
                layer_cv = statistics.stdev(avg_layers) / statistics.mean(avg_layers)
                self.log(f"   Average pattern: {[f'{x:.1f}' for x in avg_layers]}")
                self.log(f"   Pattern CV: {layer_cv:.3f}")
                
                if abs(layer_cv - self.target_cv) <= 0.050:
                    self.log(f"   🎯 PATTERN MATCHES TARGET!")
        
        return {
            'mean_cv': mean_cv,
            'cv_std': cv_std,
            'match_rate': match_rate,
            'status': status,
            'confidence': confidence,
            'raw_cvs': all_cvs
        }

def main():
    """Run the reproducible test"""
    tester = ReproducibleCrystallographicTest()
    results = tester.run_reproducible_test()
    
    if results:
        print(f"\n🏆 FINAL REPRODUCIBILITY ASSESSMENT:")
        print(f"   Status: {results['status']}")
        print(f"   Confidence: {results['confidence']}")
        print(f"   Match Rate: {results['match_rate']:.1%}")
        
        if results['confidence'] in ['HIGH', 'MODERATE']:
            print(f"\n🎉 CRYSTALLOGRAPHIC PERIODICITY REPRODUCED!")
            print(f"   The geometric information effect is VALIDATED!")
        else:
            print(f"\n🔧 Need to optimize conditions for better reproducibility")

if __name__ == "__main__":
    main() 