import os
import subprocess

from pipe.core.models.results.ts_checker_result import (
    CommandCheckResult,
    TSCheckerResult,
)
from pipe.core.models.tool_result import ToolResult


def ts_checker(
    project_root: str | None = None,
    lint_command: str = "npm run lint",
    build_command: str = "npm run build",
) -> ToolResult[TSCheckerResult]:
    """Runs TypeScript lint and build checks and reports any errors or warnings.

    Args:
        project_root: The absolute path to the project root directory.
            Defaults to the current working directory.
        lint_command: The command to run for linting. Defaults to "npm run lint".
        build_command: The command to run for building. Defaults to "npm run build".
    """
    if project_root is None:
        # Auto-detect project root by finding the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        search_dir = current_dir
        for _ in range(5):  # Go up to 5 levels
            if os.path.exists(os.path.join(search_dir, "pyproject.toml")):
                project_root = search_dir
                break
            parent = os.path.dirname(search_dir)
            if parent == search_dir:
                break
            search_dir = parent

        # If pyproject.toml not found, use current directory
        if project_root is None:
            project_root = current_dir

    # Check if src/web exists and use it as the working directory
    web_dir = os.path.join(project_root, "src", "web")
    if os.path.exists(os.path.join(web_dir, "package.json")):
        project_root = web_dir

    results: dict[str, CommandCheckResult] = {}

    def _run_command(command_str: str, command_name: str) -> None:
        try:
            process = subprocess.run(
                command_str,
                shell=True,
                capture_output=True,
                text=True,
                cwd=project_root,
            )
            output = process.stdout + process.stderr
            errors = []
            warnings = []
            for line in output.splitlines():
                if "error" in line.lower():
                    # Ignore rollup-related errors on macOS
                    if (
                        "rollup" in line.lower()
                        or "throw new error" in line.lower()
                        or "requirewithfriendlyerror" in line.lower()
                    ):
                        continue
                    errors.append(line.strip())
                elif "warning" in line.lower():
                    warnings.append(line.strip())
            results[command_name] = CommandCheckResult(errors=errors, warnings=warnings)
        except Exception as e:
            results[command_name] = CommandCheckResult(
                errors=[f"Tool execution error: {e}"], warnings=[]
            )

    _run_command(lint_command, "Lint")
    _run_command(build_command, "Build")

    result = TSCheckerResult(lint=results.get("Lint"), build=results.get("Build"))
    return ToolResult(data=result)
