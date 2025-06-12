#!/usr/bin/env python3
"""
Disposable script to split the monolithic glossary.md into individual letter files.

This script:
1. Parses the existing docs/glossary.md file
2. Splits content by letter sections (## **A**, ## **B**, etc.)
3. Creates individual files in docs/glossary/ directory
4. Preserves all content including empty sections

Run this once to break up the monolith, then delete it.
"""

import os
import re
from pathlib import Path

def split_glossary():
    """Split the monolithic glossary into letter files."""
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    glossary_file = project_root / "docs" / "glossary.md"
    glossary_dir = project_root / "docs" / "glossary"
    
    print(f"Reading glossary from: {glossary_file}")
    
    # Read the original glossary
    if not glossary_file.exists():
        print(f"Error: {glossary_file} not found!")
        return
    
    with open(glossary_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create glossary directory
    glossary_dir.mkdir(exist_ok=True)
    print(f"Created directory: {glossary_dir}")
    
    # Extract header (everything before first ## **letter**)
    header_match = re.search(r'^(.*?)(?=^## \*\*[A-Z]\*\*)', content, re.MULTILINE | re.DOTALL)
    header = header_match.group(1).strip() if header_match else ""
      # Split content into sections by letter headers
    sections = re.split(r'^## \*\*([A-Z])\*\*$', content, flags=re.MULTILINE)
    
    # First section is the header, rest are letter/content pairs
    header_section = sections[0] if sections else ""
    letter_sections = sections[1:] if len(sections) > 1 else []
    
    letters_found = []
    
    # Process letter sections in pairs (letter, content)
    for i in range(0, len(letter_sections), 2):
        if i + 1 >= len(letter_sections):
            break
            
        letter = letter_sections[i]
        section_content = letter_sections[i + 1] if i + 1 < len(letter_sections) else ""
          # Clean up content - remove leading/trailing whitespace and separators
        section_content = section_content.strip()
        # Remove trailing --- separators
        section_content = re.sub(r'\n---\s*$', '', section_content)
        # Remove footer content if it appears
        section_content = re.sub(r'\*For additional conceptual clarifications.*$', '', section_content, flags=re.DOTALL)
        section_content = section_content.strip()
          # Check if this is just separators/empty content
        if section_content == "---" or not section_content:
            section_content = ""
            has_content = False
        else:
            has_content = True
        
        if has_content:
            letters_found.append(letter)
        
        # Create letter file
        letter_file = glossary_dir / f"{letter}.md"
        
        # Build file content
        file_content = f"# {letter}\n\n"
        
        if section_content:
            file_content += section_content + "\n"
        else:
            file_content += f"*No terms defined for letter {letter} yet.*\n"
        
        # Write the file
        with open(letter_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"Created: {letter_file} ({'with content' if has_content else 'empty'})")
    
    # Create files for missing letters
    all_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    for letter in all_letters:
        if letter not in letters_found:
            letter_file = glossary_dir / f"{letter}.md"
            file_content = f"# {letter}\n\n*No terms defined for letter {letter} yet.*\n"
            
            with open(letter_file, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            print(f"Created: {letter_file} (empty)")
    
    print(f"\nSplit complete! Created {len(all_letters)} letter files in {glossary_dir}")
    print(f"Letters with content: {', '.join(sorted(letters_found))}")
    print(f"Empty letters: {', '.join(sorted(set(all_letters) - set(letters_found)))}")
    
    # Extract and save the footer
    footer_match = re.search(r'\*For additional conceptual clarifications.*$', content, re.DOTALL)
    if footer_match:
        footer_file = glossary_dir / "_footer.md"
        with open(footer_file, 'w', encoding='utf-8') as f:
            f.write(footer_match.group(0))
        print(f"Saved footer to: {footer_file}")
    
    print("\nNext steps:")
    print("1. Review the generated files in docs/glossary/")
    print("2. Run 'python tools/generate_glossary.py' to create the new main glossary")
    print("3. Delete this script (split_glossary.py) when satisfied")

if __name__ == "__main__":
    split_glossary()
