import re

from typing import Union

def search_file_content(
    pattern: str,
    include: Union[str, None] = None,
    path: Union[str, None] = None,
) -> dict:
  """Searches for a regular expression pattern within the content of files in a specified directory (or current working directory). Can filter files by a glob pattern. Returns the lines containing matches, along with their file paths and line numbers. Total results limited to 20,000 matches like VSCode.

  Args:
    pattern: The regular expression (regex) pattern to search for within file contents (e.g., 'function\s+myFunction', 'import\s+\{.*\}\s+from\s+.*').
    include: Optional: A glob pattern to filter which files are searched (e.g., '*.js', '*.{ts,tsx}', 'src/**'). If omitted, searches all files (respecting potential global ignores).
    path: Optional: The absolute path to the directory to search within. If omitted, searches the current working directory.
  """
  # This function is a stub for actual file system operations.
  # Actual file system operations must be implemented in the environment that calls this function.

  return {"search_file_content_response": {"output": f"Searching for {pattern} in {path} (stub)"}}
