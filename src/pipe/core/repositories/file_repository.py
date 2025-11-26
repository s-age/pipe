"""
Base repository for file-based persistence.
"""

import fcntl
import json
import os
import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any


@contextmanager
def file_lock(lock_path: str, timeout: float = 10.0) -> Generator[None, None, None]:
    """A context manager for acquiring and releasing a file lock with a timeout."""
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    lock_file_descriptor = open(lock_path, "w")
    start_time = time.time()
    try:
        while True:
            try:
                fcntl.flock(lock_file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break  # Lock acquired successfully
            except BlockingIOError:
                if time.time() - start_time >= timeout:
                    raise TimeoutError(
                        f"Could not acquire lock on {lock_path} within "
                        f"{timeout} seconds."
                    )
                time.sleep(0.1)  # Wait a bit before retrying
        yield
    finally:
        fcntl.flock(lock_file_descriptor, fcntl.LOCK_UN)
        lock_file_descriptor.close()
        try:
            os.remove(lock_path)
        except OSError as e:
            print(
                f"Warning: Could not remove lock file {lock_path}: {e}", file=sys.stderr
            )


class FileRepository:
    """
    Provides a base for repositories that interact with the filesystem.
    Handles file locking and JSON serialization/deserialization.
    """

    def _read_json(self, file_path: str, default_data: Any = None) -> Any:
        """Reads and decodes a JSON file."""
        if not os.path.exists(file_path):
            return default_data
        with open(file_path) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_data

    def _write_json(self, file_path: str, data: Any):
        """Encodes and writes data to a JSON file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _locked_read_json(
        self, lock_path: str, file_path: str, default_data: Any = None
    ) -> Any:
        """Reads a JSON file with a file lock."""
        with file_lock(lock_path):
            return self._read_json(file_path, default_data)

    def _locked_write_json(self, lock_path: str, file_path: str, data: Any):
        """Writes to a JSON file with a file lock."""
        with file_lock(lock_path):
            self._write_json(file_path, data)
