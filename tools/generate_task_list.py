import os
import re
import glob

# --- Configuration ---
DOCS_DIR_NAME = "docs"  # Name of the docs directory relative to project root
OUTPUT_FILE_NAME = "TASK_LIST.md" # Name of the output file

def find_markdown_files(docs_abs_path):
    """Finds all markdown files recursively in the given directory."""
    if not os.path.isdir(docs_abs_path):
        print(f"Error: Directory not found - {docs_abs_path}")
        return []
    return glob.glob(os.path.join(docs_abs_path, '**', '*.md'), recursive=True)

def extract_tasks_from_file(filepath):
    """
    Extracts content from HTML comments (<!-- ... -->) in a given file.
    Returns a list of non-empty comment contents.
    """
    tasks = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find all content within <!-- ... --> comment blocks
            matches = re.findall(r'<!--(.*?)-->', content, re.DOTALL)
            for match in matches:
                # .strip() removes leading/trailing whitespace, including newlines
                task_content = match.strip()
                if task_content:  # Only add if the comment is not empty
                    tasks.append(task_content)
    except FileNotFoundError:
        print(f"Warning: File not found during task extraction: {filepath}")
    except Exception as e:
        print(f"Error reading or processing file {filepath}: {e}")
    return tasks

def write_task_tree(file_handle, tree_level, indent_level=0):
    """
    Recursively writes the task tree to the file as a nested bulleted list.
    """
    indent = "    " * indent_level  # 4-space indentation

    # Sort keys to ensure directories are processed before files for a structured output.
    sorted_keys = sorted(tree_level.keys(), key=lambda k: "tasks" in tree_level[k])

    for key in sorted_keys:
        item = tree_level[key]
        if "tasks" in item:  # This is a file object with tasks
            file_handle.write(f"{indent}- [`{key}`]({item['path']})\n")
            task_indent = "    " * (indent_level + 1)
            for task in item['tasks']:
                task_lines = task.strip().split('\n')
                if not task_lines:
                    continue
                # Format each task as a sub-bullet with a blockquote for clarity
                file_handle.write(f"{task_indent}- > {task_lines[0].strip()}\n")
                for line in task_lines[1:]:
                    file_handle.write(f"{task_indent}  > {line.strip()}\n")
                file_handle.write("\n")  # Add space between tasks for readability
        else:  # This is a directory
            file_handle.write(f"{indent}- **{key}/**\n")
            write_task_tree(file_handle, item, indent_level + 1)

def generate_task_list(project_root_abs, docs_dir_name, output_file_name):
    """
    Generates a master task list from comments in markdown files and saves it,
    reflecting the directory structure.
    """
    docs_abs_path = os.path.join(project_root_abs, docs_dir_name)
    all_markdown_files = find_markdown_files(docs_abs_path)
    
    task_tree = {}
    
    print("Scanning for tasks...")
    for md_file_abs_path in all_markdown_files:
        tasks = extract_tasks_from_file(md_file_abs_path)
        if tasks:
            relative_path = os.path.relpath(md_file_abs_path, project_root_abs)
            path_components = relative_path.replace(os.sep, '/').split('/')
            
            current_level = task_tree
            for component in path_components[:-1]:  # Traverse directories
                if component not in current_level:
                    current_level[component] = {}
                current_level = current_level[component]
            
            filename = path_components[-1]
            current_level[filename] = {
                "tasks": tasks,
                "path": relative_path.replace(os.sep, '/')
            }
            
    output_abs_path = os.path.join(project_root_abs, output_file_name)
    
    try:
        with open(output_abs_path, 'w', encoding='utf-8') as f:
            f.write("# Documentation To-Do List\n\n")
            f.write("This list is automatically generated from `<!-- ... -->` comments found in the project's markdown files, structured by directory.\n\n")
            
            # We start from within the 'docs' directory for the output
            docs_task_tree = task_tree.get(docs_dir_name, {})

            if not docs_task_tree:
                f.write("---\n\n")
                f.write("🎉 No pending tasks found. Great job!\n")
                print("No pending tasks found.")
                return

            write_task_tree(f, docs_task_tree)

        print(f"Task list successfully generated at: {output_abs_path}")

    except Exception as e:
        print(f"Error writing to output file {output_abs_path}: {e}")

# --- Execution ---
if __name__ == "__main__":
    # The script is in a 'tools' subdirectory of the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT_ABS = os.path.dirname(script_dir)
    
    print(f"Project root identified as: {PROJECT_ROOT_ABS}")
    
    generate_task_list(PROJECT_ROOT_ABS, DOCS_DIR_NAME, OUTPUT_FILE_NAME) 