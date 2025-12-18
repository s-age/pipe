import os
from enum import Enum
from pathlib import Path

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.ts_condition_analyzer import ts_condition_analyzer
from pydantic import BaseModel, ConfigDict, Field


class TestLevel(str, Enum):
    """TypeScript test levels."""

    UNIT = "unit"
    INTEGRATION = "integration"


class TestFramework(str, Enum):
    """Test framework types."""

    JEST = "jest"
    VITEST = "vitest"
    STORYBOOK = "storybook"


class MissingCoverage(BaseModel):
    """Represents a gap in test coverage."""

    model_config = ConfigDict(frozen=True)

    type: str = Field(..., description="Type of missing coverage")
    details: str = Field(
        ...,
        description="Detailed description of the missing coverage",
    )
    lineno: int | None = None


class FunctionStrategy(BaseModel):
    """Test strategy for a specific function."""

    model_config = ConfigDict(frozen=True)

    function_name: str
    recommended_test_level: TestLevel
    recommended_framework: TestFramework
    existing_test_function: str | None = Field(
        None, description="Name of existing test function (if found)"
    )
    existing_story: str | None = Field(
        None, description="Name of existing story (if found)"
    )
    complexity: int = Field(..., description="Cyclomatic complexity")
    missing_coverage: list[MissingCoverage] = Field(
        default_factory=list, description="List of missing test coverage"
    )
    suggested_mocks: list[str] = Field(
        default_factory=list, description="List of dependencies that should be mocked"
    )
    is_custom_hook: bool = Field(
        False, description="Whether the function is a custom hook (use*)"
    )
    is_component: bool = Field(False, description="Whether the function is a component")
    recommended_story_count: int | None = Field(
        None, description="Recommended number of Storybook stories for components"
    )
    existing_story_count: int | None = Field(
        None, description="Actual number of existing stories for components"
    )


class TestStrategyResult(BaseModel):
    """Overall test strategy result."""

    model_config = ConfigDict(frozen=True)

    target_file_path: str
    corresponding_test_file: str | None = Field(
        None, description="Path to the identified test file"
    )
    corresponding_story_file: str | None = Field(
        None, description="Path to the identified Storybook file"
    )
    strategies: list[FunctionStrategy] = Field(default_factory=list)
    overall_recommendation: str = Field(..., description="Overall recommendation")
    error: str | None = None


def _is_custom_hook(function_name: str) -> bool:
    """
    Determine if a function is a custom hook.

    Args:
        function_name: Function name

    Returns:
        True if the function is a custom hook (starts with 'use')
    """
    return function_name.startswith("use") and len(function_name) > 3


def _is_component(function_name: str) -> bool:
    """
    Determine if a function is a React component.

    Args:
        function_name: Function name

    Returns:
        True if the function is a component (starts with uppercase)
    """
    return len(function_name) > 0 and function_name[0].isupper()


def _find_test_file(target_file_path: str) -> str | None:
    """
    Find the corresponding test file for the target file.

    Args:
        target_file_path: Path to the target TypeScript file

    Returns:
        Test file path (None if not found)
    """
    repo = FileRepositoryFactory.create()
    target_path = Path(target_file_path).resolve()  # Convert to absolute path
    target_name = target_path.stem
    target_ext = target_path.suffix  # .ts or .tsx

    # Test file name patterns to search for
    test_patterns = [
        f"{target_name}.test{target_ext}",
        f"{target_name}.spec{target_ext}",
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

    # First, search in the same directory (or __tests__ subdirectory)
    same_dir_candidates = [
        target_path.parent / pattern for pattern in test_patterns
    ] + [target_path.parent / "__tests__" / pattern for pattern in test_patterns]

    for candidate in same_dir_candidates:
        if repo.exists(str(candidate)):
            return str(candidate)

    # Search test directories
    possible_test_dirs = [
        project_root / "tests",
        project_root / "test",
        project_root / "__tests__",
    ]

    for test_dir in possible_test_dirs:
        if not test_dir.exists():
            continue

        # Recursively search within test directory
        for root, _, files in os.walk(test_dir):
            for pattern in test_patterns:
                if pattern in files:
                    candidate_path: str = str(Path(root) / pattern)
                    if repo.exists(candidate_path):
                        return candidate_path

    return None


def _find_story_file(target_file_path: str) -> str | None:
    """
    Find the corresponding Storybook file for the target file.

    Args:
        target_file_path: Path to the target TypeScript file

    Returns:
        Storybook file path (None if not found)
    """
    repo = FileRepositoryFactory.create()
    target_path = Path(target_file_path).resolve()

    # For index.tsx files, use the parent directory name for the story file
    # e.g., components/ToggleSwitch/index.tsx -> ToggleSwitch.stories.tsx
    if target_path.stem == "index":
        component_name = target_path.parent.name
        story_pattern = f"{component_name}.stories.tsx"
    else:
        story_pattern = f"{target_path.stem}.stories.tsx"

    # Search in the same directory (or __stories__ subdirectory)
    same_dir_candidates = [
        target_path.parent / story_pattern,
        target_path.parent / "__stories__" / story_pattern,
    ]

    for candidate in same_dir_candidates:
        if repo.exists(str(candidate)):
            return str(candidate)

    return None


def _extract_test_functions(test_file_path: str) -> list[str]:
    """
    Extract test function names from a test file.

    Args:
        test_file_path: Path to the test file

    Returns:
        List of test function names from the test file
    """
    repo = FileRepositoryFactory.create()

    if not repo.exists(test_file_path):
        return []

    try:
        source_code = repo.read_text(test_file_path)
        test_functions = []

        # Simple regex-like parsing for it() and test() blocks
        lines = source_code.split("\n")
        for line in lines:
            line_stripped = line.strip()
            # Match patterns like: it('test name', ...) or test('test name', ...)
            if (
                line_stripped.startswith("it(")
                or line_stripped.startswith("test(")
                or line_stripped.startswith("it.skip(")
                or line_stripped.startswith("test.skip(")
            ):
                # Extract the test name between quotes
                for quote in ["'", '"', "`"]:
                    if quote in line_stripped:
                        parts = line_stripped.split(quote)
                        if len(parts) >= 2:
                            test_functions.append(parts[1])
                            break

        return test_functions
    except Exception:
        return []


def _extract_stories(story_file_path: str) -> list[str]:
    """
    Extract story names from a Storybook file.

    Args:
        story_file_path: Path to the story file

    Returns:
        List of story names (e.g., ['Default', 'WithLabel', 'Disabled'])
    """
    repo = FileRepositoryFactory.create()

    if not repo.exists(story_file_path):
        return []

    try:
        source_code = repo.read_text(story_file_path)
        stories = []

        # Parse exported story names (e.g., export const Default: Story = ...)
        lines = source_code.split("\n")
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("export const ") and ": Story" in line_stripped:
                # Extract story name between 'export const ' and ':'
                parts = line_stripped.split("export const ")[1].split(":")
                if len(parts) >= 1:
                    story_name = parts[0].strip()
                    stories.append(story_name)

        return stories
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
    # Convert camelCase/PascalCase to lowercase with spaces for matching
    # e.g., handleClick -> handle click
    import re

    def camel_to_words(name: str) -> str:
        # Insert space before uppercase letters
        spaced = re.sub(r"([A-Z])", r" \1", name).strip().lower()
        return spaced

    function_words = camel_to_words(function_name)

    # Look for tests that contain function name words
    for test_func in test_functions:
        test_func_lower = test_func.lower()
        if (
            function_words in test_func_lower
            or function_name.lower() in test_func_lower
        ):
            return test_func

    return None


def _calculate_recommended_story_count(complexity: int, branch_count: int) -> int:
    """
    Calculate the recommended number of Storybook stories based on complexity.

    Args:
        complexity: Cyclomatic complexity
        branch_count: Number of branches in the component

    Returns:
        Recommended number of stories

    Note:
        The calculation considers:
        - Base case (1 story minimum)
        - Branches typically represent conditional rendering or state variations
        - Higher complexity suggests more edge cases to cover
        - Formula: max(3, branch_count + 1) for components with branches
                  or max(2, complexity) for simple components
    """
    if branch_count > 0:
        # If there are branches (conditional rendering), we need stories for each branch
        # Plus a default case
        return max(3, branch_count + 1)
    else:
        # For simple components without branches, complexity-based approach
        # Complexity 1 = 2 stories (default + one variation)
        # Higher complexity = more stories
        return max(2, min(complexity + 1, 5))


def _recommend_test_level_and_framework(
    is_custom_hook: bool, is_component: bool
) -> tuple[TestLevel, TestFramework]:
    """
    Recommend test level and framework based on function type.

    Args:
        is_custom_hook: Whether the function is a custom hook
        is_component: Whether the function is a component

    Returns:
        Tuple of (TestLevel, TestFramework)

    Note:
        - Custom hooks (use*) should always use UNIT tests
        - Components should use Storybook for INTEGRATION tests
        - Other functions default to UNIT tests with Jest/Vitest
    """
    if is_custom_hook:
        return (TestLevel.UNIT, TestFramework.JEST)
    elif is_component:
        return (TestLevel.INTEGRATION, TestFramework.STORYBOOK)
    else:
        return (TestLevel.UNIT, TestFramework.JEST)


def _generate_overall_recommendation(
    strategies: list[FunctionStrategy],
    test_file_exists: bool,
    story_file_exists: bool,
) -> str:
    """
    Generate overall recommendation.

    Args:
        strategies: List of function strategies
        test_file_exists: Whether test file exists
        story_file_exists: Whether story file exists

    Returns:
        Recommendation string
    """
    hooks = [s for s in strategies if s.is_custom_hook]
    components = [s for s in strategies if s.is_component]
    others = [s for s in strategies if not s.is_custom_hook and not s.is_component]

    tested_hooks = sum(1 for h in hooks if h.existing_test_function is not None)
    storied_components = sum(1 for c in components if c.existing_story is not None)
    tested_others = sum(1 for o in others if o.existing_test_function is not None)

    recommendations = []

    # Hook recommendations
    if hooks:
        untested_hooks = len(hooks) - tested_hooks
        if untested_hooks > 0:
            recommendations.append(
                f"{untested_hooks}/{len(hooks)} custom hook(s) are missing unit tests."
            )
        elif not test_file_exists:
            msg = f"{len(hooks)} custom hook(s) found but no test file exists. "
            recommendations.append(msg + "Creating unit tests is recommended.")

    # Component recommendations
    if components:
        unstoried_components = len(components) - storied_components
        insufficient_stories = [
            c
            for c in components
            if c.existing_story_count is not None
            and c.recommended_story_count is not None
            and c.existing_story_count < c.recommended_story_count
        ]

        if unstoried_components > 0:
            msg = f"{unstoried_components}/{len(components)} component(s) are missing "
            recommendations.append(msg + "Storybook stories.")
        elif insufficient_stories:
            total_missing = sum(
                (c.recommended_story_count or 0) - (c.existing_story_count or 0)
                for c in insufficient_stories
            )
            msg = f"{len(insufficient_stories)} component(s) need {total_missing} "
            recommendations.append(msg + "more stories to reach recommended coverage.")
        elif not story_file_exists:
            msg = f"{len(components)} component(s) found but no story file exists. "
            recommendations.append(msg + "Creating Storybook stories is recommended.")

    # Other function recommendations
    if others:
        untested_others = len(others) - tested_others
        if untested_others > 0:
            recommendations.append(
                f"{untested_others}/{len(others)} function(s) are missing unit tests."
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


def ts_test_strategist(
    target_file_path: str,
    test_file_path: str | None = None,
    story_file_path: str | None = None,
) -> ToolResult[TestStrategyResult]:
    """
    Formulate a test strategy for a specified TypeScript file.

    Args:
        target_file_path: Path to the target TypeScript implementation file
        test_file_path: Path to the corresponding test file (auto-discovered if omitted)
        story_file_path: Path to the corresponding Storybook file (auto-discovered)

    Returns:
        ToolResult[TestStrategyResult]: Test strategy analysis result

    Note:
        - Custom hooks (functions starting with 'use') are recommended for UNIT tests
        - React components (PascalCase) recommended for Storybook INTEGRATION tests
        - Other functions default to UNIT tests
    """
    repo = FileRepositoryFactory.create()

    # 1. Input validation
    if not repo.exists(target_file_path):
        return ToolResult(
            data=TestStrategyResult(
                target_file_path=target_file_path,
                corresponding_test_file=None,
                corresponding_story_file=None,
                overall_recommendation="",
                error=f"File not found: {target_file_path}",
            )
        )

    if not (target_file_path.endswith(".ts") or target_file_path.endswith(".tsx")):
        return ToolResult(
            data=TestStrategyResult(
                target_file_path=target_file_path,
                corresponding_test_file=None,
                corresponding_story_file=None,
                overall_recommendation="",
                error=f"Not a TypeScript file: {target_file_path}",
            )
        )

    # 2. Static analysis (using ts_condition_analyzer)
    analysis_result = ts_condition_analyzer(target_file_path)
    if analysis_result.error or not analysis_result.data:
        return ToolResult(
            data=TestStrategyResult(
                target_file_path=target_file_path,
                corresponding_test_file=None,
                corresponding_story_file=None,
                overall_recommendation="",
                error=f"Static analysis failed: {analysis_result.error}",
            )
        )

    condition_analysis = analysis_result.data

    # 3. Identify test file and story file
    if test_file_path is None:
        test_file_path = _find_test_file(target_file_path)

    if story_file_path is None:
        story_file_path = _find_story_file(target_file_path)

    # 4. Analyze existing tests and stories
    test_functions = []
    if test_file_path:
        test_functions = _extract_test_functions(test_file_path)

    stories = []
    if story_file_path:
        stories = _extract_stories(story_file_path)

    # 5. Gap analysis (strategy formulation)
    strategies = []
    for func_analysis in condition_analysis.functions:
        # Classify function type
        is_custom_hook = _is_custom_hook(func_analysis.name)
        is_component = _is_component(func_analysis.name)

        # Determine test level and framework
        test_level, framework = _recommend_test_level_and_framework(
            is_custom_hook, is_component
        )

        # Find matching test function or story
        matching_test = None
        matching_story = None
        recommended_story_count = None
        existing_story_count = None

        if is_component:
            # Components should have Storybook stories
            # Calculate recommended story count based on complexity and branches
            branch_count = len(func_analysis.branches)
            recommended_story_count = _calculate_recommended_story_count(
                func_analysis.cyclomatic_complexity, branch_count
            )
            existing_story_count = len(stories)

            # If any stories exist, mark as having coverage
            if stories:
                matching_story = f"{existing_story_count} stories"
        else:
            # Hooks and other functions should have unit tests
            matching_test = _find_matching_test_function(
                func_analysis.name, test_functions
            )

        # Identify missing coverage
        missing_coverage = []
        if is_component:
            if existing_story_count == 0:
                details = (
                    f"No Storybook story found for '{func_analysis.name}'. "
                    f"Recommended: {recommended_story_count} stories"
                )
                missing_coverage.append(
                    MissingCoverage(
                        type="missing_storybook",
                        details=details,
                        lineno=func_analysis.lineno,
                    )
                )
            elif (
                existing_story_count is not None
                and recommended_story_count is not None
                and existing_story_count < recommended_story_count
            ):
                details = (
                    f"'{func_analysis.name}' has {existing_story_count} stories "
                    f"but {recommended_story_count} are recommended"
                )
                missing_coverage.append(
                    MissingCoverage(
                        type="insufficient_story_coverage",
                        details=details,
                        lineno=func_analysis.lineno,
                    )
                )
        elif not matching_test:
            func_type = "hook" if is_custom_hook else "function"
            details = f"No test found for {func_type} '{func_analysis.name}'"
            missing_coverage.append(
                MissingCoverage(
                    type="missing_test_function",
                    details=details,
                    lineno=func_analysis.lineno,
                )
            )

        # Extract mock candidates
        mock_candidates = [mc.name for mc in func_analysis.mock_candidates]

        strategies.append(
            FunctionStrategy(
                function_name=func_analysis.name,
                recommended_test_level=test_level,
                recommended_framework=framework,
                existing_test_function=matching_test,
                existing_story=matching_story,
                complexity=func_analysis.cyclomatic_complexity,
                missing_coverage=missing_coverage,
                suggested_mocks=mock_candidates,
                is_custom_hook=is_custom_hook,
                is_component=is_component,
                recommended_story_count=recommended_story_count,
                existing_story_count=existing_story_count,
            )
        )

    # 6. Aggregate results
    overall_recommendation = _generate_overall_recommendation(
        strategies, test_file_path is not None, story_file_path is not None
    )

    result = TestStrategyResult(
        target_file_path=target_file_path,
        corresponding_test_file=test_file_path,
        corresponding_story_file=story_file_path,
        strategies=strategies,
        overall_recommendation=overall_recommendation,
    )

    return ToolResult(data=result)
