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
            "npx",
            "ts-node",
            script_path,
            "get_references",
            file_path,
            symbol_name,
        ]
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=project_root
        )

        if process.stderr.strip():
            # stderrはデバッグ情報なので、エラーとして返さずにログに出力
            print(f"DEBUG (ts_analyzer.ts stderr): {process.stderr.strip()}")

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
        return {"error": f"ts_analyzer.ts failed: {e.stderr.strip()}"}
    except json.JSONDecodeError:
        return {
            "error": (
                f"Failed to parse JSON output from ts_analyzer.ts: "
                f"{process.stdout.strip()}"
            )
        }
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
