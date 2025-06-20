import os
import subprocess
import sys

def run_script(script_name, project_root):
    """Runs a Python script using the same interpreter and captures output."""
    script_path = os.path.join(project_root, 'tools', script_name)
    print(f"--- Running {script_name} ---")
    try:
        # Use sys.executable to ensure the same Python interpreter is used.
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=project_root,
            check=True,       # Raise an exception if the script returns a non-zero exit code
            capture_output=True, # Capture stdout and stderr
            text=True,        # Decode stdout/stderr as text
            encoding='utf-8'  # Explicitly set encoding
        )
        print(result.stdout)
        if result.stderr:
            print("--- Stderr ---")
            print(result.stderr)
        print(f"--- Finished {script_name} successfully ---\n")
    except FileNotFoundError:
        print(f"Error: Script not found at {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stdout)
        print(e.stderr)
        print(f"--- {script_name} failed ---")
    except Exception as e:
        print(f"An unexpected error occurred while running {script_name}: {e}")

if __name__ == "__main__":
    # The script is in a 'tools' subdirectory of the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT_ABS = os.path.dirname(script_dir)
    
    print(f"Project root identified as: {PROJECT_ROOT_ABS}")
    print("Starting master script to update all documentation assets...\n")    # List of scripts to run in order
    scripts_to_run = [
        "generate_glossary.py",
        "generate_task_list.py",
        "generate_nav.py",
        "check_broken_links.py",
        "document_length_reporter.py", # Added this line
    ]

    for script in scripts_to_run:
        run_script(script, PROJECT_ROOT_ABS)

    print("All scripts executed.")