#!/usr/bin/env python3
"""
Crystallographic Periodicity Analysis
Examines timing patterns for geometric signatures
"""

import json
import statistics
from pathlib import Path

def analyze_crystallographic_periodicity(timing_data, structure_name):
    """Analyze timing data for crystallographic periodicity patterns"""
    print(f"\n🔍 ANALYZING {structure_name.upper()} PERIODICITY")
    print("=" * 50)
    
    if len(timing_data) < 40:
        print("⚠️  Insufficient data for periodicity analysis")
        return
    
    # 8-layer crystallographic analysis
    if structure_name == 'crystallographic':
        layer_size = len(timing_data) // 8
        layer_means = []
        
        print(f"📊 Layer size: {layer_size} files per layer")
        print("🔬 Layer-by-layer timing analysis:")
        
        for i in range(8):
            start_idx = i * layer_size
            end_idx = min((i + 1) * layer_size, len(timing_data))
            if end_idx > start_idx:
                layer_times = timing_data[start_idx:end_idx]
                layer_mean = statistics.mean(layer_times)
                layer_std = statistics.stdev(layer_times) if len(layer_times) > 1 else 0
                layer_means.append(layer_mean)
                
                print(f"  Layer {i+1}: {layer_mean:6.2f} μs (±{layer_std:5.2f})")
        
        if len(layer_means) >= 8:
            overall_mean = statistics.mean(layer_means)
            cv = statistics.stdev(layer_means) / overall_mean
            
            print(f"\n📈 Crystallographic Analysis:")
            print(f"  Overall mean: {overall_mean:.2f} μs")
            print(f"  Layer variation (CV): {cv:.3f}")
            print(f"  Periodicity: {'DETECTED' if cv < 0.2 else 'NOT DETECTED'}")
            
            # Look for hexagonal patterns (every 6 units within layers)
            if layer_size >= 12:  # Need at least 2 hexagonal units
                hex_patterns = []
                for layer_data in [timing_data[i*layer_size:(i+1)*layer_size] for i in range(8)]:
                    if len(layer_data) >= 12:
                        hex_groups = []
                        for j in range(0, len(layer_data), 6):
                            hex_group = layer_data[j:j+6]
                            if len(hex_group) == 6:
                                hex_groups.append(statistics.mean(hex_group))
                        
                        if len(hex_groups) >= 2:
                            hex_cv = statistics.stdev(hex_groups) / statistics.mean(hex_groups)
                            hex_patterns.append(hex_cv)
                
                if hex_patterns:
                    avg_hex_cv = statistics.mean(hex_patterns)
                    print(f"  Hexagonal pattern CV: {avg_hex_cv:.3f}")
                    print(f"  Hexagonal regularity: {'DETECTED' if avg_hex_cv < 0.15 else 'NOT DETECTED'}")
    
    # Fractal self-similarity analysis
    elif structure_name == 'fractal':
        print("🌿 Fractal self-similarity analysis:")
        
        # Analyze at different scales
        scales = [3, 9, 27]  # Powers of 3 for fractal structure
        scale_cvs = []
        
        for scale in scales:
            if scale < len(timing_data):
                chunks = []
                for i in range(0, len(timing_data), scale):
                    chunk = timing_data[i:i+scale]
                    if len(chunk) == scale:
                        chunks.append(statistics.mean(chunk))
                
                if len(chunks) >= 2:
                    cv = statistics.stdev(chunks) / statistics.mean(chunks)
                    scale_cvs.append(cv)
                    print(f"  Scale {scale:2d}: CV = {cv:.3f} ({len(chunks)} chunks)")
        
        if len(scale_cvs) >= 2:
            # Look for self-similarity (similar CVs across scales)
            cv_variation = statistics.stdev(scale_cvs) / statistics.mean(scale_cvs)
            print(f"\n📈 Self-similarity metric: {cv_variation:.3f}")
            print(f"  Self-similarity: {'DETECTED' if cv_variation < 0.3 else 'NOT DETECTED'}")

def load_and_analyze_results():
    """Load recent results and analyze periodicity"""
    print("💎 CRYSTALLOGRAPHIC PERIODICITY ANALYZER")
    print("=" * 60)
    
    # Find most recent results file
    results_files = list(Path('.').glob('ssd_crystal_results_*.json'))
    if not results_files:
        print("❌ No results files found. Run experiments first!")
        return
    
    latest_file = max(results_files, key=lambda f: f.stat().st_mtime)
    print(f"📂 Loading: {latest_file}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    raw_results = data['raw_results']
    
    # Analyze crystallographic geometric access
    if 'crystallographic_geometric' in raw_results:
        crystal_times = raw_results['crystallographic_geometric']['access_times_raw']
        analyze_crystallographic_periodicity(crystal_times, 'crystallographic')
    
    # Analyze fractal geometric access  
    if 'fractal_geometric' in raw_results:
        fractal_times = raw_results['fractal_geometric']['access_times_raw']
        analyze_crystallographic_periodicity(fractal_times, 'fractal')
    
    # Compare random vs geometric timing distributions
    print(f"\n🎯 COMPARATIVE ANALYSIS:")
    print("=" * 40)
    
    for structure in ['crystallographic', 'fractal', 'linear', 'random']:
        geom_key = f"{structure}_geometric"
        rand_key = f"{structure}_random"
        
        if geom_key in raw_results and rand_key in raw_results:
            geom_times = raw_results[geom_key]['access_times_raw']
            rand_times = raw_results[rand_key]['access_times_raw']
            
            geom_cv = statistics.stdev(geom_times) / statistics.mean(geom_times)
            rand_cv = statistics.stdev(rand_times) / statistics.mean(rand_times)
            
            consistency_advantage = (rand_cv - geom_cv) / rand_cv * 100
            
            print(f"{structure.capitalize():>15}:")
            print(f"  Geometric CV: {geom_cv:.3f}")
            print(f"  Random CV:    {rand_cv:.3f}")
            print(f"  Consistency:  {consistency_advantage:+6.1f}% advantage for geometric")

if __name__ == "__main__":
    load_and_analyze_results() 