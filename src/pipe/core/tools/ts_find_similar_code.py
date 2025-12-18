import json
import os
import subprocess

from pipe.core.models.results.ts_find_similar_code_result import (
    SimilarCodeMatch,
    TSFindSimilarCodeResult,
)
from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root


def ts_find_similar_code(
    base_file_path: str,
    symbol_name: str,
    search_directory: str | None = None,
    max_results: int = 3,
) -> ToolResult[TSFindSimilarCodeResult]:
    """
    Finds similar TypeScript code snippets based on a given symbol in a base file.
    It uses ts-morph via ts_analyzer.ts to extract code snippets and then compares them.
    Also includes the type definitions of the base symbol.

    Args:
        base_file_path: The absolute path to the base file containing the symbol.
        symbol_name: The name of the symbol to find similar code for.
        search_directory: The directory to search for similar code.
            Defaults to src/web in the project root.
        max_results: Maximum number of similar code results to return. Defaults to 3.
    """
    # Calculate project_root internally
    project_root = get_project_root()

    # Default search_directory to src/web
    if search_directory is None:
        search_directory = os.path.join(project_root, "src", "web")

    if "node_modules" in os.path.normpath(
        base_file_path
    ) or "node_modules" in os.path.normpath(search_directory):
        return ToolResult(
            error="Operation on files/directories within 'node_modules' is not allowed."
        )

    if not os.path.exists(base_file_path):
        return ToolResult(error=f"Base file not found: {base_file_path}")
    if not os.path.isdir(search_directory):
        return ToolResult(error=f"Search directory not found: {search_directory}")

    base_file_path = os.path.abspath(base_file_path)
    search_directory = os.path.abspath(search_directory)

    try:
        # Call ts_analyzer.ts with the new find_similar_code action
        command = [
            "npx",
            "ts-node",
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "cli",
                    "ts_analyzer.ts",
                )
            ),
            "find_similar_code",
            base_file_path,
            symbol_name,
            search_directory,
            str(max_results),
        ]
        process = subprocess.run(
            command, capture_output=True, text=True, check=False, cwd=project_root
        )

        if process.returncode != 0:
            return ToolResult(
                error=process.stderr.strip()
                or f"ts_analyzer.ts exited with code {process.returncode}"
            )

        # ts_analyzer.tsからのstderr出力はデバッグ情報として扱う
        if process.stderr.strip():
            print(f"DEBUG (ts_analyzer.ts stderr): {process.stderr.strip()}")

        try:
            output = json.loads(process.stdout)

            # Handle case where output is a list instead of a dict
            if isinstance(output, list):
                return ToolResult(
                    error=(
                        f"Unexpected output format from ts_analyzer.ts (got list): "
                        f"{process.stdout.strip()}"
                    )
                )

            if not isinstance(output, dict):
                return ToolResult(
                    error=(
                        f"Unexpected output type from ts_analyzer.ts: "
                        f"{type(output).__name__}"
                    )
                )

            if "error" in output:
                return ToolResult(error=output["error"])

            # Convert dict matches to SimilarCodeMatch instances
            matches = None
            if "matches" in output:
                matches = [SimilarCodeMatch(**match) for match in output["matches"]]
            result = TSFindSimilarCodeResult(
                base_snippet=output.get("base_snippet"),
                base_type_definitions=output.get("base_type_definitions"),
                matches=matches,
            )
            return ToolResult(data=result)
        except json.JSONDecodeError:
            return ToolResult(
                error=(
                    f"Failed to parse JSON output from ts_analyzer.ts: "
                    f"{process.stdout.strip()}"
                )
            )

    except Exception as e:
        return ToolResult(error=f"An unexpected error occurred: {e}")
