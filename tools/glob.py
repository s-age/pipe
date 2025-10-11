from typing import Union

def glob(
    pattern: str,
    case_sensitive: Union[bool, None] = None,
    path: Union[str, None] = None,
    respect_gemini_ignore: Union[bool, None] = None,
    respect_git_ignore: Union[bool, None] = None,
) -> dict:
  """Efficiently finds files matching specific glob patterns (e.g., `src/**/*.ts`, `**/*.md`), returning absolute paths sorted by modification time (newest first). Ideal for quickly locating files based on their name or path structure, especially in large codebases.

  Args:
    pattern: The glob pattern to match against (e.g., '**/*.py', 'docs/*.md').
    case_sensitive: Optional: Whether the search should be case-sensitive. Defaults to false.
    path: Optional: The absolute path to the directory to search within. If omitted, searches the root directory.
    respect_gemini_ignore: Optional: Whether to respect .geminiignore patterns when finding files. Defaults to true.
    respect_git_ignore: Optional: Whether to respect .gitignore patterns when finding files. Only available in git repositories. Defaults to true.
  """
  # This function is a stub for actual file system operations.
  # Actual file system operations must be implemented in the environment that calls this function.

  return {"glob_response": {"output": f"Globbing for {pattern} in {path} (stub)"}}
