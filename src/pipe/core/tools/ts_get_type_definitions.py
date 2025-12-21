import json
import os
import subprocess
from typing import Any, TypedDict

from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root


class TypeDefinitionsResult(TypedDict, total=False):
    """Result from extracting TypeScript type definitions."""

    type_definitions: dict[str, Any]  # TS type system is complex (5-2 Data Boundary)
    error: str


def ts_get_type_definitions(
    file_path: str, symbol_name: str
) -> ToolResult[TypeDefinitionsResult]:
    """
    Extracts type definitions for a function, class, or variable within the
    specified TypeScript file using ts-morph for full AST analysis.
    """
    if "node_modules" in os.path.normpath(file_path):
        return ToolResult(
            error=(
                f"Operation on files within 'node_modules' is not allowed: "
                f"{file_path}"
            )
        )

    if not os.path.exists(file_path):
        return ToolResult(error=f"File not found: {file_path}")

    file_path = os.path.abspath(file_path)

    try:
        # Construct the absolute path to the ts_analyzer.ts script
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "cli", "ts_analyzer.ts"
        )
        script_path = os.path.abspath(script_path)

        # Calculate project_root internally
        project_root = get_project_root()

        command = [
            "npx",
            "ts-node",
            script_path,
            "get_type_definitions",
            file_path,
            symbol_name,
        ]
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=project_root
        )

        output = json.loads(process.stdout)
        if "error" in output:
            return ToolResult(error=output["error"])
        else:
            return ToolResult(data={"type_definitions": output})

    except subprocess.CalledProcessError as e:
        return ToolResult(error=f"ts_analyzer.ts failed: {e.stderr.strip()}")
    except json.JSONDecodeError:
        return ToolResult(
            error=(
                f"Failed to parse JSON output from ts_analyzer.ts: "
                f"{process.stdout.strip()}"
            )
        )
    except Exception as e:
        return ToolResult(error=f"An unexpected error occurred: {e}")
