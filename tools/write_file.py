import os
from pathlib import Path
from typing import Dict, Any
import difflib

def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Writes content to a specified file.
    """
    try:
        target_path = Path(file_path).resolve()
        project_root = Path(os.getcwd()).resolve()

        # Filesystem Safety Check
        BLOCKED_PATHS = [
            project_root / ".git",
            project_root / ".env",
            project_root / "setting.yml",
            project_root / "__pycache__",
            project_root / "tools.json",
            project_root / "roles",
            project_root / "rules",
            project_root / "sessions",
            project_root / "src",
            project_root / "templates",
            project_root / "venv",
            # Add other sensitive files/directories as needed
        ]

        # Ensure the target path is not a blocked path or within a blocked directory
        for blocked_path in BLOCKED_PATHS:
            if target_path == blocked_path or target_path.is_relative_to(blocked_path):
                return {"error": f"Operation on sensitive path {file_path} is not allowed."}

        # Ensure the target path is within the project root
        if not target_path.is_relative_to(project_root):
            return {"error": f"Writing outside project root is not allowed: {file_path}"}

        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        original_content = ""
        if target_path.exists():
            original_content = target_path.read_text(encoding='utf-8')

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        diff = ""
        if original_content:
            diff_lines = difflib.unified_diff(
                original_content.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm=''
            )
            diff = "\n".join(list(diff_lines))

        message = f"File written successfully: {file_path}"
        if diff:
            message += f"\n\nDiff:\n```diff\n{diff}\n```"

        return {"status": "success", "message": message}
    except Exception as e:
        return {"error": f"Failed to write file {file_path}: {str(e)}"}
