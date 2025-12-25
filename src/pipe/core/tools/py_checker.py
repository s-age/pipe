import subprocess

from pipe.core.models.tool_result import ToolResult
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
    black: CheckStepResult | None = None
    mypy: CheckStepResult | None = None
    overall_success: bool = False
    error: str | None = None


def py_checker() -> ToolResult[PyCheckerResult]:
    """
    Runs ALL of the following Python code quality checks and fixes in a
    single execution:

    STEP 0 (Pre-formatting - Silent):
    - isort . (import sorting, output suppressed)
    - black . (code formatting, output suppressed)

    STEP 1-4 (Validation - Reported):
    1. ruff check --fix (lint and auto-fix)
    2. ruff format (code formatting)
    3. black (88-character line length enforcement and formatting)
    4. mypy (type checking)

    IMPORTANT: This tool executes all steps automatically in one call.
    You will receive results for validation steps (1-4) only.
    Pre-formatting results are suppressed to reduce token consumption.

    NOTE: If errors remain after execution, they require manual fixes.
    Running this tool again without making code changes will produce the
    same errors. Only call this tool again after you have manually fixed
    the reported issues.

    This tool performs static analysis on the entire project and may take
    approximately 30 seconds or more to complete, depending on project size.
    Please wait for the complete result and do not call this tool multiple
    times in parallel.

    Returns:
        A dictionary containing the results of each validation step,
        including stdout, stderr, and any errors encountered.
    """
    try:
        # Get project root automatically
        abs_project_root = get_project_root()

        results = PyCheckerResult()

        # STEP 0: Pre-formatting (Silent) - Run isort and black first
        # This ensures files are formatted BEFORE validation checks
        # Output is suppressed to save tokens
        try:
            # Run isort (import sorting)
            subprocess.run(
                ["poetry", "run", "isort", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            # Run black (code formatting)
            subprocess.run(
                ["poetry", "run", "black", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            # Errors in pre-formatting are ignored - validation steps will catch issues
        except Exception:
            # Silently continue - validation steps will report any real issues
            pass

        # Step 1: ruff check --fix
        try:
            process1 = subprocess.run(
                ["poetry", "run", "ruff", "check", "--fix", "."],
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
                ["poetry", "run", "ruff", "format", "."],
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

        # Step 3: black (88-character line length enforcement)
        try:
            process3 = subprocess.run(
                ["poetry", "run", "black", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            results.black = CheckStepResult(
                stdout=process3.stdout.strip() if process3.stdout else "",
                stderr=process3.stderr.strip() if process3.stderr else "",
                exit_code=process3.returncode,
                success=process3.returncode == 0,
            )
        except FileNotFoundError:
            return ToolResult(error="black command not found. Please install black.")
        except Exception as e:
            return ToolResult(error=f"Error running black: {str(e)}")

        # Step 4: mypy
        try:
            process4 = subprocess.run(
                ["poetry", "run", "mypy", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            results.mypy = CheckStepResult(
                stdout=process4.stdout.strip() if process4.stdout else "",
                stderr=process4.stderr.strip() if process4.stderr else "",
                exit_code=process4.returncode,
                success=process4.returncode == 0,
            )
        except FileNotFoundError:
            return ToolResult(error="mypy command not found. Please install mypy.")
        except Exception as e:
            return ToolResult(error=f"Error running mypy: {str(e)}")

        # Overall success
        ruff_check_success = results.ruff_check.success if results.ruff_check else False
        ruff_format_success = (
            results.ruff_format.success if results.ruff_format else False
        )
        black_success = results.black.success if results.black else False
        mypy_success = results.mypy.success if results.mypy else False
        results.overall_success = (
            ruff_check_success
            and ruff_format_success
            and black_success
            and mypy_success
        )

        return ToolResult(data=results)

    except Exception as e:
        return ToolResult(error=f"Unexpected error in py_checker: {str(e)}")
