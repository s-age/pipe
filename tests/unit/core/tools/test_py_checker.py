"""Unit tests for py_checker tool."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_checker import CheckStepResult, PyCheckerResult, py_checker


class TestPyChecker:
    """Tests for py_checker function."""

    @pytest.fixture
    def mock_project_root(self):
        """Mock project root path."""
        return "/mock/project/root"

    def _create_mock_process(self, returncode=0, stdout="success", stderr=""):
        """Helper to create a mock subprocess result."""
        mock_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_process.returncode = returncode
        mock_process.stdout = stdout
        mock_process.stderr = stderr
        return mock_process

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_all_success(self, mock_run, mock_get_root, mock_project_root):
        """Test py_checker when all steps succeed."""
        mock_get_root.return_value = mock_project_root

        # Mock successful subprocess runs
        mock_run.return_value = self._create_mock_process(stdout="success output")

        result = py_checker()

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, PyCheckerResult)
        assert result.data.overall_success is True

        # Verify all steps are present and successful
        for step in ["ruff_check", "ruff_format", "black", "mypy"]:
            step_result = getattr(result.data, step)
            assert isinstance(step_result, CheckStepResult)
            assert step_result.success is True
            assert step_result.exit_code == 0
            assert step_result.stdout == "success output"

        # Verify subprocess calls
        # Step 0: isort, black
        # Step 1-4: ruff check, ruff format, black, mypy
        assert mock_run.call_count == 6
        mock_run.assert_any_call(
            ["poetry", "run", "isort", "."],
            capture_output=True,
            text=True,
            cwd=mock_project_root,
            check=False,
        )

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_partial_failure(
        self, mock_run, mock_get_root, mock_project_root
    ):
        """Test py_checker when some steps fail."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "ruff" in cmd and "check" in cmd:
                return self._create_mock_process(
                    returncode=1, stdout="", stderr="ruff error"
                )
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()

        assert result.is_success
        assert result.data.overall_success is False
        assert result.data.ruff_check.success is False
        assert result.data.ruff_check.exit_code == 1
        assert result.data.ruff_check.stderr == "ruff error"
        assert result.data.mypy.success is True

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_command_not_found(
        self, mock_run, mock_get_root, mock_project_root
    ):
        """Test py_checker when a command is not found."""
        mock_get_root.return_value = mock_project_root

        # Fail on the first reported step (ruff check)
        def side_effect(cmd, **kwargs):
            if "ruff" in cmd and "check" in cmd:
                raise FileNotFoundError("ruff not found")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()

        assert not result.is_success
        assert "ruff command not found" in result.error

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_step_exception(
        self, mock_run, mock_get_root, mock_project_root
    ):
        """Test py_checker when a step raises an unexpected exception."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "ruff" in cmd and "check" in cmd:
                raise Exception("Unexpected error")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()

        assert not result.is_success
        assert "Error running ruff check: Unexpected error" in result.error

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_pre_formatting_silent_failure(
        self, mock_run, mock_get_root, mock_project_root
    ):
        """Test py_checker when pre-formatting steps fail (should be silent)."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "isort" in cmd or ("black" in cmd and mock_run.call_count <= 2):
                raise Exception("Silent failure")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()

        # Should still succeed because pre-formatting errors are caught and ignored
        assert result.is_success
        assert result.data.overall_success is True
        assert result.data.ruff_check.success is True

    @patch("pipe.core.tools.py_checker.get_project_root")
    def test_py_checker_unexpected_top_level_exception(self, mock_get_root):
        """Test py_checker when an unexpected exception occurs at the top level."""
        mock_get_root.side_effect = Exception("Fatal error")

        result = py_checker()

        assert not result.is_success
        assert "Unexpected error in py_checker: Fatal error" in result.error

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_ruff_format_failure(
        self, mock_run, mock_get_root, mock_project_root
    ):
        """Test py_checker when ruff format fails."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "ruff" in cmd and "format" in cmd:
                raise FileNotFoundError("ruff not found")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()
        assert not result.is_success
        assert "ruff command not found" in result.error

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_black_failure(self, mock_run, mock_get_root, mock_project_root):
        """Test py_checker when black fails."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "black" in cmd and mock_run.call_count > 2:  # Skip pre-formatting
                raise FileNotFoundError("black not found")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()
        assert not result.is_success
        assert "black command not found" in result.error

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_mypy_failure(self, mock_run, mock_get_root, mock_project_root):
        """Test py_checker when mypy fails."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "mypy" in cmd:
                raise FileNotFoundError("mypy not found")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()
        assert not result.is_success
        assert "mypy command not found" in result.error

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_ruff_format_exception(
        self, mock_run, mock_get_root, mock_project_root
    ):
        """Test py_checker when ruff format raises exception."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "ruff" in cmd and "format" in cmd:
                raise Exception("format error")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()
        assert not result.is_success
        assert "Error running ruff format: format error" in result.error

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_black_exception(
        self, mock_run, mock_get_root, mock_project_root
    ):
        """Test py_checker when black raises exception."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "black" in cmd and mock_run.call_count > 2:
                raise Exception("black error")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()
        assert not result.is_success
        assert "Error running black: black error" in result.error

    @patch("pipe.core.tools.py_checker.get_project_root")
    @patch("pipe.core.tools.py_checker.subprocess.run")
    def test_py_checker_mypy_exception(
        self, mock_run, mock_get_root, mock_project_root
    ):
        """Test py_checker when mypy raises exception."""
        mock_get_root.return_value = mock_project_root

        def side_effect(cmd, **kwargs):
            if "mypy" in cmd:
                raise Exception("mypy error")
            return self._create_mock_process()

        mock_run.side_effect = side_effect

        result = py_checker()
        assert not result.is_success
        assert "Error running mypy: mypy error" in result.error
