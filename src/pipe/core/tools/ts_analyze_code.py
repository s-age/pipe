import json
import os
import subprocess
from typing import Any

from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root
from pydantic import BaseModel, Field


class ImportInfo(BaseModel):
    """Information about an import statement."""

    module: str
    named_imports: list[str] = Field(default_factory=list)
    default_import: str | None = None
    namespace_import: str | None = None
    lineno: int


class ExportInfo(BaseModel):
    """Information about an export statement."""

    module: str | None = None
    named_exports: list[str] = Field(default_factory=list)
    lineno: int
    is_re_export: bool = False


class PropertyInfo(BaseModel):
    """Information about a TypeScript property."""

    name: str
    lineno: int
    end_lineno: int
    type_hint: str
    is_static: bool = False
    is_readonly: bool = False
    is_optional: bool = False


class MethodInfo(BaseModel):
    """Information about a TypeScript method."""

    name: str
    lineno: int
    end_lineno: int
    signature: str
    parameters: list[str] = Field(default_factory=list)
    return_type: str
    is_static: bool = False
    is_async: bool = False


class ClassInfo(BaseModel):
    """Information about a TypeScript class."""

    name: str
    lineno: int
    end_lineno: int
    is_exported: bool = False
    is_default_export: bool = False
    base_classes: list[str] = Field(default_factory=list)
    properties: list[PropertyInfo] = Field(default_factory=list)
    methods: list[MethodInfo] = Field(default_factory=list)


class InterfaceInfo(BaseModel):
    """Information about a TypeScript interface."""

    name: str
    lineno: int
    end_lineno: int
    is_exported: bool = False
    is_default_export: bool = False
    extends: list[str] = Field(default_factory=list)
    properties: list[PropertyInfo] = Field(default_factory=list)


class TypeAliasInfo(BaseModel):
    """Information about a TypeScript type alias."""

    name: str
    lineno: int
    end_lineno: int
    is_exported: bool = False
    is_default_export: bool = False
    definition: str


class FunctionInfo(BaseModel):
    """Information about a TypeScript function."""

    name: str
    lineno: int
    end_lineno: int
    is_exported: bool = False
    is_default_export: bool = False
    signature: str
    parameters: list[str] = Field(default_factory=list)
    return_type: str
    is_async: bool = False


class VariableInfo(BaseModel):
    """Information about a TypeScript variable."""

    name: str
    lineno: int
    end_lineno: int
    type_hint: str
    is_exported: bool = False
    declaration_type: str = "unknown"  # const, let, var
    is_arrow_function: bool = False
    parameters: list[str] = Field(default_factory=list)
    return_type: str | None = None


class FileAnalysisResult(BaseModel):
    """Result from analyzing a single TypeScript file."""

    file_path: str
    imports: list[ImportInfo] = Field(default_factory=list)
    exports: list[ExportInfo] = Field(default_factory=list)
    classes: list[ClassInfo] = Field(default_factory=list)
    interfaces: list[InterfaceInfo] = Field(default_factory=list)
    type_aliases: list[TypeAliasInfo] = Field(default_factory=list)
    functions: list[FunctionInfo] = Field(default_factory=list)
    variables: list[VariableInfo] = Field(default_factory=list)


class AnalyzeCodeResult(BaseModel):
    """Result from analyzing TypeScript code."""

    files: list[FileAnalysisResult] = Field(default_factory=list)
    total_files: int = 0
    error: str | None = None


def ts_analyze_code(path: str, max_files: int = 100) -> ToolResult[AnalyzeCodeResult]:
    """
    Analyzes TypeScript file(s) for symbol information.

    Args:
        path: Path to a TypeScript file or directory
        max_files: Maximum number of files to analyze (default: 100)

    Returns:
        ToolResult containing detailed symbol information including:
        - Classes with properties, methods, and signatures
        - Interfaces with properties
        - Type aliases
        - Functions with signatures
        - Variables (including arrow functions)
    """
    if "node_modules" in os.path.normpath(path):
        return ToolResult(
            error=f"Operation on files within 'node_modules' is not allowed: {path}"
        )

    if not os.path.exists(path):
        return ToolResult(error=f"Path not found: {path}")

    path = os.path.abspath(path)

    try:
        # Construct the absolute path to the ts_analyzer.ts script
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "cli", "ts_analyzer.ts"
        )
        script_path = os.path.abspath(script_path)

        # Calculate project_root internally
        project_root = get_project_root()

        # Determine if path is file or directory
        is_file = os.path.isfile(path)

        if is_file:
            if not (path.endswith(".ts") or path.endswith(".tsx")):
                return ToolResult(error=f"Not a TypeScript file: {path}")

            command = [
                "npx",
                "ts-node",
                script_path,
                "analyze_file",
                path,
            ]
        else:
            command = [
                "npx",
                "ts-node",
                script_path,
                "analyze_directory",
                path,
                "",  # symbolName placeholder (not used for analyze_directory)
                "",  # searchDirectory placeholder (not used for analyze_directory)
                str(max_files),
            ]

        process = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=project_root
        )

        output = json.loads(process.stdout)

        if "error" in output:
            return ToolResult(error=output["error"])

        # Parse the output into our models
        if is_file:
            # Single file result
            file_result = _parse_file_result(output)
            result = AnalyzeCodeResult(total_files=1, files=[file_result])
        else:
            # Directory result
            total_files = output.get("total_files", 0)
            files_data = output.get("files", [])
            files = [_parse_file_result(f) for f in files_data]
            result = AnalyzeCodeResult(total_files=total_files, files=files)

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


def _parse_file_result(data: dict[str, Any]) -> FileAnalysisResult:
    """Parse a single file result from JSON data."""
    file_result = FileAnalysisResult(file_path=data["file_path"])

    # Parse imports
    for import_data in data.get("imports", []):
        file_result.imports.append(
            ImportInfo(
                module=import_data["module"],
                named_imports=import_data.get("named_imports", []),
                default_import=import_data.get("default_import"),
                namespace_import=import_data.get("namespace_import"),
                lineno=import_data["lineno"],
            )
        )

    # Parse exports
    for export_data in data.get("exports", []):
        file_result.exports.append(
            ExportInfo(
                module=export_data.get("module"),
                named_exports=export_data.get("named_exports", []),
                lineno=export_data["lineno"],
                is_re_export=export_data.get("is_re_export", False),
            )
        )

    # Parse classes
    for cls_data in data.get("classes", []):
        properties = [
            PropertyInfo(
                name=p["name"],
                lineno=p["lineno"],
                end_lineno=p["end_lineno"],
                type_hint=p["type_hint"],
                is_static=p.get("is_static", False),
                is_readonly=p.get("is_readonly", False),
                is_optional=p.get("is_optional", False),
            )
            for p in cls_data.get("properties", [])
        ]

        methods = [
            MethodInfo(
                name=m["name"],
                lineno=m["lineno"],
                end_lineno=m["end_lineno"],
                signature=m["signature"],
                parameters=m.get("parameters", []),
                return_type=m["return_type"],
                is_static=m.get("is_static", False),
                is_async=m.get("is_async", False),
            )
            for m in cls_data.get("methods", [])
        ]

        file_result.classes.append(
            ClassInfo(
                name=cls_data["name"],
                lineno=cls_data["lineno"],
                end_lineno=cls_data["end_lineno"],
                is_exported=cls_data.get("is_exported", False),
                is_default_export=cls_data.get("is_default_export", False),
                base_classes=cls_data.get("base_classes", []),
                properties=properties,
                methods=methods,
            )
        )

    # Parse interfaces
    for iface_data in data.get("interfaces", []):
        properties = [
            PropertyInfo(
                name=p["name"],
                lineno=p["lineno"],
                end_lineno=p["end_lineno"],
                type_hint=p["type_hint"],
                is_optional=p.get("is_optional", False),
            )
            for p in iface_data.get("properties", [])
        ]

        file_result.interfaces.append(
            InterfaceInfo(
                name=iface_data["name"],
                lineno=iface_data["lineno"],
                end_lineno=iface_data["end_lineno"],
                is_exported=iface_data.get("is_exported", False),
                is_default_export=iface_data.get("is_default_export", False),
                extends=iface_data.get("extends", []),
                properties=properties,
            )
        )

    # Parse type aliases
    for type_data in data.get("type_aliases", []):
        file_result.type_aliases.append(
            TypeAliasInfo(
                name=type_data["name"],
                lineno=type_data["lineno"],
                end_lineno=type_data["end_lineno"],
                is_exported=type_data.get("is_exported", False),
                is_default_export=type_data.get("is_default_export", False),
                definition=type_data["definition"],
            )
        )

    # Parse functions
    for func_data in data.get("functions", []):
        file_result.functions.append(
            FunctionInfo(
                name=func_data["name"],
                lineno=func_data["lineno"],
                end_lineno=func_data["end_lineno"],
                is_exported=func_data.get("is_exported", False),
                is_default_export=func_data.get("is_default_export", False),
                signature=func_data["signature"],
                parameters=func_data.get("parameters", []),
                return_type=func_data["return_type"],
                is_async=func_data.get("is_async", False),
            )
        )

    # Parse variables
    for var_data in data.get("variables", []):
        file_result.variables.append(
            VariableInfo(
                name=var_data["name"],
                lineno=var_data["lineno"],
                end_lineno=var_data["end_lineno"],
                type_hint=var_data["type_hint"],
                is_exported=var_data.get("is_exported", False),
                declaration_type=var_data.get("declaration_type", "unknown"),
                is_arrow_function=var_data.get("is_arrow_function", False),
                parameters=var_data.get("parameters", []),
                return_type=var_data.get("return_type"),
            )
        )

    return file_result
