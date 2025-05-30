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
        pass  # Should be handled by file existence checks before calling
    # Fallback title if H1 not found or file error
    return os.path.splitext(os.path.basename(filepath))[0].replace('-', ' ').title()

def get_relative_path(target_abs_path, current_file_abs_path):
    """Computes the relative path from the directory of current_file_abs_path to target_abs_path."""
    if not target_abs_path: # Handle cases where a target (e.g. parent) might be None
        return "#" 
    current_dir = os.path.dirname(current_file_abs_path)
    try:
        rel_path = os.path.relpath(target_abs_path, current_dir)
        return rel_path.replace("\\\\", "/") # Ensure forward slashes for Markdown
    except ValueError: # Can happen on Windows if paths are on different drives
        return target_abs_path # Fallback to absolute path (less ideal)


# --- Main Document Processing ---
def build_document_map(docs_abs_dir):
    """Builds an ordered list of document information dictionaries."""
    all_files_ordered = []
    
    section_dirs = sorted([
        d for d in os.listdir(docs_abs_dir)
        if os.path.isdir(os.path.join(docs_abs_dir, d)) and re.match(r"^\\d{2}-", d)
    ])

    for section_dir_name in section_dirs:
        current_section_abs_dir = os.path.join(docs_abs_dir, section_dir_name)
        
        dir_number_prefix = section_dir_name.split('-', 1)[0]
        dir_name_suffix = section_dir_name.split('-', 1)[1]
        expected_main_filename = f"{dir_number_prefix}-{dir_name_suffix}.md"
        main_section_file_abs_path = os.path.join(current_section_abs_dir, expected_main_filename)
        
        main_section_doc_info = None
        
        if not os.path.exists(main_section_file_abs_path):
            # Fallback: try to find any <number>-<name>.md that isn't a subsection
            glob_pattern = os.path.join(current_section_abs_dir, f"{dir_number_prefix}-*.md")
            potential_main_files = glob.glob(glob_pattern)
            # Filter out subsections like 1a-, 1b-
            actual_main_files = [
                f for f in potential_main_files 
                if not re.match(f"^{dir_number_prefix}[a-z]+-", os.path.basename(f))
            ]
            if actual_main_files:
                main_section_file_abs_path = actual_main_files[0] # Take the first match
            else:
                print(f"Warning: Main section file for {section_dir_name} not found (expected {expected_main_filename}).")
                main_section_file_abs_path = None

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

        # Find subsection files (e.g., 1a-..., 1b-...)
        # Ensure they are sorted correctly (e.g., 1a, 1b, ... then 10a)
        subsection_files_names = sorted([
            f for f in os.listdir(current_section_abs_dir)
            if f.endswith(".md") and 
               (not main_section_file_abs_path or f != os.path.basename(main_section_file_abs_path)) and 
               re.match(f"^{dir_number_prefix}[a-z]+-", f)
        ])

        for sub_file_name in subsection_files_names:
            sub_file_abs_path = os.path.join(current_section_abs_dir, sub_file_name)
            title = get_h1_title(sub_file_abs_path)
            parent_title_for_sub = "Up" # Default
            if main_section_doc_info and main_section_doc_info["title"]:
                parent_title_for_sub = main_section_doc_info["title"]

            all_files_ordered.append({
                "abs_path": sub_file_abs_path,
                "title": title,
                "parent_dir_name": section_dir_name,
                "file_name": sub_file_name,
                "is_main_section_file": False,
                "main_section_parent_path": main_section_file_abs_path if main_section_doc_info else None,
                "main_section_parent_title": parent_title_for_sub
            })
            
    return all_files_ordered

def generate_and_apply_footers(ordered_docs, readme_abs_path, glossary_abs_path):
    """Generates and applies navigation footers to each document."""
    if not ordered_docs:
        print("No documents found to process.")
        return

    for i, current_doc in enumerate(ordered_docs):
        prev_doc = ordered_docs[i-1] if i > 0 else None
        next_doc = ordered_docs[i+1] if i < len(ordered_docs) - 1 else None

        parts = []

        # Previous Link
        if prev_doc:
            rel_path = get_relative_path(prev_doc["abs_path"], current_doc["abs_path"])
            parts.append(f'[<< Previous: {prev_doc["title"]}]({rel_path})')
        else: 
            rel_path_readme = get_relative_path(readme_abs_path, current_doc["abs_path"])
            parts.append(f'[<< Previous: README.md]({rel_path_readme})')
            
        # Up Link / Home & Glossary
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
            parts.append(f'[Glossary: glossary.md]({rel_path_glossary})')

        # Next Link
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
        else:
            content_lines = lines 

        while content_lines and not content_lines[-1].strip():
            content_lines.pop()
        
        if content_lines and content_lines[-1].strip() != "":
            content_lines.append("\\n") 
        
        content_lines.append("---\\n")
        content_lines.append(footer_content + "\\n")

        try:
            with open(current_doc["abs_path"], 'w', encoding='utf-8') as f:
                f.writelines(content_lines)
            print(f"Updated footer for: {current_doc['file_name']}")
        except Exception as e:
            print(f"Error writing to {current_doc['abs_path']}: {e}")

# --- Execution ---
if __name__ == "__main__":
    PROJECT_ROOT_ABS = os.path.dirname(os.path.abspath(__file__))
    DOCS_ABS_DIR = os.path.join(PROJECT_ROOT_ABS, DOCS_DIR_NAME)
    
    README_ABS_PATH = os.path.join(PROJECT_ROOT_ABS, "README.md")
    GLOSSARY_ABS_PATH = os.path.join(DOCS_ABS_DIR, "glossary.md")

    if not os.path.isdir(DOCS_ABS_DIR):
        print(f"Error: Docs directory not found at {DOCS_ABS_DIR}")
    elif not os.path.exists(README_ABS_PATH):
        print(f"Error: README.md not found at {README_ABS_PATH}")
    elif not os.path.exists(GLOSSARY_ABS_PATH):
        print(f"Error: glossary.md not found at {GLOSSARY_ABS_PATH}")
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
            print("No documents were found to process based on the expected structure.")
