import json
import os
import subprocess
from typing import Any


def ts_get_type_definitions(file_path: str, symbol_name: str) -> dict[str, Any]:
    """
    Extracts type definitions for a function, class, or variable within the
    specified TypeScript file using ts-morph for full AST analysis.
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

        command = ["node", script_path, file_path, symbol_name, "get_type_definitions"]
        process = subprocess.run(command, capture_output=True, text=True, check=True)

        output = json.loads(process.stdout)
        if output.get("success"):
            return {"type_definitions": output["data"]}
        else:
            return {"error": output.get("error", "Unknown error from ts_analyzer.js")}

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
