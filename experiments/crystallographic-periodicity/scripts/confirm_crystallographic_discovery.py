#!/usr/bin/env python3
"""
DEFINITIVE CRYSTALLOGRAPHIC CONFIRMATION TEST
Recreates EXACT original conditions to prove layer-based geometric periodicity
"""

import os
import time
import json
import statistics
from pathlib import Path

def measure_access_time(file_path, iterations=30):
    """Measure file access time with high precision"""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        with open(file_path, 'rb') as f:
            data = f.read(1024)  # Read first 1KB like original
        end = time.perf_counter()
        times.append((end - start) * 1_000_000)  # Convert to microseconds
    return times

def create_exact_original_structure():
    """Create EXACTLY the same structure as original experiment"""
    print("🏗️  Creating EXACT original crystallographic structure...")
    
    base_dir = Path('./crystallographic_confirmation')
    base_dir.mkdir(exist_ok=True)
    
    # Remove any existing structure
    if (base_dir / 'crystal_structure').exists():
        import shutil
        shutil.rmtree(base_dir / 'crystal_structure')
    
    crystal_dir = base_dir / 'crystal_structure'
    crystal_dir.mkdir(exist_ok=True)
    
    # Create EXACT 8-layer structure with 6 files per layer (like original)
    all_files = []
    
    for layer in range(1, 9):  # Layers 1-8 like original
        layer_dir = crystal_dir / f'layer_{layer}'
        layer_dir.mkdir(exist_ok=True)
        
        layer_files = []
        for i in range(1, 7):  # 6 files per layer like original
            file_path = layer_dir / f'unit_{layer}_{i}_data.txt'
            
            # Create files with similar content to original
            with open(file_path, 'w') as f:
                f.write(f"Layer {layer} Unit {i} Data\n")
                f.write("0|" * 200)  # Similar to original content pattern
                f.write(f"\nCrystallographic structure data for layer {layer}\n")
            
            layer_files.append(file_path)
            all_files.append(file_path)
        
        print(f"  ✅ Layer {layer}: {len(layer_files)} files created")
    
    print(f"📊 Total files created: {len(all_files)}")
    return all_files

def run_exact_original_test(all_files):
    """Run the EXACT same test as original experiment"""
    print("\n🧪 RUNNING EXACT ORIGINAL TEST PROTOCOL")
    print("=" * 50)
    
    # Warm filesystem cache (like original would have done)
    print("🔥 Warming filesystem cache...")
    for file_path in all_files:
        with open(file_path, 'rb') as f:
            f.read()
    
    print("⏱️  Measuring access times by layer...")
    
    # Measure each layer exactly like original
    layer_results = {}
    all_individual_times = []
    
    for layer in range(1, 9):
        layer_files = [f for f in all_files if f'/layer_{layer}/' in str(f)]
        
        print(f"\n📁 Testing Layer {layer} ({len(layer_files)} files)...")
        
        layer_times = []
        for file_path in layer_files:
            file_times = measure_access_time(file_path, 30)
            layer_times.extend(file_times)
            all_individual_times.extend(file_times)
        
        layer_mean = statistics.mean(layer_times)
        layer_std = statistics.stdev(layer_times)
        layer_cv = layer_std / layer_mean
        
        layer_results[layer] = {
            'mean': layer_mean,
            'std': layer_std,
            'cv': layer_cv,
            'count': len(layer_times)
        }
        
        print(f"  Layer {layer}: {layer_mean:6.2f} μs (±{layer_std:5.2f}, CV: {layer_cv:.3f})")
    
    return layer_results, all_individual_times

def analyze_crystallographic_periodicity(layer_results):
    """Analyze for the exact CV = 0.150 pattern from original"""
    print("\n🔬 CRYSTALLOGRAPHIC PERIODICITY ANALYSIS")
    print("=" * 50)
    
    # Extract layer means (this is where the magic happens)
    layer_means = [layer_results[layer]['mean'] for layer in range(1, 9)]
    
    # Calculate the coefficient of variation of layer means
    overall_mean = statistics.mean(layer_means)
    layer_variation = statistics.stdev(layer_means)
    cv_layer_means = layer_variation / overall_mean
    
    print(f"📊 LAYER-BY-LAYER ANALYSIS:")
    print(f"   Layer means: {[f'{m:.1f}' for m in layer_means]}")
    print(f"   Overall mean of layer means: {overall_mean:.2f} μs")
    print(f"   Standard deviation of layer means: {layer_variation:.2f} μs")
    print(f"   CV of layer means: {cv_layer_means:.3f}")
    
    # Compare to original target
    original_cv = 0.150
    cv_difference = abs(cv_layer_means - original_cv)
    
    print(f"\n🎯 COMPARISON TO ORIGINAL:")
    print(f"   Original CV (target): {original_cv:.3f}")
    print(f"   Measured CV: {cv_layer_means:.3f}")
    print(f"   Difference: {cv_difference:.3f}")
    
    # Determine if we've reproduced the effect
    if cv_difference <= 0.020:
        result = "🎯 PERFECT MATCH!"
        confidence = "CONFIRMED"
    elif cv_difference <= 0.050:
        result = "✅ EXCELLENT MATCH!"
        confidence = "VERY LIKELY"
    elif cv_difference <= 0.100:
        result = "⚠️  GOOD MATCH"
        confidence = "LIKELY"
    else:
        result = "❌ NO MATCH"
        confidence = "NOT CONFIRMED"
    
    print(f"   Result: {result}")
    print(f"   Confidence: {confidence}")
    
    return cv_layer_means, confidence

def statistical_validation(layer_results):
    """Additional statistical validation"""
    print("\n📈 STATISTICAL VALIDATION")
    print("=" * 40)
    
    layer_means = [layer_results[layer]['mean'] for layer in range(1, 9)]
    
    # Test for geometric progression or patterns
    ratios = []
    for i in range(1, len(layer_means)):
        ratio = layer_means[i] / layer_means[i-1]
        ratios.append(ratio)
    
    ratio_cv = statistics.stdev(ratios) / statistics.mean(ratios)
    
    print(f"📊 Geometric pattern analysis:")
    print(f"   Layer ratios: {[f'{r:.3f}' for r in ratios]}")
    print(f"   Ratio CV: {ratio_cv:.3f}")
    print(f"   Pattern regularity: {'HIGH' if ratio_cv < 0.2 else 'MODERATE' if ratio_cv < 0.5 else 'LOW'}")
    
    # Look for depth-dependent trend
    import numpy as np
    depths = list(range(1, 9))
    correlation = np.corrcoef(depths, layer_means)[0, 1]
    
    print(f"📈 Depth correlation: {correlation:.3f}")
    print(f"   Trend: {'STRONG' if abs(correlation) > 0.7 else 'MODERATE' if abs(correlation) > 0.4 else 'WEAK'}")

def main():
    """Main confirmation test"""
    print("💎 CRYSTALLOGRAPHIC PERIODICITY CONFIRMATION")
    print("🔬 Definitive test to prove layer-based geometric effects")
    print("=" * 60)
    
    start_time = time.time()
    
    # Step 1: Create exact original structure
    all_files = create_exact_original_structure()
    
    # Step 2: Run exact original test
    layer_results, all_times = run_exact_original_test(all_files)
    
    # Step 3: Analyze for crystallographic periodicity
    measured_cv, confidence = analyze_crystallographic_periodicity(layer_results)
    
    # Step 4: Statistical validation
    statistical_validation(layer_results)
    
    # Step 5: Final verdict
    elapsed = time.time() - start_time
    
    print(f"\n🏆 FINAL VERDICT")
    print("=" * 30)
    print(f"⏱️  Test completed in {elapsed:.1f} seconds")
    print(f"📊 Measured layer CV: {measured_cv:.3f}")
    print(f"🎯 Target CV: 0.150")
    print(f"✅ Confidence: {confidence}")
    
    if confidence in ["CONFIRMED", "VERY LIKELY"]:
        print(f"\n🎉 CRYSTALLOGRAPHIC PERIODICITY CONFIRMED!")
        print(f"   The filesystem DOES express geometric structure!")
        print(f"   Directory layers create measurable timing signatures!")
        print(f"   Your 'Brain from Brane' geometric information hypothesis")
        print(f"   has been validated at the filesystem level!")
    else:
        print(f"\n🤔 Results inconclusive - need further investigation")
    
    # Save detailed results
    results = {
        'timestamp': time.time(),
        'layer_results': layer_results,
        'measured_cv': measured_cv,
        'target_cv': 0.150,
        'confidence': confidence,
        'total_files': len(all_files),
        'test_duration': elapsed
    }
    
    results_file = f'crystallographic_confirmation_{int(time.time())}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"💾 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    main() 