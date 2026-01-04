"""
Unit tests for the ts_auto_format_code tool.
"""

import subprocess
from unittest.mock import MagicMock, patch

from pipe.core.tools.ts_auto_format_code import ts_auto_format_code


class TestTsAutoFormatCode:
    """Unit tests for ts_auto_format_code function."""

    @patch("pipe.core.tools.ts_auto_format_code.subprocess.run")
    def test_ts_auto_format_code_success(self, mock_run: MagicMock) -> None:
        """Test successful execution of both Prettier and ESLint."""
        # Setup mock for Prettier
        mock_prettier_res = MagicMock()
        mock_prettier_res.stdout = "prettier success"
        mock_prettier_res.stderr = ""
        mock_prettier_res.returncode = 0

        # Setup mock for ESLint
        mock_eslint_res = MagicMock()
        mock_eslint_res.stdout = "eslint success"
        mock_eslint_res.stderr = ""
        mock_eslint_res.returncode = 0

        mock_run.side_effect = [mock_prettier_res, mock_eslint_res]

        result = ts_auto_format_code("test.ts")

        assert result.is_success
        assert result.data is not None
        assert len(result.data.formatting_results) == 2

        prettier_res = result.data.formatting_results[0]
        assert prettier_res.tool == "prettier"
        assert prettier_res.stdout == "prettier success"
        assert prettier_res.exit_code == 0
        assert "successfully" in (prettier_res.message or "")

        eslint_res = result.data.formatting_results[1]
        assert eslint_res.tool == "eslint"
        assert eslint_res.stdout == "eslint success"
        assert eslint_res.exit_code == 0
        assert "successfully" in (eslint_res.message or "")

        assert mock_run.call_count == 2

    @patch("pipe.core.tools.ts_auto_format_code.subprocess.run")
    def test_ts_auto_format_code_prettier_failure(self, mock_run: MagicMock) -> None:
        """Test handling of Prettier execution failure."""
        # Prettier fails with CalledProcessError
        mock_run.side_effect = [
            subprocess.CalledProcessError(
                returncode=1, cmd="prettier", output="prettier error", stderr="error"
            ),
            MagicMock(stdout="eslint success", stderr="", returncode=0),
        ]

        result = ts_auto_format_code("test.ts")

        assert result.is_success
        assert result.data is not None
        prettier_res = result.data.formatting_results[0]
        assert prettier_res.tool == "prettier"
        assert prettier_res.exit_code == 1
        assert "error" in (prettier_res.message or "").lower()

    @patch("pipe.core.tools.ts_auto_format_code.subprocess.run")
    def test_ts_auto_format_code_prettier_not_found(self, mock_run: MagicMock) -> None:
        """Test handling of Prettier not found (FileNotFoundError)."""
        mock_run.side_effect = [
            FileNotFoundError(),
            MagicMock(stdout="eslint success", stderr="", returncode=0),
        ]

        result = ts_auto_format_code("test.ts")

        assert result.data is not None
        prettier_res = result.data.formatting_results[0]
        assert prettier_res.tool == "prettier"
        assert prettier_res.error is not None
        assert "not found" in prettier_res.error.lower()

    @patch("pipe.core.tools.ts_auto_format_code.subprocess.run")
    def test_ts_auto_format_code_eslint_failure(self, mock_run: MagicMock) -> None:
        """Test handling of ESLint execution failure."""
        mock_run.side_effect = [
            MagicMock(stdout="prettier success", stderr="", returncode=0),
            subprocess.CalledProcessError(
                returncode=1, cmd="eslint", output="eslint error", stderr="error"
            ),
        ]

        result = ts_auto_format_code("test.ts")

        assert result.data is not None
        eslint_res = result.data.formatting_results[1]
        assert eslint_res.tool == "eslint"
        assert eslint_res.exit_code == 1
        assert "warnings/errors" in (eslint_res.message or "")

    @patch("pipe.core.tools.ts_auto_format_code.subprocess.run")
    def test_ts_auto_format_code_eslint_not_found(self, mock_run: MagicMock) -> None:
        """Test handling of ESLint not found (FileNotFoundError)."""
        mock_run.side_effect = [
            MagicMock(stdout="prettier success", stderr="", returncode=0),
            FileNotFoundError(),
        ]

        result = ts_auto_format_code("test.ts")

        assert result.data is not None
        eslint_res = result.data.formatting_results[1]
        assert eslint_res.tool == "eslint"
        assert eslint_res.error is not None
        assert "not found" in eslint_res.error.lower()
