import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.tools.run_shell_command import run_shell_command


class TestRunShellCommandTool(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..")
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("subprocess.run")
    def test_run_shell_command_success(self, mock_subprocess_run):
        mock_process = MagicMock()
        mock_process.stdout = "Success output"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        result = run_shell_command(command="echo 'hello'")

        self.assertEqual(result["stdout"], "Success output")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["error"], "(none)")

    @patch("subprocess.run")
    def test_run_shell_command_failure(self, mock_subprocess_run):
        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_process.stderr = "Error output"
        mock_process.returncode = 1
        mock_subprocess_run.return_value = mock_process

        result = run_shell_command(command="ls non_existent_dir")

        self.assertEqual(result["stderr"], "Error output")
        self.assertEqual(result["exit_code"], 1)
        self.assertIn("Command failed", result["error"])

    def test_directory_does_not_exist(self):
        result = run_shell_command(command="ls", directory="non_existent_dir")
        self.assertIn("error", result)
        self.assertIn("Directory does not exist", result["error"])

    def test_directory_outside_project_root(self):
        result = run_shell_command(command="ls", directory="/etc")
        self.assertIn("error", result)
        self.assertIn(
            "Running commands outside project root is not allowed", result["error"]
        )

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_command_not_found(self, mock_subprocess_run):
        result = run_shell_command(command="non_existent_command")
        self.assertIn("error", result)
        self.assertIn("Command not found", result["error"])

    @patch("subprocess.run", side_effect=Exception("Test exception"))
    def test_general_exception(self, mock_subprocess_run):
        result = run_shell_command(command="some_command")
        self.assertIn("error", result)
        self.assertIn("Error inside run_shell_command tool", result["error"])

    @patch("subprocess.run")
    @patch("pipe.core.tools.run_shell_command.os.path.abspath")
    def test_run_in_specified_directory(self, mock_abspath, mock_subprocess_run):
        """
        Tests that the command is run in the specified directory.
        """
        # Make abspath return the temp_dir as the project root
        mock_abspath.side_effect = lambda path: (
            self.temp_dir.name
            if ".." in path
            else os.path.join(self.temp_dir.name, os.path.basename(path))
        )

        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        # Create a subdirectory within the temp dir to act as a valid target
        sub_dir = os.path.join(self.temp_dir.name, "sub")
        os.makedirs(sub_dir)

        run_shell_command(command="ls", directory=sub_dir)

        # Check that subprocess.run was called with the correct cwd
        mock_subprocess_run.assert_called_once()
        call_kwargs = mock_subprocess_run.call_args.kwargs
        self.assertEqual(call_kwargs.get("cwd"), sub_dir)


if __name__ == "__main__":
    unittest.main()
