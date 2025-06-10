#!/usr/bin/env python3
"""
Check for broken links in Brain from Brane markdown documents.
Leverages patterns and utilities from generate_nav.py and generate_task_list.py for consistency.

This script:
- Finds all markdown files in the docs directory
- Extracts all markdown links from each file
- Checks if each link is valid (file exists, anchors exist)
- Generates a comprehensive broken links report
- Provides statistics and categorization of broken links
"""

import os
import re
import glob
import urllib.parse
from pathlib import Path
from collections import defaultdict

# --- Configuration ---
DOCS_DIR_NAME = "docs"  # Name of the docs directory relative to project root
OUTPUT_FILE_NAME = "BROKEN_LINKS.md"  # Name of the output file
CHECK_EXTERNAL_URLS = False  # Set to True if you want to check external URLs (slower)

def find_markdown_files(docs_abs_path):
    """Finds all markdown files recursively in the given directory."""
    if not os.path.isdir(docs_abs_path):
        print(f"Error: Directory not found - {docs_abs_path}")
        return []
    return glob.glob(os.path.join(docs_abs_path, '**', '*.md'), recursive=True)

def extract_links_from_file(filepath):
    """
    Extracts all markdown links from a given file.
    Returns tuple: (links_list, reference_definitions)
    - links_list: list of tuples (link_text, link_url, line_number, link_type)
    - reference_definitions: dict of reference_id -> (url, line_number)
    """
    links = []
    reference_definitions = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.readlines()
            
        for line_num, line in enumerate(content, 1):
            # Find markdown links: [text](url)
            markdown_links = re.findall(r'\[([^\]]*?)\]\(([^)]+?)\)', line)
            for link_text, link_url in markdown_links:
                links.append((link_text.strip(), link_url.strip(), line_num, "inline"))
            
            # Find reference-style links: [text][ref]
            ref_links = re.findall(r'\[([^\]]+?)\]\[([^\]]*?)\]', line)
            for link_text, ref_id in ref_links:
                # If ref_id is empty, use link_text as ref_id
                actual_ref_id = ref_id.strip() if ref_id.strip() else link_text.strip()
                links.append((link_text.strip(), f"[ref:{actual_ref_id}]", line_num, "reference"))
            
            # Find reference definitions: [ref]: url
            ref_def_match = re.match(r'^\s*\[([^\]]+?)\]:\s*(.+?)(?:\s|$)', line)
            if ref_def_match:
                ref_id, ref_url = ref_def_match.groups()
                reference_definitions[ref_id.strip()] = (ref_url.strip(), line_num)
                
    except FileNotFoundError:
        print(f"Warning: File not found during link extraction: {filepath}")
    except Exception as e:
        print(f"Error reading or processing file {filepath}: {e}")
    
    return links, reference_definitions

def is_external_url(url):
    """Check if URL is external (http/https)."""
    return url.startswith(('http://', 'https://'))

def is_anchor_link(url):
    """Check if URL is an anchor link (starts with #)."""
    return url.startswith('#')

def is_mailto_link(url):
    """Check if URL is a mailto link."""
    return url.startswith('mailto:')

def resolve_relative_path(base_file_path, relative_url, project_root):
    """
    Resolve a relative URL from a markdown file to an absolute path.
    Returns the resolved absolute path or None if cannot be resolved.
    """
    try:
        # Remove URL fragments and query parameters
        clean_url = relative_url.split('#')[0].split('?')[0]
        if not clean_url:  # Just an anchor
            return base_file_path
            
        base_dir = os.path.dirname(base_file_path)
        
        # Handle relative paths
        if clean_url.startswith('./'):
            clean_url = clean_url[2:]
        elif clean_url.startswith('../'):
            # Handle ../ paths
            resolved_path = os.path.normpath(os.path.join(base_dir, clean_url))
        else:
            # Relative path without ./
            resolved_path = os.path.normpath(os.path.join(base_dir, clean_url))
        
        # Convert to absolute path
        if not os.path.isabs(resolved_path):
            resolved_path = os.path.join(project_root, resolved_path)
            
        return os.path.normpath(resolved_path)
    except Exception:
        return None

def check_link_exists(link_url, link_type, base_file_path, project_root, reference_definitions=None):
    """
    Check if a link exists and is valid.
    Returns tuple: (is_valid, error_message)
    """
    # Handle reference links
    if link_url.startswith('[ref:'):
        if not reference_definitions:
            return False, "reference definitions not provided"
        
        ref_id = link_url[5:-1]  # Remove '[ref:' and ']'
        if ref_id not in reference_definitions:
            return False, f"reference '{ref_id}' not defined"
        
        # Get the actual URL from the reference definition and check it
        actual_url, _ = reference_definitions[ref_id]
        return check_link_exists(actual_url, "inline", base_file_path, project_root)
    
    # Skip external URLs unless explicitly enabled
    if is_external_url(link_url):
        if CHECK_EXTERNAL_URLS:
            # Could add HTTP request checking here in the future
            return True, "external link (not checked)"
        else:
            return True, "external link (skipped)"
    
    # Skip mailto links
    if is_mailto_link(link_url):
        return True, "mailto link (not checked)"
    
    # Handle anchor-only links
    if is_anchor_link(link_url):
        anchor = link_url[1:]  # Remove the #
        if check_anchor_exists(base_file_path, anchor):
            return True, "valid anchor in current file"
        else:
            return False, f"anchor '#{anchor}' not found in current file"
    
    # Check relative file paths
    resolved_path = resolve_relative_path(base_file_path, link_url, project_root)
    
    if not resolved_path:
        return False, "could not resolve path"
    
    if not os.path.exists(resolved_path):
        return False, f"file not found: {os.path.relpath(resolved_path, project_root)}"
    
    # If it's a markdown file with an anchor, check the anchor exists
    if '#' in link_url and resolved_path.endswith('.md'):
        anchor = link_url.split('#', 1)[1]
        if anchor and not check_anchor_exists(resolved_path, anchor):
            return False, f"anchor '#{anchor}' not found in file"
    
    return True, "valid"

def check_anchor_exists(filepath, anchor):
    """
    Check if an anchor exists in a markdown file.
    Looks for headers that would generate the anchor.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert anchor to expected header format
        # GitHub/most markdown processors convert headers to lowercase, replace spaces with dashes
        expected_anchor = anchor.lower().replace(' ', '-')
        # Remove special characters and clean up dashes
        expected_anchor = re.sub(r'[^\w\s\-]', '', expected_anchor)
        expected_anchor = re.sub(r'\s+', '-', expected_anchor)
        expected_anchor = re.sub(r'-+', '-', expected_anchor).strip('-')
        
        # Find all headers (h1-h6)
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        for header_level, header_text in headers:
            # Clean header text and convert to anchor format
            # Remove markdown formatting like **bold**, *italic*, [links](urls), etc.
            clean_header = re.sub(r'\*\*([^*]+)\*\*', r'\1', header_text)  # **bold**
            clean_header = re.sub(r'\*([^*]+)\*', r'\1', clean_header)      # *italic*
            clean_header = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_header)  # [text](url)
            clean_header = re.sub(r'`([^`]+)`', r'\1', clean_header)        # `code`
            clean_header = re.sub(r'[^\w\s\-()]+', '', clean_header).strip()  # Remove other special chars
            
            # Convert to anchor format
            header_anchor = clean_header.lower().replace(' ', '-')
            header_anchor = re.sub(r'[^\w\-]', '', header_anchor)
            header_anchor = re.sub(r'-+', '-', header_anchor).strip('-')
            
            if header_anchor == expected_anchor:
                return True
        
        # Also check for explicit anchor tags
        if f'<a name="{anchor}"' in content or f'<a id="{anchor}"' in content:
            return True
            
        return False
    except Exception:
        return False

def generate_broken_links_report(project_root_abs, docs_dir_name, output_file_name):
    """
    Generates a broken links report from markdown files and saves it.
    """
    docs_abs_path = os.path.join(project_root_abs, docs_dir_name)
    all_markdown_files = find_markdown_files(docs_abs_path)
    
    broken_links_by_file = {}
    total_links_checked = 0
    total_broken_links = 0
    error_types = defaultdict(int)
    files_with_reference_links = 0
    
    print("Scanning for broken links...")
    
    for md_file_abs_path in all_markdown_files:
        relative_path = os.path.relpath(md_file_abs_path, project_root_abs)
        print(f"Checking: {relative_path}")
        
        links, reference_definitions = extract_links_from_file(md_file_abs_path)
        file_broken_links = []
        
        if reference_definitions:
            files_with_reference_links += 1
        
        for link_text, link_url, line_num, link_type in links:
            total_links_checked += 1
            is_valid, error_msg = check_link_exists(
                link_url, link_type, md_file_abs_path, project_root_abs, reference_definitions
            )
            
            if not is_valid:
                file_broken_links.append({
                    'text': link_text,
                    'url': link_url,
                    'line': line_num,
                    'error': error_msg,
                    'type': link_type
                })
                total_broken_links += 1
                
                # Track error types for summary
                if "anchor" in error_msg.lower():
                    error_types["Missing anchor"] += 1
                elif "file not found" in error_msg.lower():
                    error_types["File not found"] += 1
                elif "could not resolve" in error_msg.lower():
                    error_types["Path resolution error"] += 1
                elif "reference" in error_msg.lower() and "not defined" in error_msg.lower():
                    error_types["Undefined reference"] += 1
                else:
                    error_types["Other"] += 1
        
        if file_broken_links:
            broken_links_by_file[relative_path] = file_broken_links
    
    # Generate the report
    output_abs_path = os.path.join(project_root_abs, output_file_name)
    
    try:
        with open(output_abs_path, 'w', encoding='utf-8') as f:
            f.write("# Broken Links Report\n\n")
            f.write(f"This report is automatically generated by scanning all markdown files in the `{docs_dir_name}` directory.\n\n")
            
            # Summary section
            f.write("## Summary\n\n")
            f.write(f"- **Total files scanned**: {len(all_markdown_files)}\n")
            f.write(f"- **Total links checked**: {total_links_checked}\n")
            f.write(f"- **Broken links found**: {total_broken_links}\n")
            f.write(f"- **Files with broken links**: {len(broken_links_by_file)}\n")
            f.write(f"- **Files with reference-style links**: {files_with_reference_links}\n\n")
            
            if error_types:
                f.write("### Breakdown by Error Type\n\n")
                for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- **{error_type}**: {count} links\n")
                f.write("\n")
            
            if not broken_links_by_file:
                f.write("---\n\n")
                f.write("🎉 **No broken links found!** All links are working correctly.\n")
                print("No broken links found.")
                return
            
            f.write("---\n\n")
            f.write("## Broken Links by File\n\n")
            
            # Sort files for consistent output
            for file_path in sorted(broken_links_by_file.keys()):
                broken_links = broken_links_by_file[file_path]
                f.write(f"### [`{file_path}`]({file_path.replace(os.sep, '/')})\n\n")
                f.write(f"*{len(broken_links)} broken link(s) found*\n\n")
                
                for link in broken_links:
                    f.write(f"- **Line {link['line']}** ({link['type']} link): ")
                    f.write(f"`[{link['text']}]({link['url']})` ")
                    f.write(f"→ *{link['error']}*\n")
                
                f.write("\n")
            
            # Add helpful footer
            f.write("---\n\n")
            f.write("## How to Fix Broken Links\n\n")
            f.write("1. **Missing anchors**: Check if the target section headers exist and match the expected format\n")
            f.write("2. **File not found**: Verify the file path is correct and the file exists\n")
            f.write("3. **Path resolution errors**: Check for typos in relative paths (../)\n")
            f.write("4. **Undefined references**: Add missing reference definitions at the bottom of files\n\n")
            f.write(f"*Report generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        print(f"Broken links report successfully generated at: {output_abs_path}")
        print(f"Found {total_broken_links} broken links in {len(broken_links_by_file)} files")
        
        if error_types:
            print("\nBreakdown by error type:")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count} links")

    except Exception as e:
        print(f"Error writing to output file {output_abs_path}: {e}")

# --- Execution ---
if __name__ == "__main__":
    print("Starting broken links checker...")
    
    # The script is in a 'tools' subdirectory of the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT_ABS = os.path.dirname(script_dir)
    
    print(f"Project root identified as: {PROJECT_ROOT_ABS}")
    
    generate_broken_links_report(PROJECT_ROOT_ABS, DOCS_DIR_NAME, OUTPUT_FILE_NAME)
