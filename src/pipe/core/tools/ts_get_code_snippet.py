import os
import subprocess
from typing import Any


def ts_get_code_snippet(file_path: str, symbol_name: str) -> dict[str, Any]:
    """
    Extracts a code snippet for a specific symbol from the given TypeScript file
    using ts-morph for full AST analysis.
    """
    if "node_modules" in os.path.normpath(file_path):
        return {
            "error": (
                f"Operation on files within 'node_modules' is not allowed: "
                f"{file_path}"
            )
        }

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    file_path = os.path.abspath(file_path)

    try:
        # Construct the absolute path to the ts_analyzer.ts script
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "cli", "ts_analyzer.ts"
        )
        script_path = os.path.abspath(script_path)

        # Calculate project_root internally
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )

        command = [
            "npx", "ts-node", script_path, file_path, symbol_name, "get_code_snippet"
        ]
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=project_root
        )

        snippet = process.stdout.strip()
        if snippet:
            return {"snippet": snippet}
        else:
            return {"error": "No code snippet found."}

    except subprocess.CalledProcessError as e:
        return {"error": f"ts_analyzer.ts failed: {e.stderr.strip()}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
