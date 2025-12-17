import subprocess

from pipe.core.models.tool_result import ToolResult
from pipe.core.repositories.filesystem_repository import FileSystemRepository
from pipe.core.utils.path import get_project_root
from pydantic import BaseModel


class CheckStepResult(BaseModel):
    """Result from a single check step."""

    stdout: str
    stderr: str
    exit_code: int
    success: bool


class PyCheckerResult(BaseModel):
    """Result from running Python code quality checks."""

    ruff_check: CheckStepResult | None = None
    ruff_format: CheckStepResult | None = None
    mypy: CheckStepResult | None = None
    overall_success: bool = False
    error: str | None = None


def py_checker(project_root: str) -> ToolResult[PyCheckerResult]:
    """
    Runs a sequence of Python code quality checks and fixes:
    1. ruff check --fix (lint and auto-fix)
    2. ruff format (code formatting)
    3. mypy (type checking)

    Args:
        project_root: The root directory of the Python project to check.

    Returns:
        A dictionary containing the results of each step, including stdout, stderr,
        and any errors encountered.
    """
    try:
        # Use FileSystemRepository for consistent security checks
        allowed_root = get_project_root()
        repo = FileSystemRepository(allowed_root)

        # Validate and get absolute path
        if not repo.exists(project_root):
            return ToolResult(error=f"Project root does not exist: {project_root}")
        if not repo.is_dir(project_root):
            return ToolResult(error=f"Project root is not a directory: {project_root}")

        abs_project_root = repo.get_absolute_path(project_root)

        results = PyCheckerResult()

        # Step 1: ruff check --fix
        try:
            process1 = subprocess.run(
                ["ruff", "check", "--fix", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            results.ruff_check = CheckStepResult(
                stdout=process1.stdout.strip() if process1.stdout else "",
                stderr=process1.stderr.strip() if process1.stderr else "",
                exit_code=process1.returncode,
                success=process1.returncode == 0,
            )
        except FileNotFoundError:
            return ToolResult(error="ruff command not found. Please install ruff.")
        except Exception as e:
            return ToolResult(error=f"Error running ruff check: {str(e)}")

        # Step 2: ruff format (only if ruff check succeeded or had fixable issues)
        try:
            process2 = subprocess.run(
                ["ruff", "format", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            results.ruff_format = CheckStepResult(
                stdout=process2.stdout.strip() if process2.stdout else "",
                stderr=process2.stderr.strip() if process2.stderr else "",
                exit_code=process2.returncode,
                success=process2.returncode == 0,
            )
        except FileNotFoundError:
            return ToolResult(error="ruff command not found. Please install ruff.")
        except Exception as e:
            return ToolResult(error=f"Error running ruff format: {str(e)}")

        # Step 3: mypy
        try:
            process3 = subprocess.run(
                ["mypy", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            results.mypy = CheckStepResult(
                stdout=process3.stdout.strip() if process3.stdout else "",
                stderr=process3.stderr.strip() if process3.stderr else "",
                exit_code=process3.returncode,
                success=process3.returncode == 0,
            )
        except FileNotFoundError:
            return ToolResult(error="mypy command not found. Please install mypy.")
        except Exception as e:
            return ToolResult(error=f"Error running mypy: {str(e)}")

        # Overall success
        ruff_check_success = (
            results.ruff_check.success if results.ruff_check else False
        )
        ruff_format_success = (
            results.ruff_format.success if results.ruff_format else False
        )
        mypy_success = results.mypy.success if results.mypy else False
        results.overall_success = (
            ruff_check_success and ruff_format_success and mypy_success
        )

        return ToolResult(data=results)

    except ValueError as e:
        # FileSystemRepository validation errors
        return ToolResult(error=f"Invalid project root: {e}")
    except Exception as e:
        return ToolResult(error=f"Unexpected error in py_checker: {str(e)}")
