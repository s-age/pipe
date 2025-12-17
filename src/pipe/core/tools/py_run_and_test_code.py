"""
Tool for executing and testing Python code.
After code changes, this tool runs the code or executes tests to verify its behavior.
"""

import os
import subprocess
import tempfile

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.results.py_run_and_test_code_result import (
    PyRunAndTestCodeResult,
)
from pipe.core.models.tool_result import ToolResult


def py_run_and_test_code(
    file_path: str,
    function_name: str | None = None,
    test_case_name: str | None = None,
) -> ToolResult[PyRunAndTestCodeResult]:
    """
    Executes or tests the specified Python file and returns the results.
    """
    # file_path のセキュリティチェック
    try:
        # Create repository (auto-loads project_root and settings)
        repo = FileRepositoryFactory.create()

        # ファイルの存在確認とセキュリティチェック
        if not repo.exists(file_path):
            return ToolResult(error=f"File not found: {file_path}")
        if not repo.is_file(file_path):
            return ToolResult(error=f"Path is not a file: {file_path}")

        # 検証済みの絶対パスを取得
        abs_file_path = repo.get_absolute_path(file_path)
    except ValueError as e:
        return ToolResult(error=f"Invalid file path: {e}")

    command = []
    temp_script = None

    try:
        if test_case_name:
            # Use pytest to run a specific test case
            command = ["pytest", abs_file_path, "-k", test_case_name]
        elif function_name:
            # Create and run a temporary script to execute a specific function
            module_name = os.path.basename(abs_file_path).replace(".py", "")
            temp_script_content = (
                f"from {module_name} import {function_name}\n{function_name}()\n"
            )

            # Use tempfile for cross-platform compatibility and security
            temp_script = tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            )
            temp_script.write(temp_script_content)
            temp_script.close()

            command = ["python", temp_script.name]
        else:
            # Execute the entire file
            command = ["python", abs_file_path]

        result_process = subprocess.run(
            command, capture_output=True, text=True, check=True
        )
        result = PyRunAndTestCodeResult(
            stdout=result_process.stdout,
            stderr=result_process.stderr,
            exit_code=result_process.returncode,
            message="Code execution or testing completed successfully.",
        )
        return ToolResult(data=result)
    except subprocess.CalledProcessError as e:
        result = PyRunAndTestCodeResult(
            stdout=e.stdout,
            stderr=e.stderr,
            exit_code=e.returncode,
            message="An error occurred during code execution or testing.",
        )
        return ToolResult(data=result)  # Execution failure, but tool ran successfully
    except FileNotFoundError:
        return ToolResult(
            error="Specified file or command not found.",
        )
    finally:
        # Clean up temporary file
        if temp_script and os.path.exists(temp_script.name):
            try:
                os.unlink(temp_script.name)
            except Exception:
                pass  # Ignore cleanup errors
