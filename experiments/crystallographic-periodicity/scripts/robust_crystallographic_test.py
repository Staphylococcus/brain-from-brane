#!/usr/bin/env python3
"""
ROBUST CRYSTALLOGRAPHIC PERIODICITY TEST
Takes multiple measurements to reduce system noise and confirm the effect
"""

import os
import time
import json
import statistics
from pathlib import Path

def run_single_measurement():
    """Run a single measurement cycle"""
    crystal_path = Path('./ssd_crystal_test/crystal_structure')
    
    if not crystal_path.exists():
        return None
    
    # Get all layer directories
    layer_dirs = sorted([d for d in crystal_path.iterdir() if d.is_dir() and 'layer' in d.name])
    
    layer_timing_data = []
    
    for layer_dir in layer_dirs:
        layer_files = list(layer_dir.glob('*'))
        
        if not layer_files:
            continue
        
        # Quick measurement of this layer
        layer_times = []
        
        for file_path in layer_files[:10]:  # Sample 10 files per layer for speed
            start_time = time.perf_counter()
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
            except:
                continue
                
            end_time = time.perf_counter()
            access_time_us = (end_time - start_time) * 1_000_000
            layer_times.append(access_time_us)
        
        if layer_times:
            layer_mean = statistics.mean(layer_times)
            layer_timing_data.append(layer_mean)
    
    if len(layer_timing_data) == 8:
        overall_mean = statistics.mean(layer_timing_data)
        cv = statistics.stdev(layer_timing_data) / overall_mean
        return cv, layer_timing_data
    
    return None

def robust_crystallographic_test(num_trials=10):
    """Run multiple trials and analyze the results"""
    print("🔬 ROBUST CRYSTALLOGRAPHIC PERIODICITY TEST")
    print(f"Running {num_trials} independent trials to reduce system noise")
    print("=" * 60)
    
    all_cvs = []
    all_layer_data = []
    
    for trial in range(num_trials):
        print(f"🧪 Trial {trial+1}/{num_trials}...")
        
        result = run_single_measurement()
        
        if result:
            cv, layer_data = result
            all_cvs.append(cv)
            all_layer_data.append(layer_data)
            
            print(f"   CV: {cv:.3f}")
            print(f"   Layers: {[f'{x:.1f}' for x in layer_data]}")
        else:
            print("   ❌ Failed")
        
        # Small delay between trials
        time.sleep(0.5)
    
    if not all_cvs:
        print("❌ No successful measurements")
        return
    
    # Analyze the results
    print(f"\n📊 ROBUST ANALYSIS RESULTS")
    print("=" * 40)
    
    mean_cv = statistics.mean(all_cvs)
    cv_std = statistics.stdev(all_cvs) if len(all_cvs) > 1 else 0
    
    print(f"📈 CV Statistics:")
    print(f"   Mean CV: {mean_cv:.3f}")
    print(f"   CV Std Dev: {cv_std:.3f}")
    print(f"   CV Range: {min(all_cvs):.3f} - {max(all_cvs):.3f}")
    print(f"   Successful trials: {len(all_cvs)}/{num_trials}")
    
    # Compare to target
    target_cv = 0.150
    difference = abs(mean_cv - target_cv)
    
    print(f"\n🎯 COMPARISON TO TARGET:")
    print(f"   Target CV: {target_cv:.3f}")
    print(f"   Measured CV: {mean_cv:.3f} ± {cv_std:.3f}")
    print(f"   Difference: {difference:.3f}")
    
    # Determine result
    if difference <= 0.050:
        if cv_std < 0.100:  # Low variability
            result = "🎯 ROBUST CONFIRMATION!"
            confidence = "HIGH"
        else:
            result = "✅ CONFIRMED (but variable)"
            confidence = "MODERATE"
    elif difference <= 0.100:
        result = "⚠️ WEAK SIGNAL"
        confidence = "LOW"
    else:
        result = "❌ NO CLEAR SIGNAL"
        confidence = "NONE"
    
    print(f"   Result: {result}")
    print(f"   Confidence: {confidence}")
    
    # Analyze layer consistency
    if len(all_layer_data) >= 3:
        print(f"\n🔍 LAYER CONSISTENCY ANALYSIS:")
        
        # Average layer means across trials
        avg_layers = []
        for layer_idx in range(8):
            layer_values = [trial[layer_idx] for trial in all_layer_data if len(trial) > layer_idx]
            if layer_values:
                avg_layers.append(statistics.mean(layer_values))
        
        if len(avg_layers) == 8:
            layer_cv = statistics.stdev(avg_layers) / statistics.mean(avg_layers)
            print(f"   Average layer pattern: {[f'{x:.1f}' for x in avg_layers]}")
            print(f"   Average layer CV: {layer_cv:.3f}")
            print(f"   Pattern stability: {'HIGH' if layer_cv < 0.200 else 'MODERATE' if layer_cv < 0.400 else 'LOW'}")
    
    return mean_cv, cv_std, confidence

if __name__ == "__main__":
    robust_crystallographic_test() 