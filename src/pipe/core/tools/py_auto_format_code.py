"""
Tool for automatically formatting Python code using Black, isort, and Ruff.
Applies consistent code style, sorts imports, and performs linting/formatting.
"""

import subprocess

from pipe.core.models.results.py_auto_format_code_result import (
    FormatterToolResult,
    PyAutoFormatCodeResult,
)
from pipe.core.models.tool_result import ToolResult


def py_auto_format_code(file_path: str) -> ToolResult[PyAutoFormatCodeResult]:
    """
    Automatically formats the specified Python file using Black, isort, and Ruff.
    """
    results = []

    # 1. Run isort to sort imports
    try:
        isort_command = ["poetry", "run", "isort", file_path]
        isort_result = subprocess.run(
            isort_command, capture_output=True, text=True, check=True
        )
        results.append(
            FormatterToolResult(
                tool="isort",
                stdout=isort_result.stdout,
                stderr=isort_result.stderr,
                exit_code=isort_result.returncode,
                message="isort completed successfully.",
            )
        )
    except subprocess.CalledProcessError as e:
        results.append(
            FormatterToolResult(
                tool="isort",
                stdout=e.stdout,
                stderr=e.stderr,
                exit_code=e.returncode,
                message="An error occurred during isort execution.",
            )
        )
        # If isort fails, we might want to stop or continue. For now, continue.
    except FileNotFoundError:
        results.append(
            FormatterToolResult(
                tool="isort",
                error="isort command not found.",
                message="Please ensure isort is installed and in your PATH.",
            )
        )

    # 2. Run Black to format code
    try:
        black_command = ["poetry", "run", "black", file_path]
        black_result = subprocess.run(
            black_command, capture_output=True, text=True, check=True
        )
        results.append(
            FormatterToolResult(
                tool="black",
                stdout=black_result.stdout,
                stderr=black_result.stderr,
                exit_code=black_result.returncode,
                message="Black completed successfully.",
            )
        )
    except subprocess.CalledProcessError as e:
        results.append(
            FormatterToolResult(
                tool="black",
                stdout=e.stdout,
                stderr=e.stderr,
                exit_code=e.returncode,
                message="An error occurred during Black execution.",
            )
        )
    except FileNotFoundError:
        results.append(
            FormatterToolResult(
                tool="black",
                error="black command not found.",
                message="Please ensure Black is installed and in your PATH.",
            )
        )

    # 3. Run Ruff to format and lint (assuming Ruff is already installed
    # and configured for formatting)
    try:
        # Ruff can act as a formatter as well.
        # We'll run `ruff format` for formatting and `ruff check` for linting.
        ruff_format_command = ["poetry", "run", "ruff", "format", file_path]
        ruff_format_result = subprocess.run(
            ruff_format_command, capture_output=True, text=True, check=True
        )
        results.append(
            FormatterToolResult(
                tool="ruff format",
                stdout=ruff_format_result.stdout,
                stderr=ruff_format_result.stderr,
                exit_code=ruff_format_result.returncode,
                message="Ruff format completed successfully.",
            )
        )

        ruff_check_command = ["poetry", "run", "ruff", "check", file_path]
        ruff_check_result = subprocess.run(
            ruff_check_command, capture_output=True, text=True, check=True
        )
        results.append(
            FormatterToolResult(
                tool="ruff check",
                stdout=ruff_check_result.stdout,
                stderr=ruff_check_result.stderr,
                exit_code=ruff_check_result.returncode,
                message="Ruff check completed successfully.",
            )
        )

    except subprocess.CalledProcessError as e:
        results.append(
            FormatterToolResult(
                tool="ruff",
                stdout=e.stdout,
                stderr=e.stderr,
                exit_code=e.returncode,
                message="An error occurred during Ruff execution.",
            )
        )
    except FileNotFoundError:
        results.append(
            FormatterToolResult(
                tool="ruff",
                error="ruff command not found.",
                message="Please ensure Ruff is installed and in your PATH.",
            )
        )

    result = PyAutoFormatCodeResult(
        formatting_results=results,
        message="Automatic code formatting attempt completed.",
    )
    return ToolResult(data=result)
