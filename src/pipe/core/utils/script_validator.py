"""Script path validation for security.

Environment: Poetry-managed Python project
"""

from pathlib import Path


class ScriptValidationError(Exception):
    """Script validation error"""

    pass


def validate_script_path(script_name: str, project_root: str) -> Path:
    """
    Validate script path and return normalized absolute path.

    Args:
        script_name: Script name (e.g., "lint_with_retry.sh")
        project_root: Project root path

    Returns:
        Validated absolute path

    Raises:
        ScriptValidationError: Path traversal attack detected
        FileNotFoundError: Script does not exist

    Security:
        - Prevents path traversal attacks (../etc/passwd, etc.)
        - Rejects access to files outside scripts/ directory
        - Prevents symlink-based escapes
    """
    # Get absolute path to scripts directory
    scripts_dir = (Path(project_root) / "src/pipe/scripts").resolve()

    # Check for invalid characters in script name
    if "/" in script_name or "\\" in script_name or ".." in script_name:
        raise ScriptValidationError(f"Invalid characters in script name: {script_name}")

    # Construct absolute path and normalize
    script_path = (scripts_dir / script_name).resolve()

    # Strictly verify that normalized path is within scripts_dir
    # Requires Python 3.9+ for Path.is_relative_to()
    try:
        if not script_path.is_relative_to(scripts_dir):
            raise ScriptValidationError(
                f"Path traversal detected: {script_name} resolves to {script_path}"
            )
    except ValueError:
        # Fallback for Python 3.8 (should not occur in this project)
        raise ScriptValidationError(
            f"Path validation failed: {script_name} (Python 3.9+ required)"
        )

    # Verify file exists
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Verify it's a regular file (not directory or symlink)
    if not script_path.is_file():
        raise ScriptValidationError(f"Not a regular file: {script_path}")

    return script_path
