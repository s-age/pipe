"""Unit tests for ts_checker tool."""

from unittest.mock import MagicMock, patch

from pipe.core.models.results.ts_checker_result import TSCheckerResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.ts_checker import ts_checker


class TestTSChecker:
    """Tests for the ts_checker function."""

    @patch("pipe.core.tools.ts_checker.os.path.exists")
    @patch("pipe.core.tools.ts_checker.subprocess.run")
    def test_ts_checker_success(
        self, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test successful lint and build execution."""
        # Setup mocks
        mock_exists.return_value = False  # No pyproject.toml, no src/web

        # Mock subprocess.run for lint and build
        mock_lint_res = MagicMock()
        mock_lint_res.stdout = "Linting passed\n"
        mock_lint_res.stderr = ""
        mock_lint_res.returncode = 0

        mock_build_res = MagicMock()
        mock_build_res.stdout = "Building passed\n"
        mock_build_res.stderr = ""
        mock_build_res.returncode = 0

        mock_run.side_effect = [mock_lint_res, mock_build_res]

        # Execute
        result = ts_checker(project_root="/mock/root")

        # Assertions
        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, TSCheckerResult)
        assert result.data is not None
        assert result.data.lint is not None
        assert result.data.build is not None
        assert result.data.lint.errors == []
        assert result.data.lint.warnings == []
        assert result.data.build.errors == []
        assert result.data.build.warnings == []

        assert mock_run.call_count == 2
        # Check cwd
        assert mock_run.call_args_list[0].kwargs["cwd"] == "/mock/root"

    @patch("pipe.core.tools.ts_checker.os.path.exists")
    @patch("pipe.core.tools.ts_checker.subprocess.run")
    def test_ts_checker_with_errors_and_warnings(
        self, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test parsing of errors and warnings from output."""
        mock_exists.return_value = False

        mock_lint_res = MagicMock()
        mock_lint_res.stdout = "Error: something failed\nWarning: just a warning\n"
        mock_lint_res.stderr = "Another error here\n"
        mock_run.side_effect = [mock_lint_res, mock_lint_res]

        result = ts_checker(project_root="/mock/root")

        assert result.data is not None
        assert result.data.lint is not None
        assert len(result.data.lint.errors) == 2
        assert "Error: something failed" in result.data.lint.errors
        assert "Another error here" in result.data.lint.errors
        assert result.data.lint.warnings == ["Warning: just a warning"]

    @patch("pipe.core.tools.ts_checker.os.path.exists")
    @patch("pipe.core.tools.ts_checker.subprocess.run")
    def test_ts_checker_rollup_exclusion(
        self, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test that rollup-related errors are ignored."""
        mock_exists.return_value = False

        mock_res = MagicMock()
        mock_res.stdout = "Error: real error\nError: rollup failed\nthrow new error\n"
        mock_res.stderr = ""
        mock_run.side_effect = [mock_res, mock_res]

        result = ts_checker(project_root="/mock/root")

        # Only "Error: real error" should remain
        assert result.data is not None
        assert result.data.lint is not None
        assert result.data.lint.errors == ["Error: real error"]

    @patch("pipe.core.tools.ts_checker.os.path.exists")
    @patch("pipe.core.tools.ts_checker.subprocess.run")
    def test_ts_checker_exception_handling(
        self, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test handling of exceptions during subprocess execution."""
        mock_exists.return_value = False
        mock_run.side_effect = Exception("Subprocess failed")

        result = ts_checker(project_root="/mock/root")

        assert result.data is not None
        assert result.data.lint is not None
        assert result.data.build is not None
        assert "Tool execution error: Subprocess failed" in result.data.lint.errors
        assert "Tool execution error: Subprocess failed" in result.data.build.errors

    @patch("pipe.core.tools.ts_checker.os.path.exists")
    def test_ts_checker_root_detection(self, mock_exists: MagicMock) -> None:
        """Test auto-detection of project root."""

        # Mock exists to find pyproject.toml ONLY at /found/root
        def exists_side_effect(path: str) -> bool:
            # Normalize path for comparison
            norm_path = path.replace("\\", "/")
            if norm_path == "/found/root/pyproject.toml":
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        with (
            patch("pipe.core.tools.ts_checker.os.path.abspath") as mock_abspath,
            patch("pipe.core.tools.ts_checker.os.path.dirname") as mock_dirname,
            patch("pipe.core.tools.ts_checker.subprocess.run") as mock_run,
        ):
            mock_abspath.return_value = "/found/root/src/pipe/core/tools/ts_checker.py"
            # dirname will be called multiple times
            # 1. current_dir = os.path.dirname(abspath) -> /found/root/src/pipe/core/tools
            # 2. parent = os.path.dirname(search_dir) -> /found/root/src/pipe/core
            # 3. parent = os.path.dirname(search_dir) -> /found/root/src/pipe
            # 4. parent = os.path.dirname(search_dir) -> /found/root/src
            # 5. parent = os.path.dirname(search_dir) -> /found/root
            mock_dirname.side_effect = [
                "/found/root/src/pipe/core/tools",  # current_dir
                "/found/root/src/pipe/core",  # parent 1
                "/found/root/src/pipe",  # parent 2
                "/found/root/src",  # parent 3
                "/found/root",  # parent 4
            ]

            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

            ts_checker()

            # Verify cwd used in subprocess.run is the detected root
            assert mock_run.call_args_list[0].kwargs["cwd"] == "/found/root"

    @patch("pipe.core.tools.ts_checker.os.path.exists")
    def test_ts_checker_root_detection_not_found(self, mock_exists: MagicMock) -> None:
        """Test auto-detection when pyproject.toml is not found."""
        mock_exists.return_value = False

        with (
            patch("pipe.core.tools.ts_checker.os.path.abspath") as mock_abspath,
            patch("pipe.core.tools.ts_checker.os.path.dirname") as mock_dirname,
            patch("pipe.core.tools.ts_checker.subprocess.run") as mock_run,
        ):
            mock_abspath.return_value = "/mock/dir/ts_checker.py"
            mock_dirname.return_value = "/mock/dir"

            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

            ts_checker()

            # Should fallback to current_dir
            assert mock_run.call_args_list[0].kwargs["cwd"] == "/mock/dir"

    @patch("pipe.core.tools.ts_checker.os.path.exists")
    def test_ts_checker_root_detection_filesystem_root(
        self, mock_exists: MagicMock
    ) -> None:
        """Test auto-detection when reaching filesystem root."""
        mock_exists.return_value = False

        with (
            patch("pipe.core.tools.ts_checker.os.path.abspath") as mock_abspath,
            patch("pipe.core.tools.ts_checker.os.path.dirname") as mock_dirname,
            patch("pipe.core.tools.ts_checker.subprocess.run") as mock_run,
        ):
            mock_abspath.return_value = "/ts_checker.py"
            # dirname returns same path at root
            mock_dirname.return_value = "/"

            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

            ts_checker()

            assert mock_run.call_args_list[0].kwargs["cwd"] == "/"

    @patch("pipe.core.tools.ts_checker.os.path.exists")
    @patch("pipe.core.tools.ts_checker.subprocess.run")
    def test_ts_checker_web_dir_detection(
        self, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test detection of src/web directory."""

        def exists_side_effect(path: str) -> bool:
            norm_path = path.replace("\\", "/")
            if norm_path.endswith("src/web/package.json"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        ts_checker(project_root="/mock/root")

        # Should use /mock/root/src/web as cwd
        actual_cwd = mock_run.call_args_list[0].kwargs["cwd"].replace("\\", "/")
        assert actual_cwd == "/mock/root/src/web"
