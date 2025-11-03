import os
import re


def validate_file_exists(path: str):
    """Raises ValueError if the file at the given path does not exist."""
    clean_path = path.strip().strip("'\"")
    if not os.path.exists(clean_path):
        raise ValueError(f"File not found: '{clean_path}'")


def validate_comma_separated_files(paths: str):
    """Validates a comma-separated string of file paths."""
    if not paths:
        return
    for path in paths.split(","):
        if path.strip():
            validate_file_exists(path.strip())


def validate_space_separated_files(paths: str):
    """Validates a space-separated string of file paths, respecting quotes."""
    if not paths:
        return
    # Split by space, respecting quoted paths
    reference_files = re.split(r'\s+(?=(?:[^""]*"[^""]*")*[^""]*$)', paths.strip())
    for path in reference_files:
        if path.strip():
            validate_file_exists(path)

def validate_list_of_files_exist(paths: list[str]):
    """Validates that all files in a list of paths exist."""
    if not paths:
        return
    for path in paths:
        if path.strip():
            validate_file_exists(path.strip())
