"""
A utility module for path-related operations.
"""

import os


def get_project_root(
    start_dir: str | None = None, markers: tuple[str, ...] = (".git", "pyproject.toml")
) -> str:
    """
    Finds the project root by searching upward from a starting directory
    for marker files/directories.

    The function traverses up the directory tree from the starting directory
    until it finds a directory containing one of the specified marker files
    or directories. If no marker is found, it falls back to calculating the
    path relative to this script's location.

    Args:
        start_dir: The directory to start searching from. Defaults to the current
            working directory if not specified.
        markers: A tuple of marker file/directory names to search for.
            Defaults to (".git", "pyproject.toml").

    Returns:
        The absolute path to the project root directory.

    Example:
        >>> root = get_project_root()
        >>> print(root)
        /Users/username/project

        >>> root = get_project_root(start_dir="/path/to/subdir")
        >>> print(root)
        /Users/username/project
    """
    if start_dir is None:
        current_dir = os.path.abspath(os.getcwd())
    else:
        current_dir = os.path.abspath(start_dir)

    # Search upward for marker files/directories
    while True:
        for marker in markers:
            if os.path.exists(os.path.join(current_dir, marker)):
                return current_dir

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached filesystem root
            break
        current_dir = parent_dir

    # Fallback: assume project root is 3 levels up from this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
