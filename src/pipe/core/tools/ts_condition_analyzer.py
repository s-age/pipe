import json
import os
import subprocess

from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root
from pydantic import BaseModel, Field


class ConditionType(str):
    """TypeScript control flow condition types."""

    IF = "if"
    ELSE_IF = "else_if"
    ELSE = "else"
    FOR = "for"
    WHILE = "while"
    DO_WHILE = "do_while"
    TRY = "try"
    CATCH = "catch"
    FINALLY = "finally"
    SWITCH = "switch"
    CASE = "case"
    TERNARY = "ternary"


class MockCandidate(BaseModel):
    """Potential dependency to mock."""

    name: str = Field(..., description="Call name (e.g., this.repo.save)")
    lineno: int
    end_lineno: int | None = None
    is_method_call: bool = Field(..., description="True if it is a this.xxx call")


class BranchInfo(BaseModel):
    """Control flow branch information."""

    type: str
    lineno: int
    end_lineno: int | None = None
    condition_code: str | None = Field(None, description="Source code of the condition")


class FunctionAnalysis(BaseModel):
    """Analysis result for a single function."""

    name: str
    lineno: int
    end_lineno: int | None
    parameters: list[str] = Field(default_factory=list, description="Parameter list")
    branches: list[BranchInfo] = Field(
        default_factory=list, description="Detected branches"
    )
    mock_candidates: list[MockCandidate] = Field(
        default_factory=list, description="Detected mock candidates"
    )
    cyclomatic_complexity: int = Field(0, description="Cyclomatic complexity")
    is_async: bool = Field(False, description="Whether the function is async")
    is_arrow_function: bool = Field(
        False, description="Whether the function is an arrow function"
    )


class AnalyzeConditionResult(BaseModel):
    """Result of the condition analysis tool."""

    file_path: str
    functions: list[FunctionAnalysis] = Field(default_factory=list)
    error: str | None = None


def ts_condition_analyzer(
    file_path: str, function_name: str | None = None
) -> ToolResult[AnalyzeConditionResult]:
    """
    Analyzes a TypeScript file to extract control flow conditions and mock candidates.

    Args:
        file_path: Path to the TypeScript file.
        function_name: Optional function name to filter analysis.

    Returns:
        ToolResult containing detailed analysis of conditions and mock candidates.
    """
    if "node_modules" in os.path.normpath(file_path):
        return ToolResult(
            error=f"Operation on 'node_modules' is not allowed: {file_path}"
        )

    if not os.path.exists(file_path):
        return ToolResult(error=f"File not found: {file_path}")

    if not (file_path.endswith(".ts") or file_path.endswith(".tsx")):
        return ToolResult(error=f"Not a TypeScript file: {file_path}")

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
            "analyze_conditions",
            file_path,
            function_name or "",
        ]

        process = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=project_root
        )

        output = json.loads(process.stdout)

        if "error" in output:
            return ToolResult(error=output["error"])

        # Parse the output into our models
        result = AnalyzeConditionResult(
            file_path=output["file_path"],
            error=output.get("error"),
        )

        for func_data in output.get("functions", []):
            branches = [
                BranchInfo(
                    type=b["type"],
                    lineno=b["lineno"],
                    end_lineno=b.get("end_lineno"),
                    condition_code=b.get("condition_code"),
                )
                for b in func_data.get("branches", [])
            ]

            mock_candidates = [
                MockCandidate(
                    name=m["name"],
                    lineno=m["lineno"],
                    end_lineno=m.get("end_lineno"),
                    is_method_call=m["is_method_call"],
                )
                for m in func_data.get("mock_candidates", [])
            ]

            result.functions.append(
                FunctionAnalysis(
                    name=func_data["name"],
                    lineno=func_data["lineno"],
                    end_lineno=func_data.get("end_lineno"),
                    parameters=func_data.get("parameters", []),
                    branches=branches,
                    mock_candidates=mock_candidates,
                    cyclomatic_complexity=func_data.get("cyclomatic_complexity", 0),
                    is_async=func_data.get("is_async", False),
                    is_arrow_function=func_data.get("is_arrow_function", False),
                )
            )

        if function_name and not result.functions:
            return ToolResult(
                error=f"Function '{function_name}' not found in {file_path}"
            )

        return ToolResult(data=result)

    except subprocess.CalledProcessError as e:
        return ToolResult(error=f"ts_analyzer.ts failed: {e.stderr.strip()}")
    except json.JSONDecodeError:
        return ToolResult(
            error=(
                "Failed to parse JSON output from ts_analyzer.ts: "
                f"{process.stdout.strip()}"
            )
        )
    except Exception as e:
        return ToolResult(error=f"An unexpected error occurred: {e}")
