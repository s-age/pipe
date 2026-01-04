"""Unit tests for ts_run_and_test_code tool."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.ts_run_and_test_code_result import TsRunAndTestCodeResult
from pipe.core.tools.ts_run_and_test_code import ts_run_and_test_code


class TestTsRunAndTestCode:
    """Tests for ts_run_and_test_code function."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture for mocked repository."""
        repo = MagicMock()
        repo.exists.return_value = True
        repo.is_file.return_value = True
        repo.get_absolute_path.side_effect = lambda p: f"/abs/path/{p}"
        return repo

    @pytest.fixture
    def mock_repo_factory(self, mock_repo):
        """Fixture for mocked FileRepositoryFactory."""
        with patch(
            "pipe.core.tools.ts_run_and_test_code.FileRepositoryFactory.create"
        ) as mock_create:
            mock_create.return_value = mock_repo
            yield mock_create

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_run_all_tests_success(self, mock_run, mock_repo_factory):
        """Test running all tests when no file_path is provided."""
        mock_run.return_value = MagicMock(
            stdout="all tests passed", stderr="", returncode=0
        )

        result = ts_run_and_test_code()

        assert result.is_success
        assert isinstance(result.data, TsRunAndTestCodeResult)
        assert result.data.stdout == "all tests passed"
        assert result.data.exit_code == 0
        assert "completed successfully" in (result.data.message or "")
        mock_run.assert_called_once()
        assert mock_run.call_args.args[0] == ["npx", "vitest", "run"]

    def test_run_all_tests_with_filters_error(self, mock_repo_factory):
        """Test error when filters are provided without file_path."""
        result = ts_run_and_test_code(test_name="some test")
        assert not result.is_success
        assert "test_name and test_suite require file_path" in (result.error or "")

        result = ts_run_and_test_code(test_suite="some suite")
        assert not result.is_success
        assert "test_name and test_suite require file_path" in (result.error or "")

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_run_specific_test_file_success(
        self, mock_run, mock_repo, mock_repo_factory
    ):
        """Test running a specific test file."""
        mock_run.return_value = MagicMock(stdout="test passed", stderr="", returncode=0)
        file_path = "src/web/app.test.ts"
        mock_repo.get_absolute_path.return_value = "/abs/path/src/web/app.test.ts"

        result = ts_run_and_test_code(file_path=file_path)

        assert result.is_success
        assert result.data.stdout == "test passed"
        mock_run.assert_called_once()
        assert mock_run.call_args.args[0] == [
            "npx",
            "vitest",
            "run",
            "/abs/path/src/web/app.test.ts",
        ]

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_run_test_with_name_filter(self, mock_run, mock_repo, mock_repo_factory):
        """Test running a test with a name filter."""
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        file_path = "app.spec.tsx"
        mock_repo.get_absolute_path.return_value = "/abs/path/app.spec.tsx"

        ts_run_and_test_code(file_path=file_path, test_name="MyTest")

        assert mock_run.call_args.args[0] == [
            "npx",
            "vitest",
            "run",
            "/abs/path/app.spec.tsx",
            "-t",
            "MyTest",
        ]

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_run_test_with_suite_filter(self, mock_run, mock_repo, mock_repo_factory):
        """Test running a test with a suite filter."""
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        file_path = "app.test.js"
        mock_repo.get_absolute_path.return_value = "/abs/path/app.test.js"

        ts_run_and_test_code(file_path=file_path, test_suite="MySuite")

        assert mock_run.call_args.args[0] == [
            "npx",
            "vitest",
            "run",
            "/abs/path/app.test.js",
            "-t",
            "MySuite",
        ]

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_run_ts_file_execution(self, mock_run, mock_repo, mock_repo_factory):
        """Test executing a regular TypeScript file."""
        mock_run.return_value = MagicMock(stdout="ts output", stderr="", returncode=0)
        file_path = "script.ts"
        mock_repo.get_absolute_path.return_value = "/abs/path/script.ts"

        result = ts_run_and_test_code(file_path=file_path)

        assert result.is_success
        assert mock_run.call_args.args[0] == ["npx", "ts-node", "/abs/path/script.ts"]

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_run_tsx_file_execution(self, mock_run, mock_repo, mock_repo_factory):
        """Test executing a regular TSX file."""
        mock_run.return_value = MagicMock(stdout="tsx output", stderr="", returncode=0)
        file_path = "component.tsx"
        mock_repo.get_absolute_path.return_value = "/abs/path/component.tsx"

        result = ts_run_and_test_code(file_path=file_path)

        assert result.is_success
        assert mock_run.call_args.args[0] == [
            "npx",
            "ts-node",
            "/abs/path/component.tsx",
        ]

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_run_js_file_execution(self, mock_run, mock_repo, mock_repo_factory):
        """Test executing a regular JavaScript file."""
        mock_run.return_value = MagicMock(stdout="js output", stderr="", returncode=0)
        file_path = "script.js"
        mock_repo.get_absolute_path.return_value = "/abs/path/script.js"

        result = ts_run_and_test_code(file_path=file_path)

        assert result.is_success
        assert mock_run.call_args.args[0] == ["node", "/abs/path/script.js"]

    def test_file_not_found_error(self, mock_repo, mock_repo_factory):
        """Test error when file does not exist."""
        mock_repo.exists.return_value = False
        result = ts_run_and_test_code(file_path="missing.ts")
        assert not result.is_success
        assert "File not found" in (result.error or "")

    def test_not_a_file_error(self, mock_repo, mock_repo_factory):
        """Test error when path is not a file."""
        mock_repo.is_file.return_value = False
        result = ts_run_and_test_code(file_path="dir/")
        assert not result.is_success
        assert "Path is not a file" in (result.error or "")

    def test_invalid_file_path_error(self, mock_repo, mock_repo_factory):
        """Test error when path is invalid."""
        mock_repo.get_absolute_path.side_effect = ValueError("Invalid path")
        result = ts_run_and_test_code(file_path="../outside")
        assert not result.is_success
        assert "Invalid file path" in (result.error or "")

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_execution_failure_called_process_error(self, mock_run, mock_repo_factory):
        """Test handling of subprocess.CalledProcessError."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["npx", "vitest"],
            output="stdout error",
            stderr="stderr error",
        )

        result = ts_run_and_test_code()

        assert result.is_success  # Tool ran, but execution failed
        assert result.data.exit_code == 1
        assert result.data.stdout == "stdout error"
        assert result.data.stderr == "stderr error"
        assert "An error occurred" in (result.data.message or "")

    @patch("pipe.core.tools.ts_run_and_test_code.subprocess.run")
    def test_command_not_found_error(self, mock_run, mock_repo_factory):
        """Test handling of FileNotFoundError (command not found)."""
        mock_run.side_effect = FileNotFoundError()

        result = ts_run_and_test_code()

        assert not result.is_success
        assert "command not found" in (result.error or "")
