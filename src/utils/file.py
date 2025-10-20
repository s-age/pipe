import os
import yaml
import time
import json
from contextlib import contextmanager

@contextmanager
def FileLock(lock_file_path: str):
    """A simple file-based lock context manager for process-safe file operations."""
    retry_interval = 0.1
    timeout = 10.0
    start_time = time.monotonic()

    while True:
        try:
            fd = os.open(lock_file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() - start_time >= timeout:
                raise TimeoutError(f"Could not acquire lock on {lock_file_path} within {timeout} seconds.")
            time.sleep(retry_interval)
    
    try:
        yield
    finally:
        try:
            os.remove(lock_file_path)
        except OSError:
            pass

def locked_json_read_modify_write(lock_path: str, file_path: str, modifier_func: callable, default_data=None):
    """
    A utility to safely read, modify, and write a JSON file under a lock.
    The modifier function can optionally return a tuple of (data_to_write, value_to_return).
    """
    with FileLock(lock_path):
        data = default_data
        if os.path.exists(file_path):
            # Avoid race condition by opening file for read first
            content = ""
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if content:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    pass # data remains default_data if file is corrupt

        if data is None:
             raise FileNotFoundError(f"File not found and no default data provided: {file_path}")

        # Apply the modification
        result = modifier_func(data)

        # Unpack result: can be just the modified data, or a tuple (modified_data, value_to_return)
        if isinstance(result, tuple) and len(result) == 2:
            modified_data, return_value = result
        else:
            modified_data = result
            return_value = None
        
        # If modifier returns None for the data part, assume in-place modification
        if modified_data is None:
            modified_data = data

        # Write the modified data back
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(modified_data, f, indent=2, ensure_ascii=False)
        
        return return_value

def read_yaml_file(file_path: str) -> dict:
    """Reads a YAML file and returns its content as a dictionary."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_text_file(file_path: str) -> str:
    """Reads a text file and returns its content as a string."""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def locked_json_write(lock_path: str, file_path: str, data_to_write: dict):
    """
    A utility to safely write a dictionary to a JSON file under a lock.
    Overwrites the file if it exists.
    """
    with FileLock(lock_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_write, f, indent=2, ensure_ascii=False)

def locked_json_read(lock_path: str, file_path: str, default_data=None):
    """
    A utility to safely read a JSON file under a lock.
    Returns default_data if the file doesn't exist or is invalid JSON.
    """
    with FileLock(lock_path):
        if not os.path.exists(file_path):
            return default_data
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                content = f.read()
                if not content:
                    return default_data
                return json.loads(content)
            except json.JSONDecodeError:
                return default_data
