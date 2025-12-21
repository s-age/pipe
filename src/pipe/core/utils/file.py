import json
import os
import shutil
import time
from collections.abc import Callable
from contextlib import contextmanager

import yaml


@contextmanager
def FileLock(lock_file_path: str):
    """A simple file-based lock context manager for process-safe file operations."""
    retry_interval = 0.1
    timeout = 10.0
    stale_lock_timeout = 300.0  # 5 minutes - consider lock stale after this
    start_time = time.monotonic()

    while True:
        try:
            fd = os.open(lock_file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            # Check if lock file is stale
            try:
                lock_age = time.time() - os.path.getmtime(lock_file_path)
                if lock_age > stale_lock_timeout:
                    # Lock is stale, try to remove it
                    try:
                        os.remove(lock_file_path)
                        print(
                            f"WARNING: Removed stale lock file {lock_file_path} "
                            f"(age: {lock_age:.1f}s)"
                        )
                        continue  # Try to acquire lock again
                    except OSError:
                        pass  # Someone else removed it, continue waiting
            except OSError:
                pass  # Lock file disappeared, continue waiting

            if time.monotonic() - start_time >= timeout:
                raise TimeoutError(
                    f"Could not acquire lock on {lock_file_path} within {timeout} "
                    "seconds."
                )
            time.sleep(retry_interval)

    try:
        yield
    finally:
        try:
            os.remove(lock_file_path)
        except OSError:
            pass


def locked_json_read_modify_write(
    lock_path: str, file_path: str, modifier_func: Callable, default_data=None
):
    """
    A utility to safely read, modify, and write a JSON file under a lock.
    The modifier function can optionally return a tuple of (data_to_write,
    value_to_return).
    """
    with FileLock(lock_path):
        data = default_data
        if os.path.exists(file_path):
            # Avoid race condition by opening file for read first
            content = ""
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if content:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    pass  # data remains default_data if file is corrupt

        if data is None:
            raise FileNotFoundError(
                f"File not found and no default data provided: {file_path}"
            )

        # Apply the modification
        result = modifier_func(data)

        # Unpack result: can be just the modified data, or a tuple
        # (modified_data, value_to_return)
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
    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml_file(file_path: str, data: dict):
    """Writes a dictionary to a YAML file."""
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)


def read_text_file(file_path: str) -> str:
    """Reads a text file and returns its content as a string."""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, encoding="utf-8", errors="ignore") as f:
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
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            try:
                content = f.read()
                if not content:
                    return default_data
                return json.loads(content)
            except json.JSONDecodeError:
                return default_data


def append_to_text_file(file_path: str, content: str):
    """Appends a string to a text file."""
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)


def read_json_file(file_path: str) -> dict:
    """Reads a JSON file and returns its content as a dictionary."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    with open(file_path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in file: {file_path}")


def create_directory(path: str):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def copy_file(source: str, destination: str):
    """Copies a file from source to destination."""
    shutil.copy2(source, destination)


def delete_file(path: str):
    """Deletes a file if it exists."""
    if os.path.exists(path):
        os.remove(path)
