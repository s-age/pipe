import difflib
import os

from pipe.core.models.results.write_file_result import WriteFileResult


def write_file(
    file_path: str, content: str, project_root: str | None = None
) -> WriteFileResult:
    """
    Writes content to a specified file.
    """
    try:
        target_path = os.path.abspath(file_path)

        if project_root:
            project_root = os.path.abspath(project_root)
        else:
            project_root = os.path.abspath(os.getcwd())

        # Filesystem Safety Check
        BLOCKED_PATHS = [
            os.path.join(project_root, ".git"),
            os.path.join(project_root, ".env"),
            os.path.join(project_root, "setting.yml"),
            os.path.join(project_root, "__pycache__"),
            os.path.join(project_root, "roles"),
            os.path.join(project_root, "rules"),
            os.path.join(project_root, "sessions"),
            os.path.join(project_root, "venv"),
            # Add other sensitive files/directories as needed
        ]

        # Ensure the target path is not a blocked path or within a blocked directory
        for blocked_path in BLOCKED_PATHS:
            if target_path == blocked_path or target_path.startswith(
                blocked_path + os.sep
            ):
                return WriteFileResult(
                    status="error",
                    error=f"Operation on sensitive path {file_path} is not allowed.",
                )

        # Ensure the target path is within the project root
        if not target_path.startswith(project_root + os.sep):
            return WriteFileResult(
                status="error",
                error=f"Writing outside project root is not allowed: {file_path}",
            )

        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        original_content = ""
        if os.path.exists(target_path):
            with open(target_path, encoding="utf-8") as f:
                original_content = f.read()

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        diff = None
        if original_content:
            diff_lines = difflib.unified_diff(
                original_content.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm="",
            )
            diff = "\n".join(list(diff_lines))

        message = f"File written successfully: {file_path}"
        if diff:
            message += f"\n\nDiff:\n```diff\n{diff}\n```"

        return WriteFileResult(status="success", message=message, diff=diff)
    except Exception as e:
        return WriteFileResult(
            status="error", error=f"Failed to write file {file_path}: {str(e)}"
        )
