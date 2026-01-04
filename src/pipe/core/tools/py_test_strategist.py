import ast
import os
from enum import Enum
from pathlib import Path

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_condition_analyzer import py_condition_analyzer
from pydantic import BaseModel, ConfigDict, Field

# Standard library modules that should NOT be mocked
# These are stable, well-tested, and mocking them provides no benefit
STDLIB_BLACKLIST = {
    # Core modules
    "sys",
    "os",
    "pathlib",
    "builtins",
    # Text processing
    "re",
    "json",
    "csv",
    "html",
    "xml",
    # System utilities
    "logging",
    "argparse",
    "subprocess",
    "traceback",
    # Data structures & algorithms
    "collections",
    "itertools",
    "functools",
    "operator",
    # Math & numbers
    "math",
    "decimal",
    "fractions",
    "random",
    # Date & time
    "datetime",
    "time",
    "calendar",
    # File & I/O
    "io",
    "shutil",
    "tempfile",
    # Other common stdlib
    "copy",
    "pickle",
    "struct",
    "codecs",
    "hashlib",
    "uuid",
}


class TestLevel(str, Enum):
    UNIT = "unit"


class MissingCoverage(BaseModel):
    """Represents a gap in test coverage."""

    model_config = ConfigDict(frozen=True)

    type: str = Field(..., description="Type of missing coverage")
    details: str = Field(
        ...,
        description="Detailed description (e.g., 'No test found for function process')",
    )
    lineno: int | None = None


class MockTarget(BaseModel):
    """Mock target with patch path information."""

    model_config = ConfigDict(frozen=True)

    dependency_name: str = Field(
        ..., description="Dependency name (e.g., 'os', 'join', 'requests')"
    )
    patch_path: str = Field(
        ...,
        description="Full patch path for @patch decorator (e.g., 'pipe.core.utils.path.os')",
    )
    import_type: str = Field(
        ...,
        description="Import type: 'module' (import X) or 'from_import' (from X import Y)",
    )
    original_import: str = Field(
        ...,
        description="Original import statement (e.g., 'import os', 'from os.path import join')",
    )


class FunctionStrategy(BaseModel):
    """Test strategy for a specific function."""

    model_config = ConfigDict(frozen=True)

    function_name: str
    recommended_test_level: TestLevel
    existing_test_function: str | None = Field(
        None, description="Name of existing test function (if found)"
    )
    complexity: int = Field(..., description="Cyclomatic complexity")
    missing_coverage: list[MissingCoverage] = Field(
        default_factory=list, description="List of missing test coverage"
    )
    suggested_mocks: list[str] = Field(
        default_factory=list,
        description="[DEPRECATED] List of dependencies that should be mocked. Use mock_targets instead.",
    )
    mock_targets: list[MockTarget] = Field(
        default_factory=list,
        description="Detailed mock targets with patch paths for @patch decorator",
    )


class SerializationHint(BaseModel):
    """Serialization behavior hint for data models."""

    model_config = ConfigDict(frozen=True)

    model_name: str = Field(..., description="Data model name")
    base_class: str = Field(
        ..., description="Base class (e.g., 'CamelCaseModel', 'BaseModel')"
    )
    default_naming_convention: str = Field(
        ...,
        description="Default naming convention to use in tests: 'snake_case' or 'camelCase'",
    )
    serialization_notes: str = Field(
        ...,
        description="Notes about serialization behavior (e.g., camelCase vs snake_case)",
    )
    assertion_examples: list[str] = Field(
        default_factory=list,
        description="Example assertions for testing serialization",
    )


class AdditionalContext(BaseModel):
    """Additional context for test generation."""

    model_config = ConfigDict(frozen=True)

    data_models: dict[str, str] = Field(
        default_factory=dict,
        description="Data model names and their import paths (e.g., {'AgentTask': 'from pipe.core.models import AgentTask'})",
    )
    stdlib_usage: list[str] = Field(
        default_factory=list,
        description="Standard library functions used (informational only, should not be mocked)",
    )
    serialization_hints: list[SerializationHint] = Field(
        default_factory=list,
        description="Hints about data model serialization behavior (camelCase vs snake_case)",
    )


class TestStrategyResult(BaseModel):
    """Overall test strategy result."""

    model_config = ConfigDict(frozen=True)

    target_file_path: str
    corresponding_test_file: str | None = Field(
        None, description="Path to the identified test file"
    )
    strategies: list[FunctionStrategy] = Field(default_factory=list)
    overall_recommendation: str = Field(..., description="Overall recommendation")
    additional_context: AdditionalContext = Field(
        default_factory=AdditionalContext,
        description="Additional context for test generation (e.g., data models, stdlib usage)",
    )
    error: str | None = None


def _is_data_model_import(import_path: str) -> bool:
    """
    Check if the import is from a data model package.

    Args:
        import_path: Original import statement (e.g., 'from pipe.core.models import AgentTask')

    Returns:
        True if it's a data model import
    """
    # Check for common data model patterns
    model_patterns = [
        ".models.",
        ".schemas.",
        "pydantic",
        "dataclasses",
    ]
    return any(pattern in import_path for pattern in model_patterns)


def _is_stdlib_module(import_path: str, dependency_name: str) -> bool:
    """
    Check if the import is from standard library (should not be mocked).

    Args:
        import_path: Original import statement (e.g., 'import os', 'from os.path import join')
        dependency_name: Name of the dependency (e.g., 'os', 'os.path', 'join')

    Returns:
        True if it's a standard library module that should not be mocked
    """
    # Extract base module name from dependency
    # Examples:
    #   - "os" -> "os"
    #   - "os.path" -> "os"
    #   - "join" (from "from os.path import join") -> need to check import_path
    parts = dependency_name.split(".")
    base_module = parts[0]

    # Check if base module is in blacklist
    if base_module in STDLIB_BLACKLIST:
        return True

    # For "from X import Y" style imports, check the module path in import statement
    # Example: "from os.path import join" -> dependency_name="join", need to extract "os" from import_path
    if import_path.startswith("from "):
        # Extract module path: "from os.path import join" -> "os.path"
        import_parts = import_path.split()
        if len(import_parts) >= 4 and import_parts[2] == "import":
            module_path = import_parts[1]
            module_base = module_path.split(".")[0]
            if module_base in STDLIB_BLACKLIST:
                return True

    return False


def _analyze_model_base_class(
    model_name: str, import_path: str
) -> SerializationHint | None:
    """
    Analyze a data model to detect its base class and generate serialization hints.

    Args:
        model_name: Name of the data model (e.g., 'AgentTask')
        import_path: Import statement (e.g., 'from pipe.core.models import AgentTask')

    Returns:
        SerializationHint if the model can be analyzed, None otherwise
    """
    repo = FileRepositoryFactory.create()

    # Extract module path from import statement
    # Example: "from pipe.core.models import AgentTask" -> "pipe.core.models"
    if not import_path.startswith("from "):
        return None

    parts = import_path.split()
    if len(parts) < 4 or parts[2] != "import":
        return None

    module_path = parts[1]

    # Convert module path to file path
    # Example: "pipe.core.models" -> "src/pipe/core/models.py" or "src/pipe/core/models/__init__.py"
    module_parts = module_path.split(".")
    possible_paths = [
        f"src/{'/'.join(module_parts)}.py",
        f"src/{'/'.join(module_parts)}/__init__.py",
    ]

    source_code = None
    for path in possible_paths:
        if repo.exists(path):
            try:
                source_code = repo.read_text(path)
                break
            except Exception:
                continue

    if not source_code:
        return None

    try:
        tree = ast.parse(source_code)
    except Exception:
        return None

    # Find the class definition
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == model_name:
            # Check base classes
            for base in node.bases:
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    # Handle cases like models.CamelCaseModel
                    base_name = base.attr

                if base_name == "CamelCaseModel":
                    # Generate hints for CamelCaseModel
                    return SerializationHint(
                        model_name=model_name,
                        base_class="CamelCaseModel",
                        default_naming_convention="snake_case",
                        serialization_notes=(
                            f"{model_name} inherits from CamelCaseModel. "
                            "Use snake_case by default (model_dump()). "
                            "Only use camelCase with model_dump(by_alias=True) if the implementation explicitly requires it."
                        ),
                        assertion_examples=[
                            f"# Default (snake_case): data = {model_name.lower()}.model_dump()",
                            'assert data["field_name"] == expected_value',
                            f"# If camelCase needed: data = {model_name.lower()}.model_dump(by_alias=True)",
                            'assert data["fieldName"] == expected_value',
                        ],
                    )
                elif base_name == "BaseModel":
                    # Generate hints for regular BaseModel
                    return SerializationHint(
                        model_name=model_name,
                        base_class="BaseModel",
                        default_naming_convention="snake_case",
                        serialization_notes=(
                            f"{model_name} inherits from BaseModel (Pydantic). "
                            "Use snake_case by default (model_dump())."
                        ),
                        assertion_examples=[
                            f"data = {model_name.lower()}.model_dump()",
                            'assert data["field_name"] == expected_value',
                        ],
                    )

    return None


def _get_module_namespace(target_file_path: str) -> str:
    """
    Get the module namespace from file path.

    Args:
        target_file_path: Path to the target Python file

    Returns:
        Module namespace (e.g., 'pipe.core.utils.path' for 'src/pipe/core/utils/path.py')
    """
    target_path = Path(target_file_path).resolve()

    # Find src directory
    parts = target_path.parts
    try:
        src_index = parts.index("src")
        # Extract module path after 'src' and remove .py extension
        module_parts = parts[src_index + 1 : -1]  # Exclude 'src' and filename
        module_parts += (target_path.stem,)  # Add filename without extension
        return ".".join(module_parts)
    except ValueError:
        # If 'src' not found, use the filename as module
        return target_path.stem


def _extract_import_info(target_file_path: str) -> dict[str, MockTarget]:
    """
    Extract import statements and generate patch paths.

    Args:
        target_file_path: Path to the target Python file

    Returns:
        Dictionary mapping dependency names to MockTarget objects
    """
    repo = FileRepositoryFactory.create()

    if not repo.exists(target_file_path):
        return {}

    try:
        source_code = repo.read_text(target_file_path)
        tree = ast.parse(source_code)
    except Exception:
        return {}

    # Get target module namespace for patch paths
    target_module = _get_module_namespace(target_file_path)

    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # Handle: import os, import sys
            for alias in node.names:
                name = alias.asname or alias.name
                imports[name] = MockTarget(
                    dependency_name=name,
                    patch_path=f"{target_module}.{name}",
                    import_type="module",
                    original_import=f"import {alias.name}"
                    + (f" as {alias.asname}" if alias.asname else ""),
                )
        elif isinstance(node, ast.ImportFrom):
            # Handle: from os.path import join, from typing import List
            # Special case: from pipe.core.domains import gemini_api_static_payload
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    # Skip wildcard imports (cannot determine exact names)
                    continue
                name = alias.asname or alias.name
                imports[name] = MockTarget(
                    dependency_name=name,
                    patch_path=f"{target_module}.{name}",
                    import_type="from_import",
                    original_import=f"from {module} import {alias.name}"
                    + (f" as {alias.asname}" if alias.asname else ""),
                )

    return imports


def _find_test_file(target_file_path: str) -> str | None:
    """
    Find the corresponding test file for the target file.

    Args:
        target_file_path: Path to the target Python file

    Returns:
        Test file path (None if not found)
    """
    repo = FileRepositoryFactory.create()
    target_path = Path(target_file_path).resolve()  # Convert to absolute path
    target_name = target_path.stem

    # Test file name patterns to search for
    test_patterns = [
        f"test_{target_name}.py",
        f"{target_name}_test.py",
    ]

    # Find project root by looking for .git directory
    current_dir = target_path.parent
    project_root = None

    while current_dir != current_dir.parent:
        if (current_dir / ".git").exists():
            project_root = current_dir
            break
        current_dir = current_dir.parent

    if not project_root:
        # If .git not found, use target file's directory
        project_root = target_path.parent

    # Search test directories
    possible_test_dirs = [
        project_root / "tests",
        project_root / "test",
        project_root / "src" / "tests",
    ]

    for test_dir in possible_test_dirs:
        if not test_dir.exists():
            continue

        # Recursively search within test directory
        for root, _, files in os.walk(test_dir):
            for pattern in test_patterns:
                if pattern in files:
                    candidate = str(Path(root) / pattern)
                    if repo.exists(candidate):
                        return candidate

    return None


def _extract_test_functions(test_file_path: str) -> list[str]:
    """
    Extract test function names from a test file.

    Args:
        test_file_path: Path to the test file

    Returns:
        List of test function names
    """
    repo = FileRepositoryFactory.create()

    if not repo.exists(test_file_path):
        return []

    try:
        source_code = repo.read_text(test_file_path)
        tree = ast.parse(source_code)
        test_functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.name.startswith("test_"):
                    test_functions.append(node.name)

        return test_functions
    except Exception:
        return []


def _find_matching_test_function(
    function_name: str, test_functions: list[str]
) -> str | None:
    """
    Find a test function that corresponds to the target function.

    Args:
        function_name: Target function name
        test_functions: List of test function names

    Returns:
        Matched test function name (None if not found)
    """
    # Look for exact match (e.g., process -> test_process)
    exact_match = f"test_{function_name}"
    if exact_match in test_functions:
        return exact_match

    # Look for partial match (e.g., process -> test_process_success, test_process_error)
    for test_func in test_functions:
        if function_name.lower() in test_func.lower():
            return test_func

    return None


def _recommend_test_level() -> TestLevel:
    """
    Recommend test level.

    Returns:
        Recommended test level (always UNIT)

    Note:
        Unit tests are recommended as the default. Integration/E2E tests
        should be implemented separately as E2E tests.
    """
    return TestLevel.UNIT


def _generate_overall_recommendation(
    strategies: list[FunctionStrategy], test_file_exists: bool
) -> str:
    """
    Generate overall recommendation.

    Args:
        strategies: List of function strategies
        test_file_exists: Whether test file exists

    Returns:
        Recommendation string
    """
    total_functions = len(strategies)
    tested_functions = sum(
        1 for s in strategies if s.existing_test_function is not None
    )
    untested_functions = total_functions - tested_functions

    recommendations = []

    if not test_file_exists:
        recommendations.append(
            "No test file found. Creating a new test file is recommended."
        )
    elif untested_functions == 0:
        recommendations.append(
            f"All {total_functions} function(s) have corresponding tests."
        )
    else:
        recommendations.append(
            f"{untested_functions}/{total_functions} function(s) are missing tests."
        )

    # Warn about high complexity functions
    high_complexity_funcs = [s for s in strategies if s.complexity > 10]
    if high_complexity_funcs:
        func_names = ", ".join(f.function_name for f in high_complexity_funcs[:3])
        msg = f"{len(high_complexity_funcs)} function(s) have high complexity "
        recommendations.append(msg + f"(e.g., {func_names}). Testing is recommended.")

    # Recommend mocking for functions with dependencies
    funcs_needing_mocks = [s for s in strategies if len(s.suggested_mocks) > 0]
    if funcs_needing_mocks:
        msg = f"{len(funcs_needing_mocks)} function(s) need mocking for dependencies."
        recommendations.append(msg)

    if not recommendations:
        recommendations.append("Test coverage is good.")

    return " ".join(recommendations)


def py_test_strategist(
    target_file_path: str, test_file_path: str | None = None
) -> ToolResult[TestStrategyResult]:
    """
    Formulate a test strategy for a specified Python file.

    Args:
        target_file_path: Path to the target Python implementation file
        test_file_path: Path to the corresponding test file (auto-discovered if omitted)

    Returns:
        ToolResult[TestStrategyResult]: Test strategy analysis result
    """
    repo = FileRepositoryFactory.create()

    # 1. Input validation
    if not repo.exists(target_file_path):
        return ToolResult(
            data=TestStrategyResult(
                target_file_path=target_file_path,
                corresponding_test_file=None,
                overall_recommendation="",
                error=f"File not found: {target_file_path}",
            )
        )

    if not target_file_path.endswith(".py"):
        return ToolResult(
            data=TestStrategyResult(
                target_file_path=target_file_path,
                corresponding_test_file=None,
                overall_recommendation="",
                error=f"Not a Python file: {target_file_path}",
            )
        )

    # 2. Static analysis (using py_condition_analyzer)
    analysis_result = py_condition_analyzer(target_file_path)
    if analysis_result.error or not analysis_result.data:
        return ToolResult(
            data=TestStrategyResult(
                target_file_path=target_file_path,
                corresponding_test_file=None,
                overall_recommendation="",
                error=f"Static analysis failed: {analysis_result.error}",
            )
        )

    condition_analysis = analysis_result.data

    # 3. Extract import information for mock targets
    import_info = _extract_import_info(target_file_path)

    # 4. Identify test file
    if test_file_path is None:
        test_file_path = _find_test_file(target_file_path)

    # 5. Analyze existing tests
    test_functions = []
    if test_file_path:
        test_functions = _extract_test_functions(test_file_path)

    # 6. Collect additional context (data models, stdlib usage)
    data_models: dict[str, str] = {}
    stdlib_usage_set: set[str] = set()

    # Extract data models and stdlib calls from all mock candidates
    for func_analysis in condition_analysis.functions:
        for mc in func_analysis.mock_candidates:
            # Check for data models
            parts = mc.name.split(".")
            if len(parts) > 1:
                base_name = parts[0]
                if base_name in import_info:
                    import_stmt = import_info[base_name].original_import
                    if _is_data_model_import(import_stmt):
                        data_models[base_name] = import_stmt
                    elif _is_stdlib_module(import_stmt, mc.name):
                        # Track stdlib usage (informational only, will not be mocked)
                        stdlib_usage_set.add(mc.name)
            elif mc.name in import_info:
                import_stmt = import_info[mc.name].original_import
                if _is_data_model_import(import_stmt):
                    data_models[mc.name] = import_stmt
                elif _is_stdlib_module(import_stmt, mc.name):
                    # Track stdlib usage (informational only, will not be mocked)
                    stdlib_usage_set.add(mc.name)

    stdlib_usage = sorted(list(stdlib_usage_set))

    # 6.1. Analyze serialization behavior for each data model
    serialization_hints: list[SerializationHint] = []
    for model_name, import_stmt in data_models.items():
        hint = _analyze_model_base_class(model_name, import_stmt)
        if hint:
            serialization_hints.append(hint)

    # 7. Gap analysis (strategy formulation)
    strategies = []
    for func_analysis in condition_analysis.functions:
        # Find matching test function
        matching_test = _find_matching_test_function(func_analysis.name, test_functions)

        # Identify missing coverage
        missing_coverage = []
        if not matching_test:
            missing_coverage.append(
                MissingCoverage(
                    type="missing_test_function",
                    details=f"No test found for function '{func_analysis.name}'",
                    lineno=func_analysis.lineno,
                )
            )

        # Extract mock candidates (for backward compatibility)
        mock_candidates = [mc.name for mc in func_analysis.mock_candidates]

        # Build mock_targets with patch paths (excluding data models and stdlib)
        mock_targets = []
        for mc in func_analysis.mock_candidates:
            # Check if this is an attribute access (e.g., "module.function")
            parts = mc.name.split(".")

            if len(parts) > 1:
                # Attribute access: check if the base is an imported module
                base_name = parts[0]
                if base_name in import_info:
                    import_stmt = import_info[base_name].original_import

                    # Check if it's a data model - skip if true
                    if _is_data_model_import(import_stmt):
                        continue

                    # Check if it's a stdlib module - skip if true
                    if _is_stdlib_module(import_stmt, mc.name):
                        continue

                    # Build patch path: target_module.base_name.attribute
                    target_module = _get_module_namespace(target_file_path)
                    full_path = f"{target_module}.{mc.name}"
                    mock_targets.append(
                        MockTarget(
                            dependency_name=mc.name,
                            patch_path=full_path,
                            import_type="attribute_access",
                            original_import=f"# Attribute access on: {import_stmt}",
                        )
                    )
                else:
                    # Base not found in imports (e.g., self.method_call)
                    # Skip these as they are instance methods, not external dependencies
                    continue
            elif mc.name in import_info:
                import_stmt = import_info[mc.name].original_import

                # Check if it's a data model - skip if true
                if _is_data_model_import(import_stmt):
                    continue

                # Check if it's a stdlib module - skip if true
                if _is_stdlib_module(import_stmt, mc.name):
                    continue

                # Direct import: use the import info
                mock_targets.append(import_info[mc.name])
            else:
                # Fallback: create basic MockTarget without import info
                # This handles cases where dependency is not directly imported
                target_module = _get_module_namespace(target_file_path)
                mock_targets.append(
                    MockTarget(
                        dependency_name=mc.name,
                        patch_path=f"{target_module}.{mc.name}",
                        import_type="unknown",
                        original_import=f"# Not found in imports: {mc.name}",
                    )
                )

        # Recommend test level (always UNIT)
        test_level = _recommend_test_level()

        strategies.append(
            FunctionStrategy(
                function_name=func_analysis.name,
                recommended_test_level=test_level,
                existing_test_function=matching_test,
                complexity=func_analysis.cyclomatic_complexity,
                missing_coverage=missing_coverage,
                suggested_mocks=mock_candidates,  # Deprecated field
                mock_targets=mock_targets,
            )
        )

    # 8. Aggregate results
    overall_recommendation = _generate_overall_recommendation(
        strategies, test_file_path is not None
    )

    # Create additional context
    additional_context = AdditionalContext(
        data_models=data_models,
        stdlib_usage=stdlib_usage,
        serialization_hints=serialization_hints,
    )

    result = TestStrategyResult(
        target_file_path=target_file_path,
        corresponding_test_file=test_file_path,
        strategies=strategies,
        overall_recommendation=overall_recommendation,
        additional_context=additional_context,
    )

    return ToolResult(data=result)
