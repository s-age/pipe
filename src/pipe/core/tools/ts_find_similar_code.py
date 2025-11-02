import json
import os
import subprocess
from typing import Any


def ts_find_similar_code(
    base_file_path: str,
    symbol_name: str,
    search_directory: str,
    max_results: int = 3,
) -> dict[str, Any]:
    """
    Finds similar TypeScript code snippets based on a given symbol in a base file.
    It uses ts-morph via ts_analyzer.js to extract code snippets and then compares them.
    Also includes the type definitions of the base symbol.
    """
    if "node_modules" in os.path.normpath(
        base_file_path
    ) or "node_modules" in os.path.normpath(search_directory):
        return {
            "error": (
                "Operation on files/directories within 'node_modules' is not allowed."
            )
        }

    if not os.path.exists(base_file_path):
        return {"error": f"Base file not found: {base_file_path}"}
    if not os.path.isdir(search_directory):
        return {"error": f"Search directory not found: {search_directory}"}

    # Calculate project_root internally
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    try:
        # Call ts_analyzer.js with the new find_similar_code action
        command = [
            "node",
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "cli",
                    "ts_analyzer.js",
                )
            ),
            base_file_path,
            symbol_name,
            "find_similar_code",
            search_directory,
            str(max_results),
        ]
        process = subprocess.run(
            command, capture_output=True, text=True, check=False, cwd=project_root
        )

        if process.returncode != 0:
            return {
                "error": process.stderr.strip()
                or f"ts_analyzer.js exited with code {process.returncode}"
            }

        # ts_analyzer.jsからのstderr出力はデバッグ情報として扱う
        if process.stderr.strip():
            print(f"DEBUG (ts_analyzer.js stderr): {process.stderr.strip()}")

        try:
            output = json.loads(process.stdout)
            if output.get("success"):
                return output["data"]
            else:
                return {
                    "error": output.get("error", "Unknown error from ts_analyzer.js")
                }
        except json.JSONDecodeError:
            return {
                "error": (
                    f"Failed to parse JSON output from ts_analyzer.js: "
                    f"{process.stdout.strip()}"
                )
            }

    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
