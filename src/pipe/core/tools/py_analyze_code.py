import ast
from pathlib import Path

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.tool_result import ToolResult
from pydantic import BaseModel, Field


class MethodInfo(BaseModel):
    """Information about a method or function."""

    name: str
    lineno: int
    end_lineno: int | None = None
    docstring: str | None = None
    signature: str | None = None
    parameters: list[str] = Field(default_factory=list)
    return_type: str | None = None


class PropertyInfo(BaseModel):
    """Information about a class property."""

    name: str
    lineno: int
    end_lineno: int | None = None
    type_hint: str | None = None
    is_property_decorator: bool = False


class ClassInfo(BaseModel):
    """Information about a class."""

    name: str
    lineno: int
    end_lineno: int | None = None
    docstring: str | None = None
    properties: list[PropertyInfo] = Field(default_factory=list)
    methods: list[MethodInfo] = Field(default_factory=list)
    base_classes: list[str] = Field(default_factory=list)


class SymbolInfo(BaseModel):
    """Information about a code symbol (for backward compatibility)."""

    name: str
    lineno: int
    end_lineno: int | None = None
    docstring: str | None = None


class FileAnalysisResult(BaseModel):
    """Result from analyzing a single Python file."""

    file_path: str
    classes: list[ClassInfo] = Field(default_factory=list)
    functions: list[MethodInfo] = Field(default_factory=list)
    variables: list[SymbolInfo] = Field(default_factory=list)


class AnalyzeCodeResult(BaseModel):
    """Result from analyzing Python code."""

    files: list[FileAnalysisResult] = Field(default_factory=list)
    total_files: int = 0
    error: str | None = None

    # Backward compatibility fields
    classes: list[SymbolInfo] = Field(default_factory=list)
    functions: list[SymbolInfo] = Field(default_factory=list)
    variables: list[SymbolInfo] = Field(default_factory=list)


def _ast_unparse_safe(node: ast.AST) -> str | None:
    """Safely unparse an AST node to string."""
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _extract_method_info(node: ast.FunctionDef | ast.AsyncFunctionDef) -> MethodInfo:
    """Extract detailed information from a function/method node."""
    # Build parameter list
    params = []
    args = node.args

    # Regular arguments
    for arg in args.args:
        param_str = arg.arg
        if arg.annotation:
            type_hint = _ast_unparse_safe(arg.annotation)
            if type_hint:
                param_str += f": {type_hint}"
        params.append(param_str)

    # *args
    if args.vararg:
        vararg_str = f"*{args.vararg.arg}"
        if args.vararg.annotation:
            type_hint = _ast_unparse_safe(args.vararg.annotation)
            if type_hint:
                vararg_str += f": {type_hint}"
        params.append(vararg_str)

    # **kwargs
    if args.kwarg:
        kwarg_str = f"**{args.kwarg.arg}"
        if args.kwarg.annotation:
            type_hint = _ast_unparse_safe(args.kwarg.annotation)
            if type_hint:
                kwarg_str += f": {type_hint}"
        params.append(kwarg_str)

    # Return type
    return_type = None
    if node.returns:
        return_type = _ast_unparse_safe(node.returns)

    # Build signature
    signature = f"{node.name}({', '.join(params)})"
    if return_type:
        signature += f" -> {return_type}"

    return MethodInfo(
        name=node.name,
        lineno=node.lineno,
        end_lineno=node.end_lineno,
        docstring=ast.get_docstring(node),
        signature=signature,
        parameters=params,
        return_type=return_type,
    )


def _extract_class_info(node: ast.ClassDef) -> ClassInfo:
    """Extract detailed information from a class node."""
    properties: list[PropertyInfo] = []
    methods: list[MethodInfo] = []
    base_classes: list[str] = []

    # Extract base classes
    for base in node.bases:
        base_name = _ast_unparse_safe(base)
        if base_name:
            base_classes.append(base_name)

    # Extract class body
    for item in node.body:
        # Methods (including @property decorated ones)
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            is_property = any(
                isinstance(dec, ast.Name) and dec.id == "property"
                for dec in item.decorator_list
            )

            if is_property:
                # Treat @property as a property
                prop = PropertyInfo(
                    name=item.name,
                    lineno=item.lineno,
                    end_lineno=item.end_lineno,
                    type_hint=_ast_unparse_safe(item.returns) if item.returns else None,
                    is_property_decorator=True,
                )
                properties.append(prop)
            else:
                # Regular method
                methods.append(_extract_method_info(item))

        # Class attributes with type hints
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            prop = PropertyInfo(
                name=item.target.id,
                lineno=item.lineno,
                end_lineno=item.end_lineno,
                type_hint=_ast_unparse_safe(item.annotation),
                is_property_decorator=False,
            )
            properties.append(prop)

    return ClassInfo(
        name=node.name,
        lineno=node.lineno,
        end_lineno=node.end_lineno,
        docstring=ast.get_docstring(node),
        properties=properties,
        methods=methods,
        base_classes=base_classes,
    )


def _analyze_single_file(file_path: str, source_code: str) -> FileAnalysisResult | None:
    """Analyze a single Python file and return its symbols."""
    try:
        tree = ast.parse(source_code)
        file_result = FileAnalysisResult(file_path=file_path)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                file_result.classes.append(_extract_class_info(node))
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                file_result.functions.append(_extract_method_info(node))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_info = SymbolInfo(
                            name=target.id,
                            lineno=target.lineno,
                            end_lineno=target.end_lineno,
                        )
                        file_result.variables.append(var_info)

        return file_result

    except SyntaxError:
        return None


def py_analyze_code(path: str, max_files: int = 100) -> ToolResult[AnalyzeCodeResult]:
    """
    Analyzes Python file(s) for symbol information.

    Args:
        path: Path to a Python file or directory
        max_files: Maximum number of files to analyze (default: 100)

    Returns:
        ToolResult containing detailed symbol information including:
        - Classes with properties, methods, and signatures
        - Functions with signatures
        - Module-level variables
    """
    try:
        repo = FileRepositoryFactory.create()

        if not repo.exists(path):
            return ToolResult(error=f"Path not found: {path}")

        files_to_analyze: list[str] = []

        # Determine if path is file or directory
        if repo.is_file(path):
            if not path.endswith(".py"):
                return ToolResult(error=f"Not a Python file: {path}")
            files_to_analyze.append(path)
        else:
            # Directory: get all .py files (non-recursive)
            path_obj = Path(path)
            try:
                py_files = sorted(path_obj.glob("*.py"))
                files_to_analyze = [str(f) for f in py_files]
            except Exception as e:
                return ToolResult(error=f"Failed to list directory: {e}")

            if not files_to_analyze:
                return ToolResult(error=f"No Python files found in directory: {path}")

            if len(files_to_analyze) > max_files:
                return ToolResult(
                    error=f"Too many files ({len(files_to_analyze)}). "
                    f"Maximum allowed: {max_files}. "
                    f"Please specify a more specific path."
                )

        # Analyze all files
        result = AnalyzeCodeResult(total_files=len(files_to_analyze))

        for file_path in files_to_analyze:
            try:
                source_code = repo.read_text(file_path)
                file_result = _analyze_single_file(file_path, source_code)

                if file_result:
                    result.files.append(file_result)

                    # Populate backward compatibility fields (flatten all files)
                    for cls in file_result.classes:
                        result.classes.append(
                            SymbolInfo(
                                name=cls.name,
                                lineno=cls.lineno,
                                end_lineno=cls.end_lineno,
                                docstring=cls.docstring,
                            )
                        )
                    for func in file_result.functions:
                        result.functions.append(
                            SymbolInfo(
                                name=func.name,
                                lineno=func.lineno,
                                end_lineno=func.end_lineno,
                                docstring=func.docstring,
                            )
                        )
                    result.variables.extend(file_result.variables)

            except UnicodeDecodeError:
                continue
            except Exception:
                continue

        if not result.files:
            return ToolResult(
                error=f"No valid Python files could be analyzed in: {path}"
            )

        return ToolResult(data=result)

    except ValueError as e:
        return ToolResult(error=f"Invalid path: {e}")
    except Exception as e:
        return ToolResult(error=f"Failed to analyze code: {e}")
