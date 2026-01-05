"""Unit tests for TaktAgent."""

import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.agents.takt_agent import TaktAgent, create_takt_agent
from pipe.core.models.settings import Settings


@pytest.fixture
def mock_settings():
    """Create a mock Settings object."""
    settings = MagicMock(spec=Settings)
    settings.timezone = "UTC"
    return settings


@pytest.fixture
def agent(tmp_path, mock_settings):
    """Create a TaktAgent instance with a temporary project root."""
    return TaktAgent(project_root=str(tmp_path), settings=mock_settings)


class TestTaktAgent:
    """Tests for TaktAgent class."""

    def test_init(self, tmp_path, mock_settings):
        """Test initialization of TaktAgent."""
        project_root = str(tmp_path)
        agent = TaktAgent(project_root, mock_settings)
        assert agent.project_root == project_root
        assert agent.settings == mock_settings

    @patch("pipe.core.agents.takt_agent.subprocess.run")
    def test_run_new_session_success_json(self, mock_run, agent):
        """Test run_new_session success with session_id in JSON stdout."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"session_id": "test-session-123"}\n'
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        session_id, stdout, stderr = agent.run_new_session(
            purpose="test purpose",
            background="test background",
            roles="roles.yml",
            instruction="test instruction",
        )

        assert session_id == "test-session-123"
        assert stdout == mock_result.stdout
        assert stderr == mock_result.stderr

        # Verify command
        expected_command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--purpose",
            "test purpose",
            "--background",
            "test background",
            "--roles",
            "roles.yml",
            "--instruction",
            "test instruction",
            "--output-format",
            "json",
        ]
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == expected_command
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True

    @patch("pipe.core.agents.takt_agent.subprocess.run")
    def test_run_new_session_success_stderr(self, mock_run, agent):
        """Test run_new_session success with session_id in stderr fallback."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Some non-JSON output\n"
        mock_result.stderr = "New session created: test-session-456\n"
        mock_run.return_value = mock_result

        session_id, _, _ = agent.run_new_session(
            purpose="p", background="b", roles="r", instruction="i"
        )

        assert session_id == "test-session-456"

    @patch("pipe.core.agents.takt_agent.subprocess.run")
    def test_run_new_session_multi_step_reasoning(self, mock_run, agent):
        """Test run_new_session with multi_step_reasoning flag."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"session_id": "test"}\n'
        mock_run.return_value = mock_result

        agent.run_new_session(
            purpose="p",
            background="b",
            roles="r",
            instruction="i",
            multi_step_reasoning=True,
        )

        args, _ = mock_run.call_args
        assert "--multi-step-reasoning" in args[0]

    @patch("pipe.core.agents.takt_agent.subprocess.run")
    def test_run_new_session_failure(self, mock_run, agent):
        """Test run_new_session failure raises RuntimeError."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error message"
        mock_run.return_value = mock_result

        with pytest.raises(
            RuntimeError, match="takt command failed with return code 1"
        ):
            agent.run_new_session("p", "b", "r", "i")

    @patch("pipe.core.agents.takt_agent.subprocess.run")
    def test_run_new_session_extraction_failure(self, mock_run, agent):
        """Test run_new_session raises RuntimeError if session_id cannot be extracted."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "No session ID here"
        mock_result.stderr = "Nothing here either"
        mock_run.return_value = mock_result

        with pytest.raises(
            RuntimeError, match="Failed to extract session ID from takt output"
        ):
            agent.run_new_session("p", "b", "r", "i")

    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    @patch("pipe.core.agents.takt_agent.subprocess.run")
    def test_run_existing_session_success(self, mock_run, mock_pm_cls, agent):
        """Test run_existing_session success."""
        mock_pm = mock_pm_cls.return_value
        mock_pm.is_running.return_value = False

        mock_result = MagicMock()
        mock_result.stdout = "output"
        mock_result.stderr = "error"
        mock_run.return_value = mock_result

        stdout, stderr = agent.run_existing_session(
            session_id="test-session",
            instruction="test instruction",
            references=["ref1.txt"],
            artifacts=["art1.txt"],
            procedure="proc.md",
            extra_env={"FOO": "BAR"},
        )

        assert stdout == "output"
        assert stderr == "error"

        # Verify command
        expected_command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--session",
            "test-session",
            "--instruction",
            "test instruction",
            "--output-format",
            "json",
            "--references",
            "ref1.txt",
            "--artifacts",
            "art1.txt",
            "--procedure",
            "proc.md",
        ]
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == expected_command
        assert kwargs["env"]["FOO"] == "BAR"
        assert "PYTHONPATH" in kwargs["env"]

    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    def test_run_existing_session_already_running(self, mock_pm_cls, agent):
        """Test run_existing_session raises RuntimeError if session is already running."""
        mock_pm = mock_pm_cls.return_value
        mock_pm.is_running.return_value = True

        with pytest.raises(RuntimeError, match="is already running"):
            agent.run_existing_session("test-session", "i")

    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    @patch("pipe.core.agents.takt_agent.subprocess.run")
    def test_run_existing_session_failure(self, mock_run, mock_pm_cls, agent):
        """Test run_existing_session failure raises RuntimeError."""
        mock_pm = mock_pm_cls.return_value
        mock_pm.is_running.return_value = False

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="takt", stderr="Error message"
        )

        with pytest.raises(RuntimeError, match="takt command failed with exit code 1"):
            agent.run_existing_session("test-session", "i")

    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    @patch("pipe.core.agents.takt_agent.subprocess.Popen")
    def test_run_existing_session_stream_success(self, mock_popen, mock_pm_cls, agent):
        """Test run_existing_session_stream success."""
        mock_pm = mock_pm_cls.return_value
        mock_pm.is_running.return_value = False

        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.stdout.readline.side_effect = ["line1\n", "line2\n", ""]
        mock_process.stderr.read.return_value = ""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        lines = list(agent.run_existing_session_stream("test-session", "i"))

        assert lines == ["line1\n", "line2\n"]
        mock_pm.register_process.assert_called_once_with("test-session", 12345)
        mock_pm.cleanup_process.assert_called_once_with("test-session")

    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    def test_run_existing_session_stream_already_running(self, mock_pm_cls, agent):
        """Test run_existing_session_stream raises RuntimeError if session is already running."""
        mock_pm = mock_pm_cls.return_value
        mock_pm.is_running.return_value = True

        with pytest.raises(RuntimeError, match="is already running"):
            next(agent.run_existing_session_stream("test-session", "i"))

    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    @patch("pipe.core.agents.takt_agent.subprocess.Popen")
    def test_run_existing_session_stream_registration_failure(
        self, mock_popen, mock_pm_cls, agent
    ):
        """Test run_existing_session_stream failure if registration fails."""
        mock_pm = mock_pm_cls.return_value
        mock_pm.is_running.return_value = False
        mock_pm.register_process.side_effect = Exception("Registration failed")

        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        with pytest.raises(RuntimeError, match="Failed to register process"):
            next(agent.run_existing_session_stream("test-session", "i"))

        mock_process.terminate.assert_called_once()

    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    @patch("pipe.core.agents.takt_agent.subprocess.Popen")
    def test_run_existing_session_stream_command_failure(
        self, mock_popen, mock_pm_cls, agent
    ):
        """Test run_existing_session_stream failure if command returns non-zero."""
        mock_pm = mock_pm_cls.return_value
        mock_pm.is_running.return_value = False

        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.stdout.readline.side_effect = ["line1\n", ""]
        mock_process.stderr.read.return_value = "Error message"
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process

        gen = agent.run_existing_session_stream("test-session", "i")
        assert next(gen) == "line1\n"

        with pytest.raises(
            RuntimeError, match="takt command failed with return code 1"
        ):
            next(gen)

        mock_pm.cleanup_process.assert_called_once_with("test-session")

    def test_run_instruction_stream_unified(self, agent):
        """Test run_instruction_stream_unified delegates to run_existing_session_stream."""
        with patch.object(agent, "run_existing_session_stream") as mock_run_stream:
            mock_run_stream.return_value = iter(["line1"])
            lines = list(
                agent.run_instruction_stream_unified("test-session", "instruction")
            )
            assert lines == ["line1"]
            mock_run_stream.assert_called_once_with(
                session_id="test-session",
                instruction="instruction",
                multi_step_reasoning=False,
            )


def test_create_takt_agent(tmp_path, mock_settings):
    """Test create_takt_agent factory function."""
    project_root = str(tmp_path)
    agent = create_takt_agent(project_root, mock_settings)
    assert isinstance(agent, TaktAgent)
    assert agent.project_root == project_root
    assert agent.settings == mock_settings
