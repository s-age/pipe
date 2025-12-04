import os
import subprocess
from typing import Any


def py_checker(project_root: str) -> dict[str, Any]:
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
        # Safety check: ensure project_root is within the allowed project root
        allowed_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        abs_project_root = os.path.abspath(project_root)
        if not abs_project_root.startswith(allowed_root):
            return {"error": f"Project root outside allowed directory: {project_root}"}

        if not os.path.isdir(abs_project_root):
            return {"error": f"Project root is not a directory: {project_root}"}

        results: dict[str, Any] = {}

        # Step 1: ruff check --fix
        try:
            process1 = subprocess.run(
                ["ruff", "check", "--fix", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            results["ruff_check"] = {
                "stdout": process1.stdout.strip() if process1.stdout else "",
                "stderr": process1.stderr.strip() if process1.stderr else "",
                "exit_code": process1.returncode,
                "success": process1.returncode == 0,
            }
        except FileNotFoundError:
            return {"error": "ruff command not found. Please install ruff."}
        except Exception as e:
            return {"error": f"Error running ruff check: {str(e)}"}

        # Step 2: ruff format (only if ruff check succeeded or had fixable issues)
        try:
            process2 = subprocess.run(
                ["ruff", "format", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            results["ruff_format"] = {
                "stdout": process2.stdout.strip() if process2.stdout else "",
                "stderr": process2.stderr.strip() if process2.stderr else "",
                "exit_code": process2.returncode,
                "success": process2.returncode == 0,
            }
        except FileNotFoundError:
            return {"error": "ruff command not found. Please install ruff."}
        except Exception as e:
            return {"error": f"Error running ruff format: {str(e)}"}

        # Step 3: mypy
        try:
            process3 = subprocess.run(
                ["mypy", "."],
                capture_output=True,
                text=True,
                cwd=abs_project_root,
                check=False,
            )
            results["mypy"] = {
                "stdout": process3.stdout.strip() if process3.stdout else "",
                "stderr": process3.stderr.strip() if process3.stderr else "",
                "exit_code": process3.returncode,
                "success": process3.returncode == 0,
            }
        except FileNotFoundError:
            return {"error": "mypy command not found. Please install mypy."}
        except Exception as e:
            return {"error": f"Error running mypy: {str(e)}"}

        # Overall success
        all_success = all(
            step["success"] for step in results.values() if "success" in step
        )
        results["overall_success"] = all_success

        return results

    except Exception as e:
        return {"error": f"Unexpected error in py_checker: {str(e)}"}
