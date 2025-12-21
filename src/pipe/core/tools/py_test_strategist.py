import ast
import os
from enum import Enum
from pathlib import Path

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_condition_analyzer import py_condition_analyzer
from pydantic import BaseModel, ConfigDict, Field


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
        default_factory=list, description="List of dependencies that should be mocked"
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
    error: str | None = None


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

    # 3. Identify test file
    if test_file_path is None:
        test_file_path = _find_test_file(target_file_path)

    # 4. Analyze existing tests
    test_functions = []
    if test_file_path:
        test_functions = _extract_test_functions(test_file_path)

    # 5. Gap analysis (strategy formulation)
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

        # Extract mock candidates
        mock_candidates = [mc.name for mc in func_analysis.mock_candidates]

        # Recommend test level (always UNIT)
        test_level = _recommend_test_level()

        strategies.append(
            FunctionStrategy(
                function_name=func_analysis.name,
                recommended_test_level=test_level,
                existing_test_function=matching_test,
                complexity=func_analysis.cyclomatic_complexity,
                missing_coverage=missing_coverage,
                suggested_mocks=mock_candidates,
            )
        )

    # 6. Aggregate results
    overall_recommendation = _generate_overall_recommendation(
        strategies, test_file_path is not None
    )

    result = TestStrategyResult(
        target_file_path=target_file_path,
        corresponding_test_file=test_file_path,
        strategies=strategies,
        overall_recommendation=overall_recommendation,
    )

    return ToolResult(data=result)
