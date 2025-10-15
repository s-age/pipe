import os
from pathlib import Path
from typing import Dict, Any
import difflib

def replace(file_path: str, instruction: str, old_string: str, new_string: str) -> Dict[str, Any]:
    """
    Replaces text within a file.
    """
    try:
        target_path = Path(file_path).resolve()
        project_root = Path(os.getcwd()).resolve()

        # Filesystem Safety Check (similar to write_file)
        BLOCKED_PATHS = [
            project_root / ".git",
            project_root / ".env",
            project_root / "setting.yml",
            project_root / "__pycache__",
            project_root / "roles",
            project_root / "rules",
            project_root / "sessions",
            project_root / "venv",
        ]

        for blocked_path in BLOCKED_PATHS:
            if target_path == blocked_path or target_path.is_relative_to(blocked_path):
                return {"error": f"Operation on sensitive path {file_path} is not allowed."}

        if not target_path.is_relative_to(project_root):
            return {"error": f"Modifying files outside project root is not allowed: {file_path}"}

        if not target_path.exists():
            return {"error": f"File not found: {file_path}"}
        if not target_path.is_file():
            return {"error": f"Path is not a file: {file_path}"}

        # Read content
        original_content = target_path.read_text(encoding='utf-8')

        # Perform simple string replacement (first occurrence only)
        if old_string not in original_content:
            return {"status": "failed", "message": f"Old string not found in file: {file_path}"}

        new_content = original_content.replace(old_string, new_string, 1)

        # Write back modified content
        target_path.write_text(new_content, encoding='utf-8')
        
        diff = ""
        if original_content != new_content:
            diff_lines = difflib.unified_diff(
                original_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm=''
            )
            diff = "\n".join(list(diff_lines))

        message = f"Text replaced successfully in {file_path}"
        if diff:
            message += f"\n\nDiff:\n```diff\n{diff}\n```"

        return {"status": "success", "message": message}
    except Exception as e:
        return {"error": f"Failed to replace text in file {file_path}: {str(e)}"}
