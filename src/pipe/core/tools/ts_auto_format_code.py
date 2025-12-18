"""
Tool for automatically formatting TypeScript/JavaScript code using Prettier and ESLint.
Applies consistent code style and performs linting/formatting.
"""

import subprocess
from pathlib import Path

from pipe.core.models.results.ts_auto_format_code_result import (
    FormatterToolResult,
    TsAutoFormatCodeResult,
)
from pipe.core.models.tool_result import ToolResult


def ts_auto_format_code(file_path: str) -> ToolResult[TsAutoFormatCodeResult]:
    """
    Formats TypeScript/JavaScript file using Prettier and ESLint.

    Args:
        file_path: Path to the TypeScript/JavaScript file to format.
    """
    results = []

    # Determine the working directory (src/web for package.json)
    web_dir = Path(__file__).parent.parent.parent.parent.parent / "src" / "web"

    # 1. Run Prettier to format code
    try:
        prettier_command = [
            "npx",
            "prettier",
            "--write",
            file_path,
        ]
        prettier_result = subprocess.run(
            prettier_command,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(web_dir),
        )
        results.append(
            FormatterToolResult(
                tool="prettier",
                stdout=prettier_result.stdout,
                stderr=prettier_result.stderr,
                exit_code=prettier_result.returncode,
                message="Prettier completed successfully.",
            )
        )
    except subprocess.CalledProcessError as e:
        results.append(
            FormatterToolResult(
                tool="prettier",
                stdout=e.stdout,
                stderr=e.stderr,
                exit_code=e.returncode,
                message="An error occurred during Prettier execution.",
            )
        )
    except FileNotFoundError:
        results.append(
            FormatterToolResult(
                tool="prettier",
                error="npx/prettier command not found.",
                message="Please ensure Node.js and Prettier are installed.",
            )
        )

    # 2. Run ESLint to lint and fix code
    try:
        eslint_command = [
            "npx",
            "eslint",
            file_path,
            "--fix",
        ]
        eslint_result = subprocess.run(
            eslint_command,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(web_dir),
        )
        results.append(
            FormatterToolResult(
                tool="eslint",
                stdout=eslint_result.stdout,
                stderr=eslint_result.stderr,
                exit_code=eslint_result.returncode,
                message="ESLint completed successfully.",
            )
        )
    except subprocess.CalledProcessError as e:
        # ESLint returns non-zero exit code when there are unfixable issues,
        # but it still may have fixed some issues
        results.append(
            FormatterToolResult(
                tool="eslint",
                stdout=e.stdout,
                stderr=e.stderr,
                exit_code=e.returncode,
                message=(
                    "ESLint completed with warnings/errors. "
                    "Some issues may have been fixed."
                ),
            )
        )
    except FileNotFoundError:
        results.append(
            FormatterToolResult(
                tool="eslint",
                error="npx/eslint command not found.",
                message="Please ensure Node.js and ESLint are installed.",
            )
        )

    result = TsAutoFormatCodeResult(
        formatting_results=results,
        message="Automatic code formatting attempt completed.",
    )
    return ToolResult(data=result)
