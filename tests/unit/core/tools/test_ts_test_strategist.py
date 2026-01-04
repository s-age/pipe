"""Unit tests for ts_test_strategist tool."""

from unittest.mock import MagicMock, patch

from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.ts_condition_analyzer import (
    AnalyzeConditionResult,
    BranchInfo,
    FunctionAnalysis,
    MockCandidate,
)
from pipe.core.tools.ts_test_strategist import (
    FunctionStrategy,
    TestFramework,
    TestLevel,
    TestStrategyResult,
    _calculate_recommended_story_count,
    _extract_stories,
    _extract_test_functions,
    _find_matching_test_function,
    _find_story_file,
    _find_test_file,
    _generate_overall_recommendation,
    _is_component,
    _is_custom_hook,
    _recommend_test_level_and_framework,
    ts_test_strategist,
)

# Prevent pytest from trying to collect these as test classes
TestLevel.__test__ = False
TestFramework.__test__ = False
TestStrategyResult.__test__ = False


class TestIsCustomHook:
    """Tests for _is_custom_hook function."""

    def test_is_custom_hook_true(self):
        """Test with valid custom hook names."""
        assert _is_custom_hook("useSession") is True
        assert _is_custom_hook("useAuth") is True

    def test_is_custom_hook_false(self):
        """Test with non-hook names."""
        assert _is_custom_hook("getSession") is False
        assert _is_custom_hook("use") is False  # Too short
        assert _is_custom_hook("UserComponent") is False


class TestIsComponent:
    """Tests for _is_component function."""

    def test_is_component_true(self):
        """Test with valid component names."""
        assert _is_component("SessionList") is True
        assert _is_component("Button") is True

    def test_is_component_false(self):
        """Test with non-component names."""
        assert _is_component("sessionList") is False
        assert _is_component("useSession") is False
        assert _is_component("") is False


class TestFindTestFile:
    """Tests for _find_test_file function."""

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.ts_test_strategist.Path")
    def test_find_test_file_same_dir(self, mock_path_class, mock_repo_factory):
        """Test finding test file in the same directory."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo

        mock_target_path = MagicMock()
        mock_path_class.return_value.resolve.return_value = mock_target_path

        mock_target_path.stem = "target"
        mock_target_path.suffix = ".ts"
        mock_target_path.parent = mock_target_path  # Terminate loop

        # Mock / operator to return a mock whose str() is the path
        def div_side_effect(x):
            m = MagicMock()
            m.__str__.return_value = f"path/{x}"  # type: ignore[attr-defined]
            m.exists.return_value = False
            return m

        mock_target_path.__truediv__.side_effect = div_side_effect

        mock_repo.exists.side_effect = lambda p: "target.test.ts" in str(p)

        result = _find_test_file("src/target.ts")
        assert result is not None
        assert "target.test.ts" in result

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.ts_test_strategist.Path")
    @patch("pipe.core.tools.ts_test_strategist.os.walk")
    def test_find_test_file_in_test_dir(
        self, mock_walk, mock_path_class, mock_repo_factory
    ):
        """Test finding test file in a test directory."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo

        # Create distinct mock objects for proper identity comparison
        mock_target_path = MagicMock()
        mock_target_path.stem = "target"
        mock_target_path.suffix = ".ts"

        # Create parent directory (e.g., /project/src)
        mock_parent_dir = MagicMock()
        mock_target_path.parent = mock_parent_dir

        # Create project root (e.g., /project)
        mock_project_root = MagicMock()

        # Create a grandparent to ensure the loop can check .git in project_root
        # before hitting the termination condition
        mock_grandparent = MagicMock()

        # Create mock objects for .git directories
        mock_git_in_parent = MagicMock()
        mock_git_in_parent.exists.return_value = False

        mock_git_in_root = MagicMock()
        mock_git_in_root.exists.return_value = True

        # Setup division operations for parent directory
        def parent_div(name):
            if name == ".git":
                return mock_git_in_parent
            # Return mock for other paths
            m = MagicMock()
            m.exists.return_value = False
            return m

        # Setup division operations for project root
        def root_div(name):
            if name == ".git":
                return mock_git_in_root
            # For test directories: only "tests" exists
            m = MagicMock()
            m.exists.return_value = name == "tests"
            return m

        mock_parent_dir.__truediv__.side_effect = parent_div
        mock_project_root.__truediv__.side_effect = root_div

        # Setup parent chain:
        # parent_dir.parent = root, root.parent = grandparent, grandparent.parent = grandparent (loop termination)
        mock_parent_dir.parent = mock_project_root
        mock_project_root.parent = mock_grandparent
        mock_grandparent.parent = mock_grandparent

        # Path() returns mock_target_path when called with the target file,
        # but we need to handle Path(root) calls in os.walk loop differently
        def path_constructor(path_arg=None):
            if path_arg is None or path_arg == "src/target.ts":
                # This is the initial Path(target_file_path).resolve() call
                m = MagicMock()
                m.resolve.return_value = mock_target_path
                return m
            else:
                # This is Path(root) in the os.walk loop (line 174)
                # Return a mock that can do division and str() properly
                m = MagicMock()
                m.__truediv__ = lambda self, p: MagicMock(
                    __str__=lambda s: f"{path_arg}/{p}"
                )
                return m

        mock_path_class.side_effect = path_constructor

        # Mock repo.exists to fail for same dir, succeed for test dir
        # The path will be "/project/root/tests/target.test.ts"
        mock_repo.exists.side_effect = (
            lambda p: str(p) == "/project/root/tests/target.test.ts"
        )

        # Mock os.walk to find the file in tests directory
        mock_walk.return_value = [("/project/root/tests", [], ["target.test.ts"])]

        result = _find_test_file("src/target.ts")

        assert result is not None
        assert "target.test.ts" in result


class TestFindStoryFile:
    """Tests for _find_story_file function."""

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.ts_test_strategist.Path")
    def test_find_story_file_regular(self, mock_path_class, mock_repo_factory):
        """Test finding story file for a regular component."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo

        mock_target_path = MagicMock()
        mock_path_class.return_value.resolve.return_value = mock_target_path

        mock_target_path.stem = "Button"
        mock_target_path.parent = mock_target_path
        mock_target_path.__truediv__.side_effect = lambda x: MagicMock(
            __str__=MagicMock(return_value=f"path/{x}")
        )

        mock_repo.exists.return_value = True

        result = _find_story_file("src/Button.tsx")

        assert result is not None
        assert "Button.stories.tsx" in result

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.ts_test_strategist.Path")
    def test_find_story_file_index(self, mock_path_class, mock_repo_factory):
        """Test finding story file for an index.tsx component."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo

        mock_target_path = MagicMock()
        mock_path_class.return_value.resolve.return_value = mock_target_path

        mock_target_path.stem = "index"
        mock_target_path.parent.name = "ToggleSwitch"
        mock_target_path.parent.parent = mock_target_path.parent

        mock_target_path.parent.__truediv__.side_effect = lambda x: MagicMock(
            __str__=MagicMock(return_value=f"path/{x}")
        )

        mock_repo.exists.return_value = True

        result = _find_story_file("src/ToggleSwitch/index.tsx")

        assert result is not None
        assert "ToggleSwitch.stories.tsx" in result


class TestExtractTestFunctions:
    """Tests for _extract_test_functions function."""

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    def test_extract_test_functions_success(self, mock_repo_factory):
        """Test extracting test names from a file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = """
            it('should do something', () => {});
            test("should do another thing", () => {});
            it.skip(`should be skipped`, () => {});
        """

        result = _extract_test_functions("test.ts")

        assert result == [
            "should do something",
            "should do another thing",
            "should be skipped",
        ]

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    def test_extract_test_functions_not_found(self, mock_repo_factory):
        """Test when test file does not exist."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = False

        result = _extract_test_functions("test.ts")

        assert result == []


class TestExtractStories:
    """Tests for _extract_stories function."""

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    def test_extract_stories_success(self, mock_repo_factory):
        """Test extracting story names from a file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = """
            export const Default: Story = {};
            export const Disabled: Story = {};
        """

        result = _extract_stories("Button.stories.tsx")

        assert result == ["Default", "Disabled"]


class TestFindMatchingTestFunction:
    """Tests for _find_matching_test_function function."""

    def test_find_matching_test_function_exact(self):
        """Test finding exact match."""
        assert (
            _find_matching_test_function("handleClick", ["handleClick works"])
            == "handleClick works"
        )

    def test_find_matching_test_function_camel_to_words(self):
        """Test finding match with camelCase conversion."""
        assert (
            _find_matching_test_function("handleClick", ["handle click works"])
            == "handle click works"
        )

    def test_find_matching_test_function_no_match(self):
        """Test when no match is found."""
        assert _find_matching_test_function("handleClick", ["other test"]) is None


class TestCalculateRecommendedStoryCount:
    """Tests for _calculate_recommended_story_count function."""

    def test_calculate_recommended_story_count_with_branches(self):
        """Test with branches."""
        assert _calculate_recommended_story_count(5, 2) == 3
        assert _calculate_recommended_story_count(5, 5) == 6

    def test_calculate_recommended_story_count_no_branches(self):
        """Test without branches."""
        assert _calculate_recommended_story_count(1, 0) == 2
        assert _calculate_recommended_story_count(10, 0) == 5


class TestRecommendTestLevelAndFramework:
    """Tests for _recommend_test_level_and_framework function."""

    def test_recommend_hook(self):
        """Test recommendation for hooks."""
        level, framework = _recommend_test_level_and_framework(True, False)
        assert level == TestLevel.UNIT
        assert framework == TestFramework.JEST

    def test_recommend_component(self):
        """Test recommendation for components."""
        level, framework = _recommend_test_level_and_framework(False, True)
        assert level == TestLevel.INTEGRATION
        assert framework == TestFramework.STORYBOOK

    def test_recommend_other(self):
        """Test recommendation for other functions."""
        level, framework = _recommend_test_level_and_framework(False, False)
        assert level == TestLevel.UNIT
        assert framework == TestFramework.JEST


class TestGenerateOverallRecommendation:
    """Tests for _generate_overall_recommendation function."""

    def test_generate_overall_recommendation_good(self):
        """Test when coverage is good."""
        strategy = FunctionStrategy(
            function_name="test",
            recommended_test_level=TestLevel.UNIT,
            recommended_framework=TestFramework.JEST,
            existing_test_function="test works",
            complexity=1,
        )
        result = _generate_overall_recommendation([strategy], True, False)
        assert "Test coverage is good." in result

    def test_generate_overall_recommendation_missing_tests(self):
        """Test when tests are missing."""
        strategy = FunctionStrategy(
            function_name="test",
            recommended_test_level=TestLevel.UNIT,
            recommended_framework=TestFramework.JEST,
            complexity=1,
        )
        result = _generate_overall_recommendation([strategy], False, False)
        assert "1/1 function(s) are missing unit tests." in result

    def test_generate_overall_recommendation_high_complexity(self):
        """Test when high complexity functions are present."""
        strategy = FunctionStrategy(
            function_name="complexFunc",
            recommended_test_level=TestLevel.UNIT,
            recommended_framework=TestFramework.JEST,
            complexity=15,
            suggested_mocks=["api"],
        )
        result = _generate_overall_recommendation([strategy], True, False)
        assert "high complexity" in result
        assert "need mocking" in result


class TestTsTestStrategist:
    """Tests for ts_test_strategist main function."""

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.ts_test_strategist.ts_condition_analyzer")
    def test_ts_test_strategist_file_not_found(self, mock_analyzer, mock_repo_factory):
        """Test when target file is not found."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = False

        result = ts_test_strategist("non-existent.ts")

        assert isinstance(result, ToolResult)
        assert result.data is not None
        assert "File not found" in result.data.error

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.ts_test_strategist.ts_condition_analyzer")
    def test_ts_test_strategist_invalid_extension(
        self, mock_analyzer, mock_repo_factory
    ):
        """Test when file is not a TypeScript file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True

        result = ts_test_strategist("style.css")

        assert isinstance(result, ToolResult)
        assert result.data is not None
        assert "Not a TypeScript file" in result.data.error

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.ts_test_strategist.ts_condition_analyzer")
    def test_ts_test_strategist_analyzer_error(self, mock_analyzer, mock_repo_factory):
        """Test when analyzer returns an error."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True

        mock_analyzer.return_value = ToolResult(error="Analysis failed")

        result = ts_test_strategist("target.ts")

        assert isinstance(result, ToolResult)
        assert result.data is not None
        assert "Static analysis failed" in result.data.error

    @patch("pipe.core.tools.ts_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.ts_test_strategist.ts_condition_analyzer")
    @patch("pipe.core.tools.ts_test_strategist._find_test_file")
    @patch("pipe.core.tools.ts_test_strategist._find_story_file")
    def test_ts_test_strategist_success(
        self, mock_find_story, mock_find_test, mock_analyzer, mock_repo_factory
    ):
        """Test successful strategy generation."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True

        # Mock analyzer result
        functions = [
            FunctionAnalysis(
                name="useSession",
                lineno=10,
                end_lineno=20,
                cyclomatic_complexity=2,
                branches=[],
                mock_candidates=[
                    MockCandidate(name="api", lineno=15, is_method_call=False)
                ],
            ),
            FunctionAnalysis(
                name="Button",
                lineno=30,
                end_lineno=50,
                cyclomatic_complexity=5,
                branches=[BranchInfo(type="if", lineno=35)],
                mock_candidates=[],
            ),
        ]
        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(file_path="target.tsx", functions=functions)
        )

        mock_find_test.return_value = "test.ts"
        mock_find_story.return_value = "story.tsx"

        with patch(
            "pipe.core.tools.ts_test_strategist._extract_test_functions",
            return_value=["useSession works"],
        ):
            with patch(
                "pipe.core.tools.ts_test_strategist._extract_stories",
                return_value=["Default"],
            ):
                result = ts_test_strategist("src/useSession.ts")

        assert isinstance(result, ToolResult)
        assert result.data is not None
        assert result.data.target_file_path == "src/useSession.ts"
        assert len(result.data.strategies) == 2

        hook_strat = next(
            s for s in result.data.strategies if s.function_name == "useSession"
        )
        assert hook_strat.is_custom_hook is True
        assert hook_strat.existing_test_function == "useSession works"

        comp_strat = next(
            s for s in result.data.strategies if s.function_name == "Button"
        )
        assert comp_strat.is_component is True
        assert comp_strat.existing_story == "1 stories"
