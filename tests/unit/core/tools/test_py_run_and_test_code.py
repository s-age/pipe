"""Unit tests for py_run_and_test_code tool."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.py_run_and_test_code_result import PyRunAndTestCodeResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_run_and_test_code import py_run_and_test_code


class TestPyRunAndTestCode:
    """Unit tests for py_run_and_test_code tool."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture for mocked repository."""
        repo = MagicMock()
        repo.exists.return_value = True
        repo.is_file.return_value = True
        repo.get_absolute_path.side_effect = lambda x: f"/abs/{x}"
        return repo

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_run_and_test_code.subprocess.run")
    def test_run_all_tests_success(self, mock_run, mock_repo_factory, mock_repo):
        """Test running all tests when no file_path is provided."""
        mock_repo_factory.return_value = mock_repo
        mock_run.return_value = MagicMock(
            stdout="pytest output", stderr="", returncode=0
        )

        result = py_run_and_test_code()

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, PyRunAndTestCodeResult)
        assert result.data.stdout == "pytest output"
        assert result.data.exit_code == 0
        mock_run.assert_called_once_with(
            ["poetry", "run", "pytest", "-q"],
            capture_output=True,
            text=True,
            check=True,
        )

    def test_run_all_tests_with_params_error(self):
        """Test error when function_name is provided without file_path."""
        result = py_run_and_test_code(function_name="test_func")
        assert not result.is_success
        assert "require file_path" in result.error

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    def test_file_not_found(self, mock_repo_factory, mock_repo):
        """Test error when file does not exist."""
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = False

        result = py_run_and_test_code(file_path="missing.py")

        assert not result.is_success
        assert "File not found" in result.error

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    def test_path_is_not_a_file(self, mock_repo_factory, mock_repo):
        """Test error when path is a directory."""
        mock_repo_factory.return_value = mock_repo
        mock_repo.is_file.return_value = False

        result = py_run_and_test_code(file_path="dir/")

        assert not result.is_success
        assert "Path is not a file" in result.error

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    def test_invalid_file_path_value_error(self, mock_repo_factory, mock_repo):
        """Test error when get_absolute_path raises ValueError."""
        mock_repo_factory.return_value = mock_repo
        mock_repo.get_absolute_path.side_effect = ValueError("Invalid path")

        result = py_run_and_test_code(file_path="invalid.py")

        assert not result.is_success
        assert "Invalid file path: Invalid path" in result.error

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_run_and_test_code.subprocess.run")
    def test_run_specific_test_case(self, mock_run, mock_repo_factory, mock_repo):
        """Test running a specific test case."""
        mock_repo_factory.return_value = mock_repo
        mock_run.return_value = MagicMock(stdout="test passed", stderr="", returncode=0)

        result = py_run_and_test_code(
            file_path="test_file.py", test_case_name="test_case"
        )

        assert result.is_success
        mock_run.assert_called_once_with(
            ["poetry", "run", "pytest", "-q", "/abs/test_file.py", "-k", "test_case"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_run_and_test_code.subprocess.run")
    @patch("pipe.core.tools.py_run_and_test_code.tempfile.NamedTemporaryFile")
    @patch("pipe.core.tools.py_run_and_test_code.os.path.exists")
    @patch("pipe.core.tools.py_run_and_test_code.os.unlink")
    def test_run_specific_function(
        self,
        mock_unlink,
        mock_exists,
        mock_temp,
        mock_run,
        mock_repo_factory,
        mock_repo,
    ):
        """Test running a specific function via temporary script."""
        mock_repo_factory.return_value = mock_repo
        mock_run.return_value = MagicMock(stdout="func output", stderr="", returncode=0)
        mock_exists.return_value = True

        # Mock temp file
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/temp_script.py"
        mock_temp.return_value = mock_temp_file

        result = py_run_and_test_code(file_path="module.py", function_name="my_func")

        assert result.is_success
        mock_temp_file.write.assert_called_once()
        mock_temp_file.close.assert_called_once()
        mock_run.assert_called_once_with(
            ["poetry", "run", "python", "/tmp/temp_script.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        mock_unlink.assert_called_once_with("/tmp/temp_script.py")

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_run_and_test_code.subprocess.run")
    def test_run_entire_file(self, mock_run, mock_repo_factory, mock_repo):
        """Test executing the entire file."""
        mock_repo_factory.return_value = mock_repo
        mock_run.return_value = MagicMock(stdout="file output", stderr="", returncode=0)

        result = py_run_and_test_code(file_path="script.py")

        assert result.is_success
        mock_run.assert_called_once_with(
            ["poetry", "run", "python", "/abs/script.py"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_run_and_test_code.subprocess.run")
    def test_execution_failure(self, mock_run, mock_repo_factory, mock_repo):
        """Test handling of subprocess.CalledProcessError."""
        mock_repo_factory.return_value = mock_repo
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="python script.py",
            output="some output",
            stderr="some error",
        )

        result = py_run_and_test_code(file_path="script.py")

        assert result.is_success  # Tool ran successfully, even if code failed
        assert result.data.exit_code == 1
        assert result.data.stdout == "some output"
        assert result.data.stderr == "some error"
        assert "An error occurred" in result.data.message

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_run_and_test_code.subprocess.run")
    def test_command_not_found(self, mock_run, mock_repo_factory, mock_repo):
        """Test handling of FileNotFoundError from subprocess.run."""
        mock_repo_factory.return_value = mock_repo
        mock_run.side_effect = FileNotFoundError()

        result = py_run_and_test_code()

        assert not result.is_success
        assert "Specified file or command not found" in result.error

    @patch("pipe.core.tools.py_run_and_test_code.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_run_and_test_code.subprocess.run")
    @patch("pipe.core.tools.py_run_and_test_code.tempfile.NamedTemporaryFile")
    @patch("pipe.core.tools.py_run_and_test_code.os.unlink")
    @patch("pipe.core.tools.py_run_and_test_code.os.path.exists")
    def test_temp_file_cleanup_failure(
        self,
        mock_exists,
        mock_unlink,
        mock_temp,
        mock_run,
        mock_repo_factory,
        mock_repo,
    ):
        """Test that cleanup failure doesn't crash the tool."""
        mock_repo_factory.return_value = mock_repo
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        mock_exists.return_value = True
        mock_unlink.side_effect = Exception("Cleanup failed")

        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/temp.py"
        mock_temp.return_value = mock_temp_file

        # Should not raise exception
        result = py_run_and_test_code(file_path="module.py", function_name="func")
        assert result.is_success
