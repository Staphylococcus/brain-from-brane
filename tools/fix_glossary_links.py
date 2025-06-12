#!/usr/bin/env python3
"""
Fix glossary links to point to the new glossary structure.

This script:
1. Scans all markdown files for links to ../glossary.md#anchor or #anchor (within glossary files)
2. Determines which letter file the anchor belongs to
3. Updates the links to point to the correct ../glossary/LETTER.md#anchor or LETTER.md#anchor
4. Fixes footer paths and other related issues
5. Reports all changes made

Part of the Brain from Brane documentation tools.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def build_term_to_letter_mapping(glossary_dir):
    """Build a mapping from term anchors to their letter files."""
    term_to_letter = {}
    
    # Scan all letter files to build the mapping
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        letter_file = glossary_dir / f"{letter}.md"
        if not letter_file.exists():
            continue
            
        with open(letter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all term headings (### ...)
        for match in re.finditer(r'^###\s+(.+)', content, re.MULTILINE):
            term = match.group(1).strip()
            # Convert to anchor format (GitHub-style slugification)
            anchor = slugify(term)
            term_to_letter[anchor] = letter
    
    return term_to_letter

def slugify(text):
    """Convert text to GitHub-style anchor format."""
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text

def fix_glossary_links():
    """Fix all glossary links in markdown files."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / "docs"
    glossary_dir = docs_dir / "glossary"
    
    print("Building term-to-letter mapping...")
    term_to_letter = build_term_to_letter_mapping(glossary_dir)
    
    print(f"Found {len(term_to_letter)} terms across letter files")
    
    files_changed = 0
    total_links_fixed = 0
    changes_by_file = defaultdict(list)
    
    # Fix links in main docs files
    print("\n=== Fixing links in main docs files ===")
    files_changed_main, links_fixed_main = fix_main_docs_links(docs_dir, glossary_dir, term_to_letter, project_root)
    files_changed += files_changed_main
    total_links_fixed += links_fixed_main
    
    # Fix internal cross-references within glossary letter files
    print("\n=== Fixing internal cross-references in glossary files ===")
    files_changed_glossary, links_fixed_glossary = fix_glossary_internal_links(glossary_dir, term_to_letter, project_root)
    files_changed += files_changed_glossary
    total_links_fixed += links_fixed_glossary
    
    # Fix footer links
    print("\n=== Fixing footer links ===")
    files_changed_footer, links_fixed_footer = fix_footer_links(glossary_dir, project_root)
    files_changed += files_changed_footer
    total_links_fixed += links_fixed_footer
    
    print(f"\nSummary:")
    print(f"- Files changed: {files_changed}")
    print(f"- Total links fixed: {total_links_fixed}")
    
    if not files_changed:
        print("No links needed fixing!")
    
    return files_changed > 0

def fix_main_docs_links(docs_dir, glossary_dir, term_to_letter, project_root):
    """Fix glossary links in main documentation files."""
    # Pattern to match glossary links - handle both ../ and ../../ and even more levels
    glossary_link_pattern = r'\[([^\]]+)\]\((\.\./)+(glossary\.md#[^)]+)\)'
    
    files_changed = 0
    total_links_fixed = 0
    
    # Scan all markdown files in docs directory (except glossary files)
    for md_file in docs_dir.rglob("*.md"):
        # Skip the main glossary file and letter files
        if md_file.name == "glossary.md" or md_file.parent.name == "glossary":
            continue
            
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_changes = []
        
        # Find and replace glossary links
        def replace_link(match):
            link_text = match.group(1)
            path_prefix = match.group(2)  # The ../ or ../../ etc.
            glossary_part = match.group(3)  # glossary.md#anchor
            
            # Extract the anchor from glossary.md#anchor
            if '#' in glossary_part:
                anchor = glossary_part.split('#')[1]
            else:
                return match.group(0)  # No anchor, keep original
            
            if anchor in term_to_letter:
                letter = term_to_letter[anchor]
                # Calculate the correct relative path
                relative_path = md_file.relative_to(docs_dir)
                depth = len(relative_path.parts) - 1  # -1 because the file itself doesn't count
                path_prefix = "../" * depth if depth > 0 else ""
                new_link = f"[{link_text}]({path_prefix}glossary/{letter}.md#{anchor})"
                file_changes.append(f"  {match.group(0)} → {new_link}")
                return new_link
            else:
                # Keep original link if we can't find the term
                print(f"  Warning: Could not find term '{anchor}' in any letter file")
                return match.group(0)
        
        content = re.sub(glossary_link_pattern, replace_link, content)
        
        # Write back if changed
        if content != original_content:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files_changed += 1
            total_links_fixed += len(file_changes)
            
            print(f"Fixed {len(file_changes)} link(s) in {md_file.relative_to(project_root)}")
            for change in file_changes:
                print(change)
            print()
    
    return files_changed, total_links_fixed

def fix_glossary_internal_links(glossary_dir, term_to_letter, project_root):
    """Fix internal cross-references within glossary letter files."""
    # Pattern to match internal anchor links like [text](#anchor)
    internal_link_pattern = r'\[([^\]]+)\]\(#([^)]+)\)'
    
    files_changed = 0
    total_links_fixed = 0
    
    # Process each letter file
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        letter_file = glossary_dir / f"{letter}.md"
        if not letter_file.exists():
            continue
            
        with open(letter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_changes = []
        
        # Find and replace internal links that point to terms in other files
        def replace_internal_link(match):
            link_text = match.group(1)
            anchor = match.group(2)
            
            if anchor in term_to_letter:
                target_letter = term_to_letter[anchor]
                if target_letter != letter:  # Only fix if pointing to different letter file
                    new_link = f"[{link_text}]({target_letter}.md#{anchor})"
                    file_changes.append(f"  {match.group(0)} → {new_link}")
                    return new_link
            
            # Keep original link (either same file or term not found)
            return match.group(0)
        
        content = re.sub(internal_link_pattern, replace_internal_link, content)
        
        # Write back if changed
        if content != original_content:
            with open(letter_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files_changed += 1
            total_links_fixed += len(file_changes)
            
            print(f"Fixed {len(file_changes)} internal link(s) in {letter_file.relative_to(project_root)}")
            for change in file_changes:
                print(change)
            print()
    
    return files_changed, total_links_fixed

def fix_footer_links(glossary_dir, project_root):
    """Fix links in the footer file."""
    footer_file = glossary_dir / "_footer.md"
    if not footer_file.exists():
        return 0, 0
        
    with open(footer_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix the paths in footer - they should be relative to docs/ not docs/glossary/
    content = content.replace(
        "[Introduction](01-pattern-realism/1-pattern-realism.md)",
        "[Introduction](../01-pattern-realism/1-pattern-realism.md)"
    )
    content = content.replace(
        "[Framework Overview](../README.md)",
        "[Framework Overview](../../README.md)"
    )
    
    files_changed = 0
    links_fixed = 0
    
    if content != original_content:
        with open(footer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        files_changed = 1
        links_fixed = 2  # Two links fixed
        print(f"Fixed footer links in {footer_file.relative_to(project_root)}")
    
    return files_changed, links_fixed

if __name__ == "__main__":
    fix_glossary_links()
