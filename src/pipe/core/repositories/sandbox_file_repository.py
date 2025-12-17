"""
Sandbox-restricted file repository that prevents writes outside project root.
"""

import fnmatch
import glob as std_glob
import os
import subprocess

from pipe.core.repositories.file_repository import FileRepository


class SandboxFileRepository(FileRepository):
    """
    File repository with sandbox restrictions for enhanced security.
    - READ operations: Allowed anywhere (no path restriction)
    - WRITE operations: Restricted to project root only
    """

    def __init__(self, project_root: str):
        super().__init__()
        self.project_root = os.path.abspath(project_root)

        # Paths that are not allowed to be written to
        self.blocked_paths = [
            os.path.join(self.project_root, ".git"),
            os.path.join(self.project_root, ".env"),
            os.path.join(self.project_root, "setting.yml"),
            os.path.join(self.project_root, "__pycache__"),
            os.path.join(self.project_root, "roles"),
            os.path.join(self.project_root, "rules"),
            os.path.join(self.project_root, "sessions"),
            os.path.join(self.project_root, "venv"),
        ]

    def _validate_path_for_write(self, path: str) -> str:
        """
        Validates that the path is within project root for write operations.
        Returns the absolute path.

        Raises:
            ValueError: If path is outside project root or blocked for writing
        """
        abs_path = os.path.abspath(path)

        # Sandbox mode: Write operations must be within project root
        if not abs_path.startswith(self.project_root):
            raise ValueError("Running commands outside project root is not allowed")

        # Check blocked paths
        for blocked in self.blocked_paths:
            if abs_path == blocked or abs_path.startswith(blocked + os.sep):
                raise ValueError(f"Access denied: Writing to {path} is not allowed.")

        return abs_path

    def get_absolute_path(self, path: str, allow_write: bool = False) -> str:
        """
        Returns the validated absolute path.

        For write operations in sandbox mode, validates path is within project root.
        For read operations, returns absolute path without restriction.
        """
        if allow_write:
            return self._validate_path_for_write(path)
        else:
            # Read operations: no sandbox restriction
            return os.path.abspath(path)

    def read_text(
        self,
        path: str,
        encoding: str = "utf-8",
        limit: int | None = None,
        offset: int = 0,
    ) -> str:
        """Reads text content from a file (no sandbox restriction)."""
        abs_path = os.path.abspath(path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {path}")
        if not os.path.isfile(abs_path):
            raise ValueError(f"Path is not a file: {path}")

        with open(abs_path, encoding=encoding) as f:
            if offset > 0 or limit is not None:
                lines = f.readlines()
                start = offset
                end = start + limit if limit is not None else None
                return "".join(lines[start:end])
            else:
                return f.read()

    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """Writes text content to a file (sandbox: must be within project root)."""
        abs_path = self._validate_path_for_write(path)

        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding=encoding) as f:
            f.write(content)

    def exists(self, path: str) -> bool:
        """Checks if a path exists (no sandbox restriction for read)."""
        abs_path = os.path.abspath(path)
        return os.path.exists(abs_path)

    def is_file(self, path: str) -> bool:
        """Checks if a path is a file (no sandbox restriction for read)."""
        abs_path = os.path.abspath(path)
        return os.path.isfile(abs_path)

    def is_dir(self, path: str) -> bool:
        """Checks if a path is a directory (no sandbox restriction for read)."""
        abs_path = os.path.abspath(path)
        return os.path.isdir(abs_path)

    def list_directory(
        self, path: str, ignore: list[str] | None = None
    ) -> tuple[list[str], list[str]]:
        """
        Lists files and directories in a given path (no sandbox restriction for read).
        Returns (files, directories).
        """
        abs_path = os.path.abspath(path)

        if not os.path.isdir(abs_path):
            raise ValueError(f"Path is not a directory: {path}")

        all_entries = os.listdir(abs_path)
        files = []
        directories = []
        ignore_patterns = ignore or []

        for entry in all_entries:
            if any(fnmatch.fnmatch(entry, pattern) for pattern in ignore_patterns):
                continue

            entry_path = os.path.join(abs_path, entry)
            if os.path.isfile(entry_path):
                files.append(entry)
            elif os.path.isdir(entry_path):
                directories.append(entry)

        return sorted(files), sorted(directories)

    def glob(
        self,
        pattern: str,
        search_path: str = ".",
        recursive: bool = True,
        respect_gitignore: bool = True,
    ) -> list[str]:
        """
        Finds files matching a pattern (no sandbox restriction for read).
        Returns absolute paths.
        """
        abs_search_path = os.path.abspath(search_path)

        glob_pattern = os.path.join(abs_search_path, pattern)
        all_files = set(std_glob.glob(glob_pattern, recursive=recursive))

        ignored_files_abs = set()
        if respect_gitignore:
            try:
                git_process = subprocess.run(
                    ["git", "ls-files", "--ignored", "--exclude-standard", "--others"],
                    capture_output=True,
                    text=True,
                    cwd=abs_search_path,
                    check=True,
                )
                ignored_files = set(git_process.stdout.strip().split("\n"))
                ignored_files_abs = {
                    os.path.join(abs_search_path, f) for f in ignored_files
                }
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        matched_files = [f for f in all_files if f not in ignored_files_abs]
        return sorted(matched_files)
