#!/usr/bin/env python3
"""
Apply Abstraction Altitude indicators to Brain from Brane markdown documents.
Leverages patterns and utilities from generate_nav.py for consistency.
"""

import os
import re
import glob

# --- Configuration ---
DOCS_DIR_NAME = "docs"  # Name of the docs directory relative to project root

# Files to skip (meta-documentation that shouldn't have altitude indicators)
SKIP_FILES = {
    "abstraction-altitudes.md",
    "altitude-indicators.md", 
    "glossary.md",
    "operationalization-template.md"
}

# --- Utility Functions (adapted from generate_nav.py) ---
def get_h1_title(filepath):
    """Extracts the H1 title (e.g., # Title) from a Markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("# "):
                    return line[2:].strip()
    except FileNotFoundError:
        pass 
    return os.path.splitext(os.path.basename(filepath))[0].replace('-', ' ').title()

def determine_altitude_from_filename(filename):
    """
    Determine the altitude level based on filename patterns.
    Returns tuple: (altitude_text, emoji, description)
    """
    # Main section files (e.g., 1-pattern-realism.md, 3-agents-as-information-processors.md)
    if re.match(r"^\d+-.*\.md$", filename):
        return (
            "Medium (1,000-10,000 feet) - Conceptual Exploration",
            "🔍",
            "*Medium Altitude Exploration*"
        )
    
    # Subsection files (e.g., 1a-pathway-emergence.md, 5d1-ethical-systems.md)
    elif re.match(r"^\d+[a-z]+-.*\.md$", filename) or re.match(r"^\d+[a-z]\d+-.*\.md$", filename):
        return (
            "Low (0-1,000 feet) - Detailed Analysis", 
            "⚙️",
            "*Low Altitude Analysis*"
        )
    
    return None

def has_altitude_indicator(content):
    """Check if content already has an altitude indicator."""
    return "📍 **Altitude**:" in content

def apply_altitude_indicator(filepath, altitude_text, emoji, description):
    """Apply altitude indicator to a markdown file."""
    try:
        # Read current content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has indicator
        if has_altitude_indicator(content):
            return False, "already has altitude indicator"
        
        # Find and replace the first H1 heading
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if not h1_match:
            return False, "no H1 heading found"
        
        original_title = h1_match.group(1)
        # Clean up any existing formatting
        clean_title = re.sub(r'[🔭🔍⚙️]\s*', '', original_title)
        clean_title = re.sub(r'\*\*', '', clean_title)
        
        # Create new header with altitude indicator
        new_header = f"""# {emoji} {clean_title}
{description}

📍 **Altitude**: {altitude_text}"""
        
        # Replace the original header
        new_content = re.sub(r'^# .+$', new_header, content, count=1, flags=re.MULTILINE)
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "updated successfully"
        
    except Exception as e:
        return False, f"error: {e}"

def find_all_markdown_files(docs_abs_dir):
    """Find all markdown files in the docs directory, excluding meta files."""
    markdown_files = []
    
    for root, dirs, files in os.walk(docs_abs_dir):
        for file in files:
            if file.endswith('.md') and file not in SKIP_FILES:
                full_path = os.path.join(root, file)
                markdown_files.append((full_path, file))
    
    return sorted(markdown_files)

def main():
    """Main function to apply altitude indicators to all relevant markdown files."""
    # Get project paths (same pattern as generate_nav.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    docs_abs_dir = os.path.join(project_root, DOCS_DIR_NAME)
    
    print(f"Project root: {project_root}")
    print(f"Docs directory: {docs_abs_dir}")
    
    if not os.path.isdir(docs_abs_dir):
        print(f"Error: Docs directory not found at {docs_abs_dir}")
        return
    
    # Find all markdown files
    markdown_files = find_all_markdown_files(docs_abs_dir)
    print(f"\nFound {len(markdown_files)} markdown files to process")
    
    # Process each file
    updated_count = 0
    skipped_count = 0
    
    for filepath, filename in markdown_files:
        print(f"\nProcessing: {filename}")
          # Determine altitude based on filename
        altitude_info = determine_altitude_from_filename(filename)
        
        if not altitude_info:
            print(f"  [SKIP] Skipping - doesn't match expected naming pattern")
            skipped_count += 1
            continue
        
        altitude_text, emoji, description = altitude_info
        
        # Apply the altitude indicator
        success, message = apply_altitude_indicator(filepath, altitude_text, emoji, description)
        
        if success:
            altitude_level = altitude_text.split(' ')[0]  # Extract "Medium" or "Low"
            print(f"  [OK] Updated with {altitude_level} altitude indicator")
            updated_count += 1
        else:
            print(f"  [SKIP] Skipped - {message}")
            skipped_count += 1
    
    print(f"\n" + "="*50)
    print(f"Altitude indicator application complete!")
    print(f"Updated: {updated_count} files")
    print(f"Skipped: {skipped_count} files")
    print(f"Total processed: {len(markdown_files)} files")

if __name__ == "__main__":
    main()
