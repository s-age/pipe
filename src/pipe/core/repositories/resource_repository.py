"""
Repository for reading and validating external text resources.

Handles access to external files (roles, procedures, etc.) with path
validation to prevent directory traversal attacks and unauthorized access.
"""

from pathlib import Path


class ResourceRepository:
    """
    Manages access to external text resources with strict path validation.

    This repository ensures that all resource access is confined within
    specified root directories and validates paths to prevent traversal attacks.
    """

    def __init__(self, project_root: str):
        """
        Initialize the ResourceRepository.

        Args:
            project_root: The root directory for resource access validation
        """
        self.project_root = Path(project_root).resolve()

    def read_text(self, file_path: str, allowed_root: str | None = None) -> str:
        """
        Read text content from a file with path validation.

        Args:
            file_path: The path to the file to read
            allowed_root: Optional additional allowed root directory.
                         If not provided, defaults to project_root.

        Returns:
            The file content as a string

        Raises:
            ValueError: If the file path is outside the allowed root directory
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        # Determine the allowed root
        root = Path(allowed_root or self.project_root).resolve()

        # Resolve the requested file path
        requested_path = Path(file_path).resolve()

        # Verify the file is within the allowed root
        try:
            requested_path.relative_to(root)
        except ValueError:
            raise ValueError(
                f"Access denied: '{file_path}' is outside the allowed "
                f"root directory '{root}'"
            )

        # Check if file exists
        if not requested_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not requested_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Read and return the file content
        try:
            with open(requested_path, encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            raise OSError(f"Failed to read file '{file_path}': {e}")

    def exists(self, file_path: str, allowed_root: str | None = None) -> bool:
        """
        Check if a file exists with path validation.

        Args:
            file_path: The path to check
            allowed_root: Optional additional allowed root directory

        Returns:
            True if the file exists and is within allowed root, False otherwise
        """
        try:
            root = Path(allowed_root or self.project_root).resolve()
            requested_path = Path(file_path).resolve()

            # Verify the file is within the allowed root
            requested_path.relative_to(root)

            return requested_path.exists() and requested_path.is_file()
        except ValueError:
            # Path is outside allowed root
            return False

    def validate_path(self, file_path: str, allowed_root: str | None = None) -> bool:
        """
        Validate that a path is within the allowed root without accessing the file.

        Args:
            file_path: The path to validate
            allowed_root: Optional additional allowed root directory

        Returns:
            True if the path is within allowed root, False otherwise
        """
        try:
            root = Path(allowed_root or self.project_root).resolve()
            requested_path = Path(file_path).resolve()

            # Try to make the path relative to root
            requested_path.relative_to(root)
            return True
        except ValueError:
            # Path is outside allowed root
            return False

    def get_absolute_path(self, file_path: str, allowed_root: str | None = None) -> str:
        """
        Get the absolute path of a file with validation.

        Args:
            file_path: The path to convert to absolute
            allowed_root: Optional additional allowed root directory

        Returns:
            The absolute path if valid

        Raises:
            ValueError: If the path is outside the allowed root directory
        """
        root = Path(allowed_root or self.project_root).resolve()
        requested_path = Path(file_path).resolve()

        # Verify the file is within the allowed root
        try:
            requested_path.relative_to(root)
        except ValueError:
            raise ValueError(
                f"Access denied: '{file_path}' is outside the allowed "
                f"root directory '{root}'"
            )

        return str(requested_path)
