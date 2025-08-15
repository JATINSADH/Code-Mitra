# analyzer.py
# This module contains functions for local analysis tasks like running pylint and reading files.

import subprocess

def run_pylint(file_path: str) -> str:
    """
    Runs pylint on a given Python file and returns the output.
    """
    try:
        result = subprocess.run(
            ['pylint', file_path, '--exit-zero'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False 
        )
        return result.stdout if result.stdout else result.stderr
            
    except FileNotFoundError:
        return "Error: 'pylint' command not found. Please make sure it's installed and in your system's PATH."
    except Exception as e:
        return f"An unexpected error occurred during pylint analysis: {e}"

def read_file_content(file_path: str) -> str:
    """
    Safely reads the content of a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
