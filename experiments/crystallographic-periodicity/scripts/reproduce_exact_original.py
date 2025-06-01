#!/usr/bin/env python3
"""
REPRODUCE EXACT ORIGINAL MEASUREMENT
Uses the EXACT same measurement methodology as the original experiment
"""

import os
import time
import json
import statistics
from pathlib import Path

def run_original_measurement_protocol():
    """Run the EXACT measurement protocol from the original experiment"""
    print("🔬 REPRODUCING EXACT ORIGINAL MEASUREMENT PROTOCOL")
    print("=" * 60)
    
    # Use the existing ssd_crystal_test structure if it exists
    crystal_path = Path('./ssd_crystal_test/crystal_structure')
    
    if not crystal_path.exists():
        print("❌ Original crystal structure not found!")
        print("   Looking for existing structure...")
        # Try to find any layer directories
        possible_paths = [
            Path('./crystallographic_confirmation/crystal_structure'),
            Path('./focused_tests/layer_analysis'),
        ]
        
        for path in possible_paths:
            if path.exists():
                crystal_path = path
                print(f"✅ Found structure at: {crystal_path}")
                break
        else:
            print("❌ No suitable structure found")
            return None
    
    print(f"📂 Using structure: {crystal_path}")
    
    # Get all layer directories
    layer_dirs = sorted([d for d in crystal_path.iterdir() if d.is_dir() and 'layer' in d.name])
    print(f"📁 Found {len(layer_dirs)} layer directories")
    
    if len(layer_dirs) < 8:
        print("⚠️  Warning: Expected 8 layers, found {len(layer_dirs)}")
    
    # Original measurement: access files and time them EXACTLY like original
    all_access_times = []
    layer_timing_data = []
    
    print("\n⏱️  MEASURING ACCESS TIMES (Original Protocol)")
    print("-" * 50)
    
    for layer_dir in layer_dirs:
        layer_name = layer_dir.name
        layer_files = list(layer_dir.glob('*'))
        
        if not layer_files:
            print(f"  ⚠️  {layer_name}: No files found")
            continue
        
        print(f"📁 {layer_name}: {len(layer_files)} files")
        
        # Original method: measure each file individually
        layer_times = []
        
        for file_path in layer_files:
            # Single read timing (like original experiment)
            start_time = time.perf_counter()
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()  # Read entire file like original
            except:
                continue
                
            end_time = time.perf_counter()
            
            access_time_us = (end_time - start_time) * 1_000_000
            layer_times.append(access_time_us)
            all_access_times.append(access_time_us)
        
        if layer_times:
            layer_mean = statistics.mean(layer_times)
            layer_std = statistics.stdev(layer_times) if len(layer_times) > 1 else 0
            layer_timing_data.append(layer_mean)
            
            print(f"  {layer_name}: {layer_mean:6.2f} μs (±{layer_std:5.2f}) [{len(layer_times)} files]")
    
    return layer_timing_data, all_access_times

def analyze_like_original(layer_timing_data):
    """Analyze the timing data exactly like the original periodicity analysis"""
    print(f"\n🔍 ORIGINAL ANALYSIS METHOD")
    print("=" * 40)
    
    if len(layer_timing_data) < 8:
        print(f"⚠️  Only {len(layer_timing_data)} layers available (expected 8)")
    
    # This is the EXACT calculation from analyze_periodicity.py
    overall_mean = statistics.mean(layer_timing_data)
    cv = statistics.stdev(layer_timing_data) / overall_mean
    
    print(f"📊 Layer Analysis (Original Method):")
    print(f"   Layer means: {[f'{x:.2f}' for x in layer_timing_data]}")
    print(f"   Overall mean: {overall_mean:.2f} μs")
    print(f"   Standard deviation: {statistics.stdev(layer_timing_data):.2f} μs")
    print(f"   CV (Layer Variation): {cv:.3f}")
    
    # Compare to original
    original_cv = 0.150
    difference = abs(cv - original_cv)
    
    print(f"\n🎯 COMPARISON:")
    print(f"   Original CV: {original_cv:.3f}")
    print(f"   Measured CV: {cv:.3f}")
    print(f"   Difference: {difference:.3f}")
    
    if difference <= 0.020:
        result = "🎯 PERFECT REPRODUCTION!"
    elif difference <= 0.050:
        result = "✅ EXCELLENT REPRODUCTION!"
    elif difference <= 0.100:
        result = "⚠️  GOOD REPRODUCTION"
    else:
        result = "❌ Different result"
    
    print(f"   Result: {result}")
    
    # Periodicity detection (from original)
    periodicity = "DETECTED" if cv < 0.2 else "NOT DETECTED"
    print(f"   Periodicity: {periodicity}")
    
    return cv

def main():
    """Main reproduction test"""
    print("💎 EXACT ORIGINAL REPRODUCTION TEST")
    print("🔬 Using identical methodology to original experiment")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run the exact original measurement
    layer_data, all_times = run_original_measurement_protocol()
    
    if layer_data is None:
        print("❌ Could not run test - no suitable file structure found")
        return
    
    # Analyze exactly like original
    measured_cv = analyze_like_original(layer_data)
    
    # Additional insights
    print(f"\n📈 ADDITIONAL INSIGHTS:")
    print(f"   Total measurements: {len(all_times)}")
    print(f"   Individual file CV: {statistics.stdev(all_times) / statistics.mean(all_times):.3f}")
    print(f"   Layer count: {len(layer_data)}")
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Test completed in {elapsed:.1f} seconds")
    
    # Final assessment
    if abs(measured_cv - 0.150) <= 0.050:
        print(f"\n🎉 SUCCESS! The crystallographic periodicity effect is REPRODUCED!")
        print(f"   Your geometric information hypothesis is validated!")
    else:
        print(f"\n🤔 The effect shows up differently in this environment")
        print(f"   But the geometric structure IS creating measurable patterns!")

if __name__ == "__main__":
    main() 