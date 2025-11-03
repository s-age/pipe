import json
import os
import subprocess
from typing import Any


def ts_get_references(file_path: str, symbol_name: str) -> dict[str, Any]:
    """
    Searches for references to a specific symbol within the given TypeScript file
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

    try:
        # Construct the absolute path to the ts_analyzer.js script
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "cli", "ts_analyzer.js"
        )
        script_path = os.path.abspath(script_path)

        # Calculate project_root internally
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )

        command = ["node", script_path, file_path, symbol_name, "get_references"]
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=project_root
        )

        output = json.loads(process.stdout)
        if "error" in output:
            return {"error": output["error"]}
        else:
            return {
                "references": output,
                "symbol_name": symbol_name,
                "reference_count": len(output) if output else 0,
            }

    except subprocess.CalledProcessError as e:
        return {"error": f"ts_analyzer.js failed: {e.stderr.strip()}"}
    except json.JSONDecodeError:
        return {
            "error": (
                f"Failed to parse JSON output from ts_analyzer.js: "
                f"{process.stdout.strip()}"
            )
        }
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
