# Tools Layer

## Purpose

Tools are **executable functions** that the AI can invoke. Each tool is a self-contained capability, from reading files to searching the web. Tools are the AI's hands in the world - they are the only way the AI can interact with the external environment.

## Responsibilities

1. **AI Capabilities** - Provide functions the AI can call
2. **Parameter Validation** - Validate tool inputs
3. **Execution** - Perform the requested action
4. **Result Formatting** - Return results in AI-readable format
5. **Error Handling** - Handle errors gracefully and return error messages

## Characteristics

- ✅ Self-contained functions (one tool per file)
- ✅ Type-annotated parameters for schema generation
- ✅ Docstrings for AI understanding
- ✅ Access to services via context injection
- ✅ Return string results (AI-readable)
- ❌ **NO complex workflows** - tools are atomic actions
- ❌ **NO state** - tools are stateless functions
- ❌ **NO UI** - tools return data, not display

## File Structure

```
tools/
├── __init__.py
├── read_file.py           # Read file contents
├── write_file.py          # Write to file
├── list_directory.py      # List directory contents
├── search_files.py        # Search for files
├── run_command.py         # Execute shell command
├── search_web.py          # Web search
└── ...                    # Each tool is one file
```

## Dependencies

**Allowed:**

- ✅ `services/` - Via context injection (session_service, etc.)
- ✅ `models/` - For type hints (Settings, Session, etc.)
- ✅ `utils/` - For utilities
- ✅ Standard library
- ✅ External libraries (requests, etc.)

**Forbidden:**

- ❌ Direct access to repositories (use services)
- ❌ Direct access to domains (use services)
- ❌ Complex business logic (keep tools simple)

## Template

```python
"""
Tool for [action description].

This tool allows the AI to [specific capability].
"""

from pipe.core.services.session_service import SessionService
from pipe.core.models.settings import Settings


def tool_name(
    # User-provided parameters (visible to AI)
    param1: str,
    param2: int,
    # Context-injected parameters (NOT visible to AI)
    session_service: SessionService | None = None,
    session_id: str | None = None,
    settings: Settings | None = None,
    project_root: str | None = None,
) -> str:
    """
    [Clear, concise description of what this tool does].

    The AI reads this docstring to understand when and how to use the tool.
    Be specific about:
    - What the tool does
    - When to use it
    - What it returns

    Args:
        param1: Description of param1 (what it's for, format, constraints)
        param2: Description of param2

    Returns:
        Description of what is returned (success message, data, etc.)

    Examples:
        tool_name("example_value", 42)
    """
    try:
        # 1. Validate inputs
        if not param1:
            return "Error: param1 cannot be empty"

        if param2 < 0:
            return "Error: param2 must be non-negative"

        # 2. Execute action
        result = _perform_action(param1, param2)

        # 3. Format and return result
        return f"Success: {result}"

    except Exception as e:
        # 4. Handle errors gracefully
        return f"Error: {str(e)}"


def _perform_action(param1: str, param2: int) -> str:
    """
    Internal helper function.

    Private functions (prefixed with _) are not exposed as tools.
    """
    # Implementation
    return f"Processed {param1} with {param2}"
```

## Real Examples

### read_file.py - Read File Contents

**Key Characteristics:**

- Reads file from project directory
- Supports line range selection
- Returns file contents as string
- Handles file not found errors

```python
"""
Tool for reading file contents.

This tool allows the AI to read text files from the project directory.
"""

import os


def read_file(
    file_path: str,
    start_line: int = 1,
    end_line: int = -1,
    project_root: str = "",
) -> str:
    """
    Reads contents of a file from the project directory.

    Use this tool to read source code, configuration files, documentation,
    or any other text file in the project. You can read the entire file
    or specify a line range.

    Args:
        file_path: Relative path to file from project root (e.g., "src/main.py")
        start_line: Starting line number (1-indexed, default: 1)
        end_line: Ending line number (-1 for entire file, default: -1)

    Returns:
        File contents as string, or error message if file not found

    Examples:
        read_file("src/main.py")  # Read entire file
        read_file("src/main.py", 10, 20)  # Read lines 10-20
    """
    try:
        # Build full path
        full_path = os.path.join(project_root, file_path)

        # Check if file exists
        if not os.path.exists(full_path):
            return f"Error: File not found: {file_path}"

        # Check if it's a file (not directory)
        if not os.path.isfile(full_path):
            return f"Error: Path is not a file: {file_path}"

        # Read file
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Handle line range
        if end_line == -1:
            end_line = len(lines)

        # Validate line numbers
        if start_line < 1 or start_line > len(lines):
            return f"Error: Invalid start_line {start_line} (file has {len(lines)} lines)"

        if end_line < start_line or end_line > len(lines):
            return f"Error: Invalid end_line {end_line}"

        # Get requested lines
        selected_lines = lines[start_line - 1:end_line]
        content = ''.join(selected_lines)

        # Return with metadata
        return f"File: {file_path}\nLines: {start_line}-{end_line}\n\n{content}"

    except UnicodeDecodeError:
        return f"Error: File appears to be binary or uses unsupported encoding: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

### write_file.py - Write File Contents

```python
"""
Tool for writing content to a file.

This tool allows the AI to create or modify text files in the project.
"""

import os


def write_file(
    file_path: str,
    content: str,
    create_dirs: bool = True,
    project_root: str = "",
) -> str:
    """
    Writes content to a file in the project directory.

    Use this tool to create new files or overwrite existing files.
    By default, this creates parent directories if they don't exist.

    Args:
        file_path: Relative path to file from project root (e.g., "src/new_file.py")
        content: Text content to write to the file
        create_dirs: Whether to create parent directories (default: True)

    Returns:
        Success message or error message

    Examples:
        write_file("src/hello.py", "print('Hello, World!')")
    """
    try:
        # Build full path
        full_path = os.path.join(project_root, file_path)

        # Create parent directories if needed
        if create_dirs:
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Return success with file info
        size = len(content)
        lines = content.count('\n') + 1
        return f"Success: Wrote {size} bytes ({lines} lines) to {file_path}"

    except Exception as e:
        return f"Error writing file: {str(e)}"
```

### list_directory.py - List Directory Contents

```python
"""
Tool for listing directory contents.

This tool allows the AI to explore the project directory structure.
"""

import os


def list_directory(
    dir_path: str = ".",
    include_hidden: bool = False,
    project_root: str = "",
) -> str:
    """
    Lists contents of a directory in the project.

    Use this tool to explore the project structure, find files,
    or understand directory organization.

    Args:
        dir_path: Relative path to directory from project root (default: ".")
        include_hidden: Whether to include hidden files/dirs (default: False)

    Returns:
        Formatted list of directory contents, or error message

    Examples:
        list_directory()  # List project root
        list_directory("src")  # List src directory
    """
    try:
        # Build full path
        full_path = os.path.join(project_root, dir_path)

        # Check if directory exists
        if not os.path.exists(full_path):
            return f"Error: Directory not found: {dir_path}"

        # Check if it's a directory
        if not os.path.isdir(full_path):
            return f"Error: Path is not a directory: {dir_path}"

        # List contents
        entries = os.listdir(full_path)

        # Filter hidden files if requested
        if not include_hidden:
            entries = [e for e in entries if not e.startswith('.')]

        # Sort entries
        entries.sort()

        # Separate directories and files
        dirs = []
        files = []

        for entry in entries:
            entry_path = os.path.join(full_path, entry)
            if os.path.isdir(entry_path):
                dirs.append(f"{entry}/")
            else:
                # Get file size
                size = os.path.getsize(entry_path)
                files.append(f"{entry} ({size} bytes)")

        # Format output
        result = [f"Directory: {dir_path}\n"]

        if dirs:
            result.append("Directories:")
            for d in dirs:
                result.append(f"  {d}")
            result.append("")

        if files:
            result.append("Files:")
            for f in files:
                result.append(f"  {f}")

        if not dirs and not files:
            result.append("(Empty directory)")

        return '\n'.join(result)

    except Exception as e:
        return f"Error listing directory: {str(e)}"
```

### search_files.py - Search for Files

```python
"""
Tool for searching files by name pattern.

This tool allows the AI to find files matching a specific pattern.
"""

import os
import fnmatch


def search_files(
    pattern: str,
    dir_path: str = ".",
    recursive: bool = True,
    project_root: str = "",
) -> str:
    """
    Searches for files matching a pattern.

    Use this tool to find files by name or extension when you don't
    know the exact path. Supports wildcards (* and ?).

    Args:
        pattern: Filename pattern with wildcards (e.g., "*.py", "test_*.py")
        dir_path: Directory to search in (default: ".")
        recursive: Whether to search subdirectories (default: True)

    Returns:
        List of matching file paths, or error message

    Examples:
        search_files("*.py")  # Find all Python files
        search_files("test_*.py", "src/tests")  # Find test files
    """
    try:
        # Build full path
        full_path = os.path.join(project_root, dir_path)

        # Check if directory exists
        if not os.path.exists(full_path):
            return f"Error: Directory not found: {dir_path}"

        matches = []

        if recursive:
            # Recursive search
            for root, dirs, files in os.walk(full_path):
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        # Get relative path
                        rel_root = os.path.relpath(root, project_root)
                        rel_path = os.path.join(rel_root, filename)
                        matches.append(rel_path)
        else:
            # Non-recursive search
            for filename in os.listdir(full_path):
                file_path = os.path.join(full_path, filename)
                if os.path.isfile(file_path) and fnmatch.fnmatch(filename, pattern):
                    rel_path = os.path.relpath(file_path, project_root)
                    matches.append(rel_path)

        # Format output
        if not matches:
            return f"No files found matching pattern: {pattern}"

        matches.sort()
        result = [f"Found {len(matches)} file(s) matching '{pattern}':\n"]
        for match in matches:
            result.append(f"  {match}")

        return '\n'.join(result)

    except Exception as e:
        return f"Error searching files: {str(e)}"
```

### run_command.py - Execute Shell Command

```python
"""
Tool for executing shell commands.

This tool allows the AI to run shell commands in the project directory.
USE WITH CAUTION - this can modify the system.
"""

import subprocess
import shlex


def run_command(
    command: str,
    timeout: int = 30,
    project_root: str = "",
) -> str:
    """
    Executes a shell command in the project directory.

    Use this tool to run CLI commands, build scripts, tests, etc.
    The command runs in the project root directory.

    ⚠️ CAUTION: This can modify files and system state. Use carefully.

    Args:
        command: Shell command to execute (e.g., "ls -la", "python test.py")
        timeout: Maximum execution time in seconds (default: 30)

    Returns:
        Command output (stdout and stderr), or error message

    Examples:
        run_command("ls -la")
        run_command("python --version")
    """
    try:
        # Parse command safely
        cmd_parts = shlex.split(command)

        # Execute command
        result = subprocess.run(
            cmd_parts,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Format output
        output_parts = [f"Command: {command}"]
        output_parts.append(f"Exit code: {result.returncode}")

        if result.stdout:
            output_parts.append(f"\nStdout:\n{result.stdout}")

        if result.stderr:
            output_parts.append(f"\nStderr:\n{result.stderr}")

        return '\n'.join(output_parts)

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except FileNotFoundError:
        return f"Error: Command not found: {cmd_parts[0] if cmd_parts else command}"
    except Exception as e:
        return f"Error executing command: {str(e)}"
```

## Tool Schema Generation

The agents layer automatically generates tool schemas from tool functions. The schema is derived from:

1. **Function name** - becomes tool name
2. **Docstring** - becomes tool description
3. **Type hints** - become parameter types
4. **Parameter names** - become parameter names

Example:

```python
def read_file(
    file_path: str,
    start_line: int = 1,
    end_line: int = -1,
    project_root: str = "",  # Context-injected, excluded from schema
) -> str:
    """Reads contents of a file."""
    ...
```

Generates schema:

```json
{
  "name": "read_file",
  "description": "Reads contents of a file.",
  "parameters": {
    "type": "object",
    "properties": {
      "file_path": { "type": "string" },
      "start_line": { "type": "number" },
      "end_line": { "type": "number" }
    },
    "required": ["file_path"]
  }
}
```

**Context-injected parameters** (session_service, project_root, etc.) are automatically excluded from the schema.

## Testing

### Unit Testing Tools

```python
# tests/core/tools/test_read_file.py
import tempfile
import os
from pipe.core.tools.read_file import read_file


def test_read_file_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        # Read file
        result = read_file("test.txt", project_root=tmpdir)

        # Verify
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result


def test_read_file_not_found():
    result = read_file("nonexistent.txt", project_root="/tmp")
    assert "Error" in result
    assert "not found" in result.lower()


def test_read_file_line_range():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

        result = read_file("test.txt", start_line=2, end_line=4, project_root=tmpdir)

        assert "Line 2" in result
        assert "Line 3" in result
        assert "Line 4" in result
        assert "Line 1" not in result
        assert "Line 5" not in result
```

## Best Practices

### 1. Always Return Strings

```python
# ✅ GOOD: Return string result
def read_file(file_path: str) -> str:
    return "File contents here"

# ❌ BAD: Return complex objects
def read_file(file_path: str) -> dict:
    return {"content": "...", "metadata": {...}}  # AI can't use this
```

### 2. Handle Errors Gracefully

```python
# ✅ GOOD: Return error as string
def read_file(file_path: str) -> str:
    try:
        # ...
        return content
    except Exception as e:
        return f"Error: {str(e)}"

# ❌ BAD: Let exceptions propagate
def read_file(file_path: str) -> str:
    # ... (no error handling)
    return content  # May raise exception
```

### 3. Clear, Actionable Docstrings

```python
# ✅ GOOD: Clear description with examples
def read_file(file_path: str) -> str:
    """
    Reads contents of a file from the project directory.

    Use this to read source code, configs, or documentation.

    Args:
        file_path: Relative path from project root (e.g., "src/main.py")

    Returns:
        File contents as string

    Examples:
        read_file("src/main.py")
    """
    ...

# ❌ BAD: Vague docstring
def read_file(file_path: str) -> str:
    """Reads a file."""
    ...
```

### 4. Keep Tools Atomic

```python
# ✅ GOOD: Single, focused action
def read_file(file_path: str) -> str:
    """Reads a file."""
    ...

# ❌ BAD: Multiple actions in one tool
def read_and_analyze_file(file_path: str) -> str:
    """Reads file and performs analysis."""
    # Does too much - split into separate tools
    ...
```

## Summary

Tools are the **AI's capabilities**:

- ✅ Self-contained functions
- ✅ Type-annotated for schema generation
- ✅ Clear docstrings for AI understanding
- ✅ Return string results
- ✅ Graceful error handling
- ❌ No complex workflows
- ❌ No state
- ❌ No UI

Tools are the bridge between the AI's intent and the real world.
