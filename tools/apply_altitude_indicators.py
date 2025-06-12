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

# Directories to skip (generated content that shouldn't have altitude indicators)
SKIP_DIRS = {
    "glossary"  # Skip the glossary subdirectory with individual letter files
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

def extract_leading_comments(content):
    """Extract HTML comments that appear before the first H1 heading."""
    lines = content.split('\n')
    comments = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<!--') and not stripped.endswith('-->'):
            # Multi-line comment start
            comments.append(line)
            continue
        elif stripped.startswith('<!--') and stripped.endswith('-->'):
            # Single-line comment
            comments.append(line)
            continue
        elif stripped.endswith('-->'):
            # Multi-line comment end
            comments.append(line)
            continue
        elif comments and not stripped.startswith('#'):
            # Inside a multi-line comment or empty line between comments and header
            comments.append(line)
            continue
        elif stripped.startswith('#'):
            # Found the H1 header, stop collecting comments
            break
        elif not stripped:
            # Empty line, might be between comments and header
            comments.append(line)
            continue
        else:
            # Non-comment content before header, stop collecting
            break
    
    return comments

def get_expected_header_block(emoji, clean_title, description, altitude_text):
    """Generate the expected header block format."""
    return f"""# {emoji} {clean_title}
<!-- markdownlint-disable MD036 -->
{description}
<!-- markdownlint-enable MD036 -->

📍 **Altitude**: {altitude_text}"""

def has_correct_header_block(content, emoji, clean_title, description, altitude_text):
    """Check if content has the correct header block format."""
    expected = get_expected_header_block(emoji, clean_title, description, altitude_text)
    
    # Extract the header section from content (skip leading comments)
    lines = content.split('\n')
    header_start = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith('# '):
            header_start = i
            break
    
    if header_start == -1:
        return False
    
    # Find the end of the header block (next section or empty line after altitude)
    header_end = header_start
    altitude_found = False
    
    for i in range(header_start, len(lines)):
        if altitude_found and (lines[i].strip() == '' or lines[i].strip().startswith('#')):
            header_end = i
            break
        elif '📍 **Altitude**:' in lines[i]:
            altitude_found = True
            header_end = i + 1
    
    if not altitude_found:
        return False
    
    # Extract actual header block
    actual_header = '\n'.join(lines[header_start:header_end])
    
    return actual_header.strip() == expected.strip()

def apply_altitude_indicator(filepath, altitude_text, emoji, description):
    """Apply altitude indicator to a markdown file."""
    try:
        # Read current content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and extract the H1 heading
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if not h1_match:
            return False, "no H1 heading found"
        
        original_title = h1_match.group(1)
        # Clean up any existing formatting
        clean_title = re.sub(r'[🔭🔍⚙️]\s*', '', original_title)
        clean_title = re.sub(r'\*\*', '', clean_title)
        
        # Check if header block is already correct
        if has_correct_header_block(content, emoji, clean_title, description, altitude_text):
            return False, "header block already correct"
        
        # Extract leading comments
        leading_comments = extract_leading_comments(content)
        
        # Create new header block with markdownlint directives
        new_header_block = get_expected_header_block(emoji, clean_title, description, altitude_text)
        
        # Find the position where header block ends
        lines = content.split('\n')
        header_start = -1
        header_end = -1
        
        # Find start of header (first H1)
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                header_start = i
                break
        
        if header_start == -1:
            return False, "no H1 heading found"
        
        # Find end of header block (after altitude line or at next section)
        altitude_found = False
        for i in range(header_start, len(lines)):
            if '📍 **Altitude**:' in lines[i]:
                altitude_found = True
                header_end = i + 1
                break
            elif i > header_start and lines[i].strip().startswith('#'):
                # Found next section without altitude
                header_end = i
                break
            elif i > header_start and lines[i].strip() != '' and not lines[i].strip().startswith('*') and not lines[i].strip().startswith('📍') and not lines[i].strip().startswith('<!--') and not lines[i].strip().endswith('-->'):
                # Found content that's not part of header block
                header_end = i
                break
        
        if header_end == -1:
            header_end = len(lines)
        
        # Rebuild content
        new_lines = []
        
        # Add leading comments if any
        if leading_comments:
            # Only add comments that appear before the header
            comment_end = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('# '):
                    comment_end = i
                    break
            new_lines.extend(lines[:comment_end])
        
        # Add new header block
        new_lines.extend(new_header_block.split('\n'))
        
        # Add remaining content (skip the old header block)
        if header_end < len(lines):
            # Add empty line separator if next content isn't empty
            if lines[header_end].strip() != '':
                new_lines.append('')
            new_lines.extend(lines[header_end:])
        
        # Write back to file
        new_content = '\n'.join(new_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "updated successfully"
        
    except Exception as e:
        return False, f"error: {e}"

def find_all_markdown_files(docs_abs_dir):
    """Find all markdown files in the docs directory, excluding meta files."""
    markdown_files = []
    
    for root, dirs, files in os.walk(docs_abs_dir):
        # Skip directories that should be excluded
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
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
