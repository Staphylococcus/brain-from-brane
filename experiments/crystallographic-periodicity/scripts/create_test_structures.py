#!/usr/bin/env python3
"""
SSD Crystallographic Experiment - File Structure Creator
Creates different geometric organizational patterns for testing information geometry
"""

import os
import random
import string
import hashlib
from pathlib import Path
import time

# Configuration
NUM_FILES = 1000
FILE_SIZE_MB = 1
CHUNK_SIZE = 1024 * 1024  # 1MB chunks

def generate_test_content(file_id, pattern_type):
    """Generate deterministic content based on file ID and pattern type"""
    # Create deterministic but varied content
    seed = f"{pattern_type}_{file_id}"
    content_hash = hashlib.md5(seed.encode()).hexdigest()
    
    # Generate content that's exactly FILE_SIZE_MB
    base_content = content_hash * (FILE_SIZE_MB * CHUNK_SIZE // len(content_hash) + 1)
    return base_content[:FILE_SIZE_MB * CHUNK_SIZE].encode()

def create_random_organization(base_path):
    """Condition A: Random file organization (control)"""
    print("Creating RANDOM organization...")
    path = Path(base_path) / "random_files"
    path.mkdir(parents=True, exist_ok=True)
    
    # Generate random filenames
    random.seed(42)  # Deterministic randomness for reproducibility
    filenames = []
    for i in range(NUM_FILES):
        # Random 8-character filename
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        ext = random.choice(['.txt', '.doc', '.pdf', '.data', '.info'])
        filenames.append(f"{name}{ext}")
    
    for i, filename in enumerate(filenames):
        filepath = path / filename
        with open(filepath, 'wb') as f:
            f.write(generate_test_content(i, "random"))
    
    print(f"✅ Created {NUM_FILES} randomly organized files")
    return path

def create_crystallographic_organization(base_path):
    """Condition B: Crystallographic lattice organization"""
    print("Creating CRYSTALLOGRAPHIC organization...")
    path = Path(base_path) / "crystal_structure"
    path.mkdir(parents=True, exist_ok=True)
    
    # Crystallographic parameters
    LAYERS = 8
    UNITS_PER_LAYER = NUM_FILES // LAYERS
    UNITS_PER_ROW = 6  # Hexagonal packing
    
    file_count = 0
    for layer in range(LAYERS):
        layer_path = path / f"layer_{layer + 1}"
        layer_path.mkdir(exist_ok=True)
        
        for unit in range(UNITS_PER_LAYER):
            if file_count >= NUM_FILES:
                break
            
            # Calculate position in crystallographic lattice
            row = unit // UNITS_PER_ROW
            col = unit % UNITS_PER_ROW
            
            # Hexagonal offset for alternate rows
            offset = "_offset" if row % 2 == 1 else ""
            
            filename = f"unit_{layer + 1}_{row + 1}_{col + 1}{offset}.txt"
            filepath = layer_path / filename
            
            with open(filepath, 'wb') as f:
                f.write(generate_test_content(file_count, "crystal"))
            
            file_count += 1
    
    print(f"✅ Created {file_count} crystallographically organized files in {LAYERS} layers")
    return path

def create_fractal_organization(base_path):
    """Condition C: Fractal self-similar organization"""
    print("Creating FRACTAL organization...")
    path = Path(base_path) / "fractal_tree"
    path.mkdir(parents=True, exist_ok=True)
    
    def create_fractal_branch(current_path, depth, branch_id, file_counter):
        """Recursively create fractal structure"""
        if depth <= 0 or file_counter[0] >= NUM_FILES:
            return
        
        # Create 3 sub-branches at each level
        for i in range(3):
            if file_counter[0] >= NUM_FILES:
                break
                
            if depth > 1:
                # Create sub-directory
                sub_path = current_path / f"branch_{branch_id}_{i + 1}"
                sub_path.mkdir(exist_ok=True)
                create_fractal_branch(sub_path, depth - 1, f"{branch_id}_{i + 1}", file_counter)
            else:
                # Create leaf file
                filename = f"leaf_{branch_id}_{i + 1}.txt"
                filepath = current_path / filename
                
                with open(filepath, 'wb') as f:
                    f.write(generate_test_content(file_counter[0], "fractal"))
                
                file_counter[0] += 1
    
    # Start fractal generation
    file_counter = [0]
    create_fractal_branch(path, 6, "1", file_counter)  # 6 levels deep
    
    print(f"✅ Created {file_counter[0]} fractally organized files")
    return path

def create_linear_organization(base_path):
    """Condition D: Simple linear sequential organization"""
    print("Creating LINEAR organization...")
    path = Path(base_path) / "sequence"
    path.mkdir(parents=True, exist_ok=True)
    
    for i in range(NUM_FILES):
        filename = f"file_{i + 1:04d}.txt"
        filepath = path / filename
        
        with open(filepath, 'wb') as f:
            f.write(generate_test_content(i, "linear"))
    
    print(f"✅ Created {NUM_FILES} linearly organized files")
    return path

def create_all_test_structures(base_path="ssd_crystal_test"):
    """Create all test conditions"""
    print("🧪 CREATING SSD CRYSTALLOGRAPHIC TEST STRUCTURES")
    print("=" * 60)
    
    base_path = Path(base_path)
    base_path.mkdir(exist_ok=True)
    
    start_time = time.time()
    
    structures = {
        'random': create_random_organization(base_path),
        'crystallographic': create_crystallographic_organization(base_path),
        'fractal': create_fractal_organization(base_path),
        'linear': create_linear_organization(base_path)
    }
    
    creation_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"✅ ALL STRUCTURES CREATED in {creation_time:.2f} seconds")
    print(f"📊 Total files: {NUM_FILES * 4}")
    print(f"💾 Total size: ~{NUM_FILES * 4 * FILE_SIZE_MB} MB")
    print("\nStructure locations:")
    for name, path in structures.items():
        file_count = sum(1 for _ in path.rglob('*.txt'))
        print(f"  {name:>15}: {path} ({file_count} files)")
    
    # Force filesystem sync
    print("\n🔄 Syncing filesystem...")
    os.sync()
    
    return structures

def get_file_lists(base_path="ssd_crystal_test"):
    """Get organized lists of files for each structure"""
    base_path = Path(base_path)
    
    file_lists = {}
    
    # Random files
    random_path = base_path / "random_files"
    file_lists['random'] = sorted(random_path.glob('*'))
    
    # Crystallographic files (by layer, then by lattice position)
    crystal_path = base_path / "crystal_structure"
    crystal_files = []
    for layer in sorted(crystal_path.iterdir()):
        if layer.is_dir():
            crystal_files.extend(sorted(layer.glob('*.txt')))
    file_lists['crystallographic'] = crystal_files
    
    # Fractal files (depth-first traversal)
    fractal_path = base_path / "fractal_tree"
    file_lists['fractal'] = sorted(fractal_path.rglob('*.txt'))
    
    # Linear files
    linear_path = base_path / "sequence"
    file_lists['linear'] = sorted(linear_path.glob('*.txt'))
    
    return file_lists

if __name__ == "__main__":
    print("💎 SSD CRYSTALLOGRAPHIC EXPERIMENT")
    print("Testing whether information organization creates geometric signatures")
    print()
    
    structures = create_all_test_structures()
    
    print("\n🔬 READY FOR GEOMETRIC DETECTION!")
    print("Next step: run access timing measurements...") 