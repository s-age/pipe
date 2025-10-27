import difflib
import os


def replace(
    file_path: str, instruction: str, old_string: str, new_string: str
) -> dict[str, str]:
    """
    Replaces text within a file.
    """
    try:
        target_path = os.path.abspath(file_path)
        project_root = os.path.abspath(os.getcwd())

        # Filesystem Safety Check (similar to write_file)
        BLOCKED_PATHS = [
            os.path.join(project_root, ".git"),
            os.path.join(project_root, ".env"),
            os.path.join(project_root, "setting.yml"),
            os.path.join(project_root, "__pycache__"),
            os.path.join(project_root, "roles"),
            os.path.join(project_root, "rules"),
            os.path.join(project_root, "sessions"),
            os.path.join(project_root, "venv"),
        ]

        for blocked_path in BLOCKED_PATHS:
            if target_path == blocked_path or target_path.startswith(blocked_path):
                return {
                    "error": f"Operation on sensitive path {file_path} is not allowed."
                }

        if not target_path.startswith(project_root):
            return {
                "error": (
                    "Modifying files outside project root is not allowed: "
                    f"{file_path}"
                )
            }

        if not os.path.exists(target_path):
            return {"error": f"File not found: {file_path}"}
        if not os.path.isfile(target_path):
            return {"error": f"Path is not a file: {file_path}"}

        # Read content
        with open(target_path, encoding="utf-8") as f:
            original_content = f.read()

        # Perform simple string replacement (first occurrence only)
        if old_string not in original_content:
            return {
                "status": "failed",
                "message": f"Old string not found in file: {file_path}",
            }

        new_content = original_content.replace(old_string, new_string, 1)

        # Write back modified content
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        diff = ""
        if original_content != new_content:
            diff_lines = difflib.unified_diff(
                original_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm="",
            )
            diff = "\n".join(list(diff_lines))

        message = f"Text replaced successfully in {file_path}"
        if diff:
            message += f"\n\nDiff:\n```diff\n{diff}\n```"

        return {"status": "success", "message": message}
    except Exception as e:
        return {"error": f"Failed to replace text in file {file_path}: {str(e)}"}
