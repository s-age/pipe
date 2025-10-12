import os
from pathlib import Path
from typing import Dict, Any

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

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"status": "success", "message": f"File written successfully: {file_path}"}
    except Exception as e:
        return {"error": f"Failed to write file {file_path}: {str(e)}"}

