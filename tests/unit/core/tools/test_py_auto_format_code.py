"""Unit tests for py_auto_format_code tool."""

import subprocess
from unittest.mock import MagicMock, patch

from pipe.core.models.results.py_auto_format_code_result import PyAutoFormatCodeResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_auto_format_code import py_auto_format_code


class TestPyAutoFormatCode:
    """Unit tests for py_auto_format_code tool."""

    @patch("pipe.core.tools.py_auto_format_code.subprocess.run")
    def test_py_auto_format_code_all_success(self, mock_run: MagicMock) -> None:
        """Test py_auto_format_code when all tools succeed."""
        # Setup mock responses for isort, black, ruff format, ruff check
        mock_run.return_value = MagicMock(
            stdout="success output", stderr="", returncode=0
        )

        result = py_auto_format_code("test.py")

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, PyAutoFormatCodeResult)
        assert result.data is not None
        assert len(result.data.formatting_results) == 4

        # Verify tools called
        assert result.data.formatting_results[0].tool == "isort"
        assert result.data.formatting_results[1].tool == "black"
        assert result.data.formatting_results[2].tool == "ruff format"
        assert result.data.formatting_results[3].tool == "ruff check"

        for res in result.data.formatting_results:
            assert res.exit_code == 0
            assert res.message is not None
            assert res.message.endswith("completed successfully.")

    @patch("pipe.core.tools.py_auto_format_code.subprocess.run")
    def test_py_auto_format_code_isort_failure(self, mock_run: MagicMock) -> None:
        """Test py_auto_format_code when isort fails."""

        # isort fails, others succeed
        def side_effect(command: list[str], **kwargs: object) -> MagicMock:
            if "isort" in command:
                raise subprocess.CalledProcessError(
                    returncode=1,
                    cmd=command,
                    output="isort error",
                    stderr="isort stderr",
                )
            return MagicMock(stdout="success", stderr="", returncode=0)

        mock_run.side_effect = side_effect

        result = py_auto_format_code("test.py")

        assert result.data is not None
        isort_res = result.data.formatting_results[0]
        assert isort_res.tool == "isort"
        assert isort_res.exit_code == 1
        assert isort_res.message is not None
        assert "error" in isort_res.message.lower()

    @patch("pipe.core.tools.py_auto_format_code.subprocess.run")
    def test_py_auto_format_code_isort_not_found(self, mock_run: MagicMock) -> None:
        """Test py_auto_format_code when isort is not found."""

        def side_effect(command: list[str], **kwargs: object) -> MagicMock:
            if "isort" in command:
                raise FileNotFoundError("isort not found")
            return MagicMock(stdout="success", stderr="", returncode=0)

        mock_run.side_effect = side_effect

        result = py_auto_format_code("test.py")

        assert result.data is not None
        isort_res = result.data.formatting_results[0]
        assert isort_res.tool == "isort"
        assert isort_res.error == "isort command not found."

    @patch("pipe.core.tools.py_auto_format_code.subprocess.run")
    def test_py_auto_format_code_black_failure(self, mock_run: MagicMock) -> None:
        """Test py_auto_format_code when black fails."""

        def side_effect(command: list[str], **kwargs: object) -> MagicMock:
            if "black" in command:
                raise subprocess.CalledProcessError(
                    returncode=1,
                    cmd=command,
                    output="black error",
                    stderr="black stderr",
                )
            return MagicMock(stdout="success", stderr="", returncode=0)

        mock_run.side_effect = side_effect

        result = py_auto_format_code("test.py")

        assert result.data is not None
        black_res = result.data.formatting_results[1]
        assert black_res.tool == "black"
        assert black_res.exit_code == 1

    @patch("pipe.core.tools.py_auto_format_code.subprocess.run")
    def test_py_auto_format_code_black_not_found(self, mock_run: MagicMock) -> None:
        """Test py_auto_format_code when black is not found."""

        def side_effect(command: list[str], **kwargs: object) -> MagicMock:
            if "black" in command:
                raise FileNotFoundError("black not found")
            return MagicMock(stdout="success", stderr="", returncode=0)

        mock_run.side_effect = side_effect

        result = py_auto_format_code("test.py")

        assert result.data is not None
        black_res = result.data.formatting_results[1]
        assert black_res.tool == "black"
        assert black_res.error == "black command not found."

    @patch("pipe.core.tools.py_auto_format_code.subprocess.run")
    def test_py_auto_format_code_ruff_failure(self, mock_run: MagicMock) -> None:
        """Test py_auto_format_code when ruff fails."""

        def side_effect(command: list[str], **kwargs: object) -> MagicMock:
            if "ruff" in command:
                raise subprocess.CalledProcessError(
                    returncode=1,
                    cmd=command,
                    output="ruff error",
                    stderr="ruff stderr",
                )
            return MagicMock(stdout="success", stderr="", returncode=0)

        mock_run.side_effect = side_effect

        result = py_auto_format_code("test.py")

        assert result.data is not None
        # Ruff failure appends one result with tool="ruff"
        ruff_res = result.data.formatting_results[2]
        assert ruff_res.tool == "ruff"
        assert ruff_res.exit_code == 1

    @patch("pipe.core.tools.py_auto_format_code.subprocess.run")
    def test_py_auto_format_code_ruff_not_found(self, mock_run: MagicMock) -> None:
        """Test py_auto_format_code when ruff is not found."""

        def side_effect(command: list[str], **kwargs: object) -> MagicMock:
            if "ruff" in command:
                raise FileNotFoundError("ruff not found")
            return MagicMock(stdout="success", stderr="", returncode=0)

        mock_run.side_effect = side_effect

        result = py_auto_format_code("test.py")

        assert result.data is not None
        ruff_res = result.data.formatting_results[2]
        assert ruff_res.tool == "ruff"
        assert ruff_res.error == "ruff command not found."
