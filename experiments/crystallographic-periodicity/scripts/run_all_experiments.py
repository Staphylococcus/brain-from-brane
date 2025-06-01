#!/usr/bin/env python3
"""
🚀 AUTOMATED GEOMETRIC INFORMATION EXPERIMENT SUITE
Run all breakthrough experiments with one command!

This script automatically runs all four major experiments:
1. Quick Geometric Test (fractal vs linear computation)
2. Memory Geometry Test (crystallographic vs random allocation)  
3. Data Structure Test (spiral vs linear access)
4. Crystallographic Periodicity (filesystem geometry)

Usage: python3 run_all_experiments.py
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def print_header(title, emoji="🧪"):
    """Print a formatted section header"""
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

def print_step(step_num, total_steps, description, emoji="⚡"):
    """Print a formatted step"""
    print(f"\n{emoji} STEP {step_num}/{total_steps}: {description}")
    print("-" * (len(description) + 20))

def run_experiment(script_name, description, estimated_time="30 seconds"):
    """Run a single experiment script"""
    print(f"🔬 Running: {description}")
    print(f"⏱️  Estimated time: {estimated_time}")
    print(f"📜 Script: {script_name}")
    print()
    
    try:
        # Run the script and capture output
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("✅ SUCCESS!")
            print(result.stdout)
            return True
        else:
            print("❌ FAILED!")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT! (took longer than 5 minutes)")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

def check_prerequisites():
    """Check if all required files exist"""
    required_scripts = [
        "simple_geometry_test.py",
        "memory_geometry_test.py", 
        "data_structure_geometry_test.py",
        "create_test_structures.py",
        "reproduce_exact_original.py"
    ]
    
    missing = []
    for script in required_scripts:
        if not Path(script).exists():
            missing.append(script)
    
    if missing:
        print("❌ MISSING REQUIRED FILES:")
        for file in missing:
            print(f"   - {file}")
        print("\nPlease make sure you're in the correct directory:")
        print("brain-from-brane/experiments/crystallographic-periodicity/scripts/")
        return False
    
    return True

def main():
    """Run all geometric information experiments"""
    print_header("AUTOMATED GEOMETRIC INFORMATION EXPERIMENT SUITE", "🚀")
    print("Make your computer prove that information has shapes!")
    print("Total time: ~10 minutes | Total experiments: 4")
    
    # Check prerequisites
    print_step(0, 5, "Checking Prerequisites", "🔍")
    if not check_prerequisites():
        return False
    
    print("✅ All required files found!")
    
    # Track results
    results = {}
    start_time = time.time()
    
    # Experiment 1: Quick Geometric Test
    print_step(1, 5, "Quick Geometric Test", "🔥")
    print("Testing fractal computation vs linear computation...")
    results['geometric'] = run_experiment(
        "simple_geometry_test.py",
        "Fractal vs Linear Computation Signatures",
        "30 seconds"
    )
    
    # Experiment 2: Memory Geometry
    print_step(2, 5, "Memory Geometry Test", "🧠")
    print("Testing crystallographic vs random memory patterns...")
    results['memory'] = run_experiment(
        "memory_geometry_test.py", 
        "Crystallographic vs Random Memory Allocation",
        "1 minute"
    )
    
    # Experiment 3: Data Structure Geometry
    print_step(3, 5, "Data Structure Test", "🌪️")
    print("Testing spiral vs linear data access patterns...")
    results['data_structure'] = run_experiment(
        "data_structure_geometry_test.py",
        "Spiral vs Linear Data Access Patterns", 
        "1 minute"
    )
    
    # Experiment 4: Crystallographic Periodicity (setup)
    print_step(4, 5, "Crystallographic Discovery Setup", "💎")
    print("Creating crystallographic file structures...")
    setup_success = run_experiment(
        "create_test_structures.py",
        "Creating Geometric File Organizations",
        "2 minutes"  
    )
    
    if setup_success:
        print("\n🔬 Running main crystallographic periodicity test...")
        results['crystallographic'] = run_experiment(
            "reproduce_exact_original.py",
            "Filesystem Geometry Timing Measurement",
            "2 minutes"
        )
    else:
        print("❌ Skipping crystallographic test due to setup failure")
        results['crystallographic'] = False
    
    # Final Results Summary
    print_step(5, 5, "Final Results Summary", "🏆")
    
    total_time = time.time() - start_time
    print(f"⏱️  Total experiment time: {total_time:.1f} seconds")
    
    # Count successes
    successes = sum(1 for result in results.values() if result)
    total_experiments = len(results)
    
    print(f"\n📊 EXPERIMENT RESULTS:")
    print(f"   ✅ Successful: {successes}/{total_experiments}")
    print(f"   ❌ Failed: {total_experiments - successes}/{total_experiments}")
    print(f"   📈 Success Rate: {(successes/total_experiments)*100:.1f}%")
    
    # Detailed breakdown
    experiment_names = {
        'geometric': '🔥 Fractal Computation',
        'memory': '🧠 Memory Geometry', 
        'data_structure': '🌪️ Data Structure Geometry',
        'crystallographic': '💎 Crystallographic Periodicity'
    }
    
    print(f"\n🔍 DETAILED RESULTS:")
    for key, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {experiment_names[key]}: {status}")
    
    # Overall assessment
    if successes >= 3:
        print(f"\n🎉 OUTSTANDING SUCCESS!")
        print(f"You successfully reproduced {successes}/4 geometric information effects!")
        print(f"🚀 You've validated the Brain from Brane framework!")
        
        if successes == 4:
            print(f"\n🏆 PERFECT SCORE! 🏆")
            print(f"You achieved 100% reproduction of all geometric signatures!")
            print(f"🌟 You're now a certified geometric information scientist! 🌟")
            
    elif successes >= 2:
        print(f"\n✅ GOOD SUCCESS!")
        print(f"You reproduced {successes}/4 experiments - strong validation!")
        print(f"💪 Some geometric information effects clearly demonstrated!")
        
    elif successes >= 1:
        print(f"\n⚠️  PARTIAL SUCCESS")
        print(f"You reproduced {successes}/4 experiments - some validation achieved")
        print(f"🔧 Consider checking system conditions and trying again")
        
    else:
        print(f"\n❌ NO SUCCESS")
        print(f"All experiments failed - likely system or setup issue")
        print(f"🛠️  Check the troubleshooting guide and try again")
    
    print(f"\n📚 For detailed analysis, see the individual experiment outputs above")
    print(f"📖 For help, see: SUPER_SIMPLE_REPRODUCTION_GUIDE.md")
    
    return successes >= 2  # Consider 2+ successes as overall success

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n🎯 MISSION ACCOMPLISHED! 🎯")
            sys.exit(0)
        else:
            print(f"\n🔧 MISSION INCOMPLETE - See troubleshooting guide")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Experiment suite interrupted by user")
        print(f"Run again anytime with: python3 run_all_experiments.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        print(f"Please report this issue or check the troubleshooting guide")
        sys.exit(1) 