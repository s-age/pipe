"""
Tool for executing and testing TypeScript/JavaScript code.
After code changes, this tool runs the code or executes tests to verify its behavior.
"""

import subprocess
from pathlib import Path

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.results.ts_run_and_test_code_result import TsRunAndTestCodeResult
from pipe.core.models.tool_result import ToolResult


def ts_run_and_test_code(
    file_path: str | None = None,
    test_name: str | None = None,
    test_suite: str | None = None,
) -> ToolResult[TsRunAndTestCodeResult]:
    """
    Executes or tests the specified TypeScript/JavaScript file and returns the results.

    Args:
        file_path: Path to the TypeScript/JavaScript file to execute or test.
            If None, runs all tests in the project using the configured test runner.
        test_name: Name of a specific test case to run (requires file_path).
        test_suite: Name of a specific test suite to run (requires file_path).
    """
    # Create repository (auto-loads project_root and settings)
    repo = FileRepositoryFactory.create()

    # Determine the working directory (src/web for package.json)
    web_dir = Path(__file__).parent.parent.parent.parent.parent / "src" / "web"

    command = []
    abs_file_path = None

    # If file_path is not provided, run all tests
    if file_path is None:
        if test_name or test_suite:
            return ToolResult(
                error=("test_name and test_suite require file_path to be specified.")
            )
        # Run all tests in the project using vitest
        # Use vitest run for single execution (not watch mode)
        command = ["npx", "vitest", "run"]
    else:
        # Security check for file_path
        try:
            # Check file existence and security
            if not repo.exists(file_path):
                return ToolResult(error=f"File not found: {file_path}")
            if not repo.is_file(file_path):
                return ToolResult(error=f"Path is not a file: {file_path}")

            # Get validated absolute path
            abs_file_path = repo.get_absolute_path(file_path)
        except ValueError as e:
            return ToolResult(error=f"Invalid file path: {e}")

        # Check if it's a test file or regular file
        is_test_file = (
            ".test." in abs_file_path
            or ".spec." in abs_file_path
            or abs_file_path.endswith(".test.ts")
            or abs_file_path.endswith(".test.tsx")
            or abs_file_path.endswith(".spec.ts")
            or abs_file_path.endswith(".spec.tsx")
        )

        if is_test_file:
            # Run tests from the specified file
            command = ["npx", "vitest", "run", abs_file_path]

            # Add test name filter if specified
            if test_name:
                command.extend(["-t", test_name])
            elif test_suite:
                command.extend(["-t", test_suite])
        else:
            # For non-test files, execute with ts-node or node
            if abs_file_path.endswith((".ts", ".tsx")):
                # TypeScript file - use ts-node
                command = ["npx", "ts-node", abs_file_path]
            else:
                # JavaScript file - use node
                command = ["node", abs_file_path]

    try:
        result_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(web_dir),
        )
        result = TsRunAndTestCodeResult(
            stdout=result_process.stdout,
            stderr=result_process.stderr,
            exit_code=result_process.returncode,
            message="Code execution or testing completed successfully.",
        )
        return ToolResult(data=result)
    except subprocess.CalledProcessError as e:
        result = TsRunAndTestCodeResult(
            stdout=e.stdout,
            stderr=e.stderr,
            exit_code=e.returncode,
            message="An error occurred during code execution or testing.",
        )
        return ToolResult(data=result)  # Execution failure, but tool ran successfully
    except FileNotFoundError:
        return ToolResult(
            error="Specified file or command not found. Ensure Node.js is installed.",
        )
