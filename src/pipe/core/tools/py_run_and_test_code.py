"""
Tool for executing and testing Python code.
After code changes, this tool runs the code or executes tests to verify its behavior.
"""

import os
import subprocess

from pipe.core.models.results.py_run_and_test_code_result import (
    PyRunAndTestCodeResult,
)


def py_run_and_test_code(
    file_path: str,
    function_name: str | None = None,
    test_case_name: str | None = None,
) -> PyRunAndTestCodeResult:
    """
    Executes or tests the specified Python file and returns the results.
    """
    command = []
    if test_case_name:
        # Use pytest to run a specific test case
        command = ["pytest", file_path, "-k", test_case_name]
    elif function_name:
        # Create and run a simple script to execute a specific function
        # This is a simplified approach; a more robust implementation might be needed.
        module_name = os.path.basename(file_path).replace(".py", "")
        temp_script_content = (
            f"from {module_name} import {function_name}\n{function_name}()\n"
        )
        temp_script_path = "/tmp/temp_exec_script.py"
        with open(temp_script_path, "w") as f:
            f.write(temp_script_content)
        command = ["python", temp_script_path]
    else:
        # Execute the entire file
        command = ["python", file_path]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return PyRunAndTestCodeResult(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
            message="Code execution or testing completed successfully.",
        )
    except subprocess.CalledProcessError as e:
        return PyRunAndTestCodeResult(
            stdout=e.stdout,
            stderr=e.stderr,
            exit_code=e.returncode,
            message="An error occurred during code execution or testing.",
        )
    except FileNotFoundError:
        return PyRunAndTestCodeResult(
            error="Specified file or command not found.",
            message="Please check the file path.",
        )
