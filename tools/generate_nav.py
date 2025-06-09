\
import os
import re
import glob

# --- Configuration ---
DOCS_DIR_NAME = "docs"  # Name of the docs directory relative to project root

# --- Helper Functions ---
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

def get_relative_path(target_abs_path, current_file_abs_path):
    """Computes the relative path from the directory of current_file_abs_path to target_abs_path."""
    if not target_abs_path: 
        return "#" 
    current_dir = os.path.dirname(current_file_abs_path)
    try:
        rel_path = os.path.relpath(target_abs_path, current_dir)
        return rel_path.replace(os.sep, "/") # Changed from rel_path.replace("\\\\", "/")
    except ValueError: 
        return target_abs_path 

def process_subsection_directory(subsection_dir_path, subsection_dir_name, parent_section_info, file_number_str, dir_number_prefix_str):
    """Process files within a subsection subdirectory (e.g., 4b-emergent-stability-longevity/)."""
    subsection_files = []
    print(f"Debug: Processing subsection directory: {subsection_dir_path}")
    
    try:
        items_in_subsection = os.listdir(subsection_dir_path)
        markdown_files = [f for f in items_in_subsection if f.endswith('.md')]
        markdown_files.sort()  # Alphabetical ordering within subsection
        print(f"Debug: Found markdown files in {subsection_dir_name}: {markdown_files}")
        
        for md_file in markdown_files:
            file_abs_path = os.path.join(subsection_dir_path, md_file)
            title = get_h1_title(file_abs_path)
            
            # Determine parent info for nested files
            parent_title = "Up"
            parent_path = None
            if parent_section_info:
                parent_title = parent_section_info["title"]
                parent_path = parent_section_info["abs_path"]
            
            subsection_files.append({
                "abs_path": file_abs_path,
                "title": title,
                "parent_dir_name": parent_section_info["parent_dir_name"] if parent_section_info else subsection_dir_name,
                "file_name": md_file,
                "is_main_section_file": False,
                "main_section_parent_path": parent_path,
                "main_section_parent_title": parent_title,
                "is_nested_file": True,
                "subsection_dir_name": subsection_dir_name
            })
            print(f"Debug: Added nested file: {md_file}")
            
    except Exception as e:
        print(f"Debug: Error processing subsection directory {subsection_dir_path}: {e}")
    
    return subsection_files

# --- Main Document Processing ---
def build_document_map(docs_abs_dir):
    """Builds an ordered list of document information dictionaries."""
    all_files_ordered = []
    print(f"Debug: docs_abs_dir = {docs_abs_dir}")

    try:
        listed_items = os.listdir(docs_abs_dir)
        print(f"Debug: items in docs_abs_dir = {listed_items}")
    except Exception as e:
        print(f"Debug: Error listing directory {docs_abs_dir}: {e}")
        return []

    section_dirs_candidates = []
    for d_item in listed_items:
        path_d_item = os.path.join(docs_abs_dir, d_item)
        if os.path.isdir(path_d_item):
            section_dirs_candidates.append(d_item)
    print(f"Debug: candidate directories in docs_abs_dir = {section_dirs_candidates}")
    
    section_dirs = sorted([
        d for d in section_dirs_candidates
        if re.match(r"^\d{2}-", d) 
    ])
    print(f"Debug: matched section_dirs = {section_dirs}")

    if not section_dirs:
        print("Debug: No section directories found matching the pattern '\\\\d{2}-'.")
        return []

    for section_dir_name in section_dirs: # e.g., "01-pattern-realism"
        current_section_abs_dir = os.path.join(docs_abs_dir, section_dir_name)
        
        dir_number_prefix_str = section_dir_name.split('-', 1)[0] # "01", "02", ...
        dir_name_suffix = section_dir_name.split('-', 1)[1]    # "pattern-realism"
        
        try:
            # Number used in filenames, typically without leading zero for 01-09
            file_number_str = str(int(dir_number_prefix_str)) # "1", "2", ...
        except ValueError:
            print(f"Warning: Could not parse number from directory prefix {dir_number_prefix_str} in {section_dir_name}")
            file_number_str = dir_number_prefix_str # Fallback

        print(f"Debug: Processing section {section_dir_name}: dir_num_prefix='{dir_number_prefix_str}', file_num_str='{file_number_str}', suffix='{dir_name_suffix}'")

        # Expected main filename based on observed pattern (e.g., "1-pattern-realism.md")
        expected_main_filename = f"{file_number_str}-{dir_name_suffix}.md"
        main_section_file_abs_path = os.path.join(current_section_abs_dir, expected_main_filename)
        
        main_section_doc_info = None
        
        if not os.path.exists(main_section_file_abs_path):
            print(f"Debug: Primary expected main file '{expected_main_filename}' not found in {current_section_abs_dir}.")
            # Fallback 1: Try with leading zero in filename (e.g., "01-pattern-realism.md")
            expected_main_filename_alt = f"{dir_number_prefix_str}-{dir_name_suffix}.md"
            main_section_file_abs_path_alt = os.path.join(current_section_abs_dir, expected_main_filename_alt)
            if os.path.exists(main_section_file_abs_path_alt):
                main_section_file_abs_path = main_section_file_abs_path_alt
                print(f"Debug: Found main file (alt name with leading zero): {main_section_file_abs_path}")
            else:
                print(f"Debug: Alt main file '{expected_main_filename_alt}' also not found.")
                # Fallback 2: More general glob for <file_number_str>-*.md (e.g. "1-*.md") and filter out subsections
                glob_pattern = os.path.join(current_section_abs_dir, f"{file_number_str}-*.md") # e.g. "1-*.md"
                potential_main_files = glob.glob(glob_pattern)
                print(f"Debug: Main file globbing with '{glob_pattern}', found: {potential_main_files}")
                
                actual_main_files = [
                    f_path for f_path in potential_main_files 
                    if not re.match(f"^{file_number_str}[a-z]+-", os.path.basename(f_path)) # e.g. not "1a-..."
                ]
                print(f"Debug: Filtered actual_main_files (glob): {actual_main_files}")

                if actual_main_files:
                    actual_main_files.sort(key=lambda p: len(os.path.basename(p))) # Prefer shorter names
                    main_section_file_abs_path = actual_main_files[0]
                    print(f"Debug: Found main file (glob): {main_section_file_abs_path}")
                else:
                    print(f"Warning: Main section file for {section_dir_name} not found via primary, alt, or glob methods.")
                    main_section_file_abs_path = None 
        else:
            print(f"Debug: Found main file (primary name): {main_section_file_abs_path}")

        if main_section_file_abs_path and os.path.exists(main_section_file_abs_path):
            title = get_h1_title(main_section_file_abs_path)
            main_section_doc_info = {
                "abs_path": main_section_file_abs_path,
                "title": title,
                "parent_dir_name": section_dir_name,
                "file_name": os.path.basename(main_section_file_abs_path),
                "is_main_section_file": True,
                "main_section_parent_path": None, 
                "main_section_parent_title": None 
            }
            all_files_ordered.append(main_section_doc_info)
            print(f"Debug: Added main doc: {main_section_doc_info['file_name']}")
        else:
            # Ensure it's really None if not found, to avoid issues with subsection parent title
            main_section_file_abs_path = None 
            main_section_doc_info = None
            print(f"Debug: Main section file for {section_dir_name} was ultimately not processed.")        # Find subsection files (e.g., 1a-..., 1b-...) and subsection directories
        # First collect all items that could be subsections
        subsection_items = []
        try:
            items_in_subdir = os.listdir(current_section_abs_dir)
            for item_name in items_in_subdir:
                item_path = os.path.join(current_section_abs_dir, item_name)
                
                # Check if item matches subsection pattern (both files and directories)
                if (re.match(f"^{file_number_str}[a-z]+-", item_name) or  # Primary: "1a-"
                    re.match(f"^{dir_number_prefix_str}[a-z]+-", item_name)):  # Fallback: "01a-"
                    
                    # Skip if it's the main section file
                    if main_section_file_abs_path and item_name == os.path.basename(main_section_file_abs_path):
                        continue
                        
                    subsection_items.append((item_name, item_path))
            
            subsection_items.sort()  # Sort by name for consistent ordering
            
        except Exception as e:
            print(f"Debug: Error listing subsection items in {current_section_abs_dir}: {e}")

        print(f"Debug: Found subsection items for {section_dir_name}: {[item[0] for item in subsection_items]}")

        # Process each subsection item (file or directory)
        for item_name, item_path in subsection_items:
            if os.path.isfile(item_path) and item_name.endswith('.md'):
                # Handle traditional flat subsection file
                title = get_h1_title(item_path)
                parent_title_for_sub = "Up" 
                if main_section_doc_info and main_section_doc_info["title"]:
                    parent_title_for_sub = main_section_doc_info["title"]

                all_files_ordered.append({
                    "abs_path": item_path,
                    "title": title,
                    "parent_dir_name": section_dir_name,
                    "file_name": item_name,
                    "is_main_section_file": False,
                    "main_section_parent_path": main_section_file_abs_path if main_section_doc_info else None,
                    "main_section_parent_title": parent_title_for_sub,
                    "is_nested_file": False,
                    "subsection_dir_name": None
                })
                print(f"Debug: Added flat subsection doc: {item_name}")
                
            elif os.path.isdir(item_path):
                # Handle nested subsection directory
                nested_files = process_subsection_directory(
                    item_path, item_name, main_section_doc_info, 
                    file_number_str, dir_number_prefix_str
                )
                all_files_ordered.extend(nested_files)
            
    return all_files_ordered

def generate_and_apply_footers(ordered_docs, readme_abs_path, glossary_abs_path):
    """Generates and applies navigation footers to each document."""
    if not ordered_docs:
        print("No documents found to process for footer generation.") # Changed message
        return

    for i, current_doc in enumerate(ordered_docs):
        prev_doc = ordered_docs[i-1] if i > 0 else None
        next_doc = ordered_docs[i+1] if i < len(ordered_docs) - 1 else None

        parts = []

        if prev_doc:
            rel_path = get_relative_path(prev_doc["abs_path"], current_doc["abs_path"])
            parts.append(f'[<< Previous: {prev_doc["title"]}]({rel_path})')
        else: 
            rel_path_readme = get_relative_path(readme_abs_path, current_doc["abs_path"])
            parts.append(f'[<< Previous: README.md]({rel_path_readme})')
            
        if not current_doc["is_main_section_file"]: 
            if current_doc["main_section_parent_path"] and current_doc["main_section_parent_title"] != "Up":
                rel_path_up = get_relative_path(current_doc["main_section_parent_path"], current_doc["abs_path"])
                parts.append(f'[Up: {current_doc["main_section_parent_title"]}]({rel_path_up})')
            else: 
                rel_path_readme = get_relative_path(readme_abs_path, current_doc["abs_path"])
                parts.append(f'[Up: README.md]({rel_path_readme})') 
        else: 
            rel_path_readme = get_relative_path(readme_abs_path, current_doc["abs_path"])
            rel_path_glossary = get_relative_path(glossary_abs_path, current_doc["abs_path"])
            parts.append(f'[Home: README.md]({rel_path_readme})')
            if glossary_abs_path: # Only add glossary if path is valid
                 parts.append(f'[Glossary: glossary.md]({rel_path_glossary})')

        if next_doc:
            rel_path = get_relative_path(next_doc["abs_path"], current_doc["abs_path"])
            parts.append(f'[Next: {next_doc["title"]} >>]({rel_path})')
        else: 
            rel_path_readme = get_relative_path(readme_abs_path, current_doc["abs_path"])
            parts.append(f'[Next: README.md >>]({rel_path_readme})')

        footer_content = " | ".join(parts)
        
        try:
            with open(current_doc["abs_path"], 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File not found during read {current_doc['abs_path']}")
            continue

        last_hr_index = -1
        for j in range(len(lines) - 1, -1, -1):
            if lines[j].strip() == "---":
                last_hr_index = j
                break
        
        if last_hr_index != -1:
            content_lines = lines[:last_hr_index]
        else: # If no ---, append to end
            print(f"Warning: No '---' separator found in {current_doc['file_name']}. Appending footer to end.")
            content_lines = lines 
            # Remove trailing newlines from original content if HR is missing
            while content_lines and (not content_lines[-1].strip() or content_lines[-1] == '\\n'):
                content_lines.pop()


        # Ensure there's a blank line before ---, unless content is empty
        if content_lines and content_lines[-1].strip() != "":
            content_lines.append("\n") 
        elif not content_lines: # If file was empty or only newlines
             content_lines.append("\n")


        content_lines.append("---\n")
        content_lines.append(footer_content + "\n")

        try:
            with open(current_doc["abs_path"], 'w', encoding='utf-8') as f:
                f.writelines(content_lines)
            print(f"Updated footer for: {current_doc['file_name']}")
        except Exception as e:
            print(f"Error writing to {current_doc['abs_path']}: {e}")

# --- Execution ---
if __name__ == "__main__":
    # Assuming the script is in a 'tools' subdirectory of the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT_ABS = os.path.dirname(script_dir)
    DOCS_ABS_DIR = os.path.join(PROJECT_ROOT_ABS, DOCS_DIR_NAME)
    
    README_ABS_PATH = os.path.join(PROJECT_ROOT_ABS, "README.md")
    # Glossary is inside DOCS_DIR
    GLOSSARY_ABS_PATH = os.path.join(DOCS_ABS_DIR, "glossary.md")

    print(f"Debug: Project root: {PROJECT_ROOT_ABS}")
    print(f"Debug: Docs directory: {DOCS_ABS_DIR}")
    print(f"Debug: README path: {README_ABS_PATH}")
    print(f"Debug: Glossary path: {GLOSSARY_ABS_PATH}")


    if not os.path.isdir(DOCS_ABS_DIR):
        print(f"Error: Docs directory not found at {DOCS_ABS_DIR}")
    elif not os.path.exists(README_ABS_PATH):
        print(f"Error: README.md not found at {README_ABS_PATH}")
    # Glossary is optional for footer generation logic, but good to check
    elif not os.path.exists(GLOSSARY_ABS_PATH):
        print(f"Warning: glossary.md not found at {GLOSSARY_ABS_PATH}. Glossary links may be affected.")
        # Set to None if not found, so get_relative_path handles it gracefully if used
        # GLOSSARY_ABS_PATH = None # generate_and_apply_footers checks this
        ordered_docs = build_document_map(DOCS_ABS_DIR)
        if ordered_docs:
            generate_and_apply_footers(ordered_docs, README_ABS_PATH, GLOSSARY_ABS_PATH) # Pass potentially None glossary path
            print("\\nNavigation footers update process complete.")
        else:
            print("No documents were identified by build_document_map.")

    else:
        print(f"Scanning documents in: {DOCS_ABS_DIR}")
        ordered_docs = build_document_map(DOCS_ABS_DIR)
        
        # print("\\n--- Document Order ---")
        # for doc in ordered_docs:
        #     print(f"- {doc['parent_dir_name']}/{doc['file_name']} (Title: {doc['title']})")
        # print("--- End Document Order ---\\n")

        if ordered_docs:
            generate_and_apply_footers(ordered_docs, README_ABS_PATH, GLOSSARY_ABS_PATH)
            print("\\nNavigation footers update process complete.")
        else:
            # Specific message if build_document_map returns empty
            print("No documents were identified by build_document_map. Please check debug output above for issues in file/directory discovery.")
