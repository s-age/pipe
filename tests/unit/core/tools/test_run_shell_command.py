"""Unit tests for run_shell_command tool."""

from unittest.mock import MagicMock, patch

from pipe.core.models.results.run_shell_command_result import RunShellCommandResult
from pipe.core.tools.run_shell_command import run_shell_command


class TestRunShellCommand:
    """Test suite for run_shell_command function."""

    @patch("pipe.core.tools.run_shell_command.get_project_root")
    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    @patch("subprocess.run")
    def test_run_shell_command_success_no_directory(
        self,
        mock_run: MagicMock,
        mock_repo_factory: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test successful command execution without specifying a directory."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "hello world\n"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Execute
        result = run_shell_command(command="echo hello")

        # Verify
        assert result.is_success
        assert isinstance(result.data, RunShellCommandResult)
        assert result.data is not None
        assert result.data.command == "echo hello"
        assert result.data.stdout == "hello world"
        assert result.data.exit_code == 0
        assert result.data.directory == "/project/root"

        mock_run.assert_called_once_with(
            "echo hello",
            shell=True,
            capture_output=True,
            text=True,
            cwd="/project/root",
            check=False,
        )

    @patch("pipe.core.tools.run_shell_command.get_project_root")
    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    @patch("subprocess.run")
    def test_run_shell_command_success_with_directory(
        self,
        mock_run: MagicMock,
        mock_repo_factory: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test successful command execution with a specified directory."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo = MagicMock()
        mock_repo.exists.return_value = True
        mock_repo.is_dir.return_value = True
        mock_repo.get_absolute_path.return_value = "/project/root/subdir"
        mock_repo_factory.return_value = mock_repo

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "in subdir\n"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Execute
        result = run_shell_command(command="ls", directory="subdir")

        # Verify
        assert result.is_success
        assert result.data is not None
        assert result.data.directory == "/project/root/subdir"
        assert result.data.stdout == "in subdir"

        mock_repo.exists.assert_called_once_with("subdir")
        mock_repo.is_dir.assert_called_once_with("subdir")
        mock_run.assert_called_once_with(
            "ls",
            shell=True,
            capture_output=True,
            text=True,
            cwd="/project/root/subdir",
            check=False,
        )

    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    def test_run_shell_command_directory_not_exists(
        self, mock_repo_factory: MagicMock
    ) -> None:
        """Test failure when the specified directory does not exist."""
        # Setup
        mock_repo = MagicMock()
        mock_repo.exists.return_value = False
        mock_repo_factory.return_value = mock_repo

        # Execute
        result = run_shell_command(command="ls", directory="nonexistent")

        # Verify
        assert not result.is_success
        assert result.error is not None
        assert "Directory does not exist" in result.error
        assert result.data is None

    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    def test_run_shell_command_path_not_a_directory(
        self, mock_repo_factory: MagicMock
    ) -> None:
        """Test failure when the specified path is not a directory."""
        # Setup
        mock_repo = MagicMock()
        mock_repo.exists.return_value = True
        mock_repo.is_dir.return_value = False
        mock_repo_factory.return_value = mock_repo

        # Execute
        result = run_shell_command(command="ls", directory="file.txt")

        # Verify
        assert not result.is_success
        assert result.error is not None
        assert "Path is not a directory" in result.error

    @patch("pipe.core.tools.run_shell_command.get_project_root")
    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    @patch("subprocess.run")
    def test_run_shell_command_execution_failure(
        self,
        mock_run: MagicMock,
        mock_repo_factory: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test command execution that returns a non-zero exit code."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo_factory.return_value = MagicMock()

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "error message\n"
        mock_run.return_value = mock_process

        # Execute
        result = run_shell_command(command="false")

        # Verify
        assert result.is_success  # ToolResult is success even if command fails
        assert result.data is not None
        assert result.data.exit_code == 1
        assert result.data.stderr == "error message"
        assert "Command failed with exit code 1" in result.data.error

    @patch("pipe.core.tools.run_shell_command.get_project_root")
    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    @patch("subprocess.run")
    def test_run_shell_command_not_found(
        self,
        mock_run: MagicMock,
        mock_repo_factory: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test handling of FileNotFoundError when command is not found."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo_factory.return_value = MagicMock()
        mock_run.side_effect = FileNotFoundError()

        # Execute
        result = run_shell_command(command="nonexistent_cmd")

        # Verify
        assert not result.is_success
        assert result.error is not None
        assert "Command not found" in result.error

    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    def test_run_shell_command_value_error(self, mock_repo_factory: MagicMock) -> None:
        """Test handling of ValueError from repository operations."""
        # Setup
        mock_repo = MagicMock()
        mock_repo.exists.side_effect = ValueError("Invalid path")
        mock_repo_factory.return_value = mock_repo

        # Execute
        result = run_shell_command(command="ls", directory="invalid/path")

        # Verify
        assert not result.is_success
        assert result.error is not None
        assert "Invalid directory: Invalid path" in result.error

    @patch("pipe.core.tools.run_shell_command.get_project_root")
    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    @patch("subprocess.run")
    def test_run_shell_command_general_exception(
        self,
        mock_run: MagicMock,
        mock_repo_factory: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test handling of unexpected exceptions."""
        # Setup
        mock_get_root.side_effect = Exception("Unexpected error")

        # Execute
        result = run_shell_command(command="ls")

        # Verify
        assert not result.is_success
        assert result.error is not None
        assert "Error inside run_shell_command tool: Unexpected error" in result.error

    @patch("pipe.core.tools.run_shell_command.get_project_root")
    @patch("pipe.core.tools.run_shell_command.FileRepositoryFactory.create")
    @patch("subprocess.run")
    def test_run_shell_command_empty_output(
        self,
        mock_run: MagicMock,
        mock_repo_factory: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test handling of empty stdout and stderr."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo_factory.return_value = MagicMock()

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = None
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Execute
        result = run_shell_command(command="true")

        # Verify
        assert result.data is not None
        assert result.data.stdout == "(empty)"
        assert result.data.stderr == "(empty)"
