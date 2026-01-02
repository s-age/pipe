"""Unit tests for SessionInstructionService."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.services.session_instruction_service import SessionInstructionService

from tests.factories.models import SessionFactory


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock()
    settings.timezone = "UTC"
    return settings


@pytest.fixture
def service(mock_settings):
    """Create SessionInstructionService instance."""
    return SessionInstructionService(project_root="/mock/root", settings=mock_settings)


class TestSessionInstructionServiceInit:
    """Tests for SessionInstructionService.__init__."""

    def test_init(self, mock_settings):
        """Test initialization."""
        service = SessionInstructionService(
            project_root="/mock/root", settings=mock_settings
        )
        assert service.project_root == "/mock/root"
        assert service.settings == mock_settings


class TestSessionInstructionServiceExecuteInstructionStream:
    """Tests for SessionInstructionService.execute_instruction_stream."""

    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_already_running(self, MockProcessManager, service):
        """Test behavior when session is already running."""
        session = SessionFactory.create(session_id="test-session")
        mock_pm = MockProcessManager.return_value
        mock_pm.is_running.return_value = True

        generator = service.execute_instruction_stream(session, "test instruction")
        events = list(generator)

        assert len(events) == 1
        assert "error" in events[0]
        assert "already running" in events[0]["error"]
        mock_pm.is_running.assert_called_once_with("test-session")

    @patch("pipe.core.services.session_instruction_service.subprocess.Popen")
    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_success_stream(self, MockProcessManager, MockPopen, service):
        """Test successful execution and streaming."""
        session = SessionFactory.create(session_id="test-session")
        mock_pm = MockProcessManager.return_value
        mock_pm.is_running.return_value = False

        mock_process = MagicMock()
        MockPopen.return_value = mock_process
        mock_process.poll.return_value = None
        mock_process.wait.return_value = 0

        # Mock stdout as an iterator of lines
        mock_process.stdout = MagicMock()
        mock_process.stdout.readline.side_effect = [
            '{"type": "content", "text": "Hello"}\n',
            '{"type": "done"}\n',
            "",
        ]

        generator = service.execute_instruction_stream(session, "test instruction")
        events = list(generator)

        assert events[0] == {"type": "start", "session_id": "test-session"}
        assert events[1] == {"type": "content", "text": "Hello"}
        assert events[2] == {"type": "done"}

        MockPopen.assert_called_once()
        args, kwargs = MockPopen.call_args
        command = args[0]
        assert "pipe.cli.takt" in command
        assert "--session" in command
        assert "test-session" in command
        assert "--instruction" in command
        assert "test instruction" in command
        assert "--output-format" in command
        assert "stream-json" in command
        assert kwargs["cwd"] == "/mock/root"

    @patch("pipe.core.services.session_instruction_service.subprocess.Popen")
    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_multi_step_reasoning_enabled(self, MockProcessManager, MockPopen, service):
        """Test command includes --multi-step-reasoning when enabled."""
        session = SessionFactory.create(
            session_id="test-session", multi_step_reasoning_enabled=True
        )
        MockProcessManager.return_value.is_running.return_value = False

        mock_process = MagicMock()
        MockPopen.return_value = mock_process
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = ""
        mock_process.wait.return_value = 0

        list(service.execute_instruction_stream(session, "test instruction"))

        args, _ = MockPopen.call_args
        command = args[0]
        assert "--multi-step-reasoning" in command

    @patch("pipe.core.services.session_instruction_service.subprocess.Popen")
    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_process_exited_unexpectedly(self, MockProcessManager, MockPopen, service):
        """Test behavior when process exits immediately with error."""
        session = SessionFactory.create(session_id="test-session")
        MockProcessManager.return_value.is_running.return_value = False

        mock_process = MagicMock()
        MockPopen.return_value = mock_process
        mock_process.poll.return_value = 1  # Already exited
        mock_process.stderr.read.return_value = "Some error"

        generator = service.execute_instruction_stream(session, "test instruction")
        events = list(generator)

        assert events[0] == {"type": "start", "session_id": "test-session"}
        assert "error" in events[1]
        assert "Process exited unexpectedly: Some error" in events[1]["error"]

    @patch("pipe.core.services.session_instruction_service.subprocess.Popen")
    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_non_json_output(self, MockProcessManager, MockPopen, service):
        """Test behavior when output is not JSON."""
        session = SessionFactory.create(session_id="test-session")
        MockProcessManager.return_value.is_running.return_value = False

        mock_process = MagicMock()
        MockPopen.return_value = mock_process
        mock_process.poll.return_value = None
        mock_process.wait.return_value = 0
        mock_process.stdout.readline.side_effect = ["Plain text output\n", ""]

        generator = service.execute_instruction_stream(session, "test instruction")
        events = list(generator)

        assert events[1] == {"content": "Plain text output"}

    @patch("pipe.core.services.session_instruction_service.subprocess.Popen")
    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_process_failed_exit_code(self, MockProcessManager, MockPopen, service):
        """Test behavior when process returns non-zero exit code."""
        session = SessionFactory.create(session_id="test-session")
        MockProcessManager.return_value.is_running.return_value = False

        mock_process = MagicMock()
        MockPopen.return_value = mock_process
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = ""
        mock_process.wait.return_value = 1
        mock_process.stderr.read.return_value = "Runtime error"

        generator = service.execute_instruction_stream(session, "test instruction")
        events = list(generator)

        assert "error" in events[-1]
        assert "Process failed with code 1: Runtime error" in events[-1]["error"]

    @patch("pipe.core.services.session_instruction_service.subprocess.Popen")
    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_exception_handling(self, MockProcessManager, MockPopen, service):
        """Test behavior when an exception occurs during execution."""
        session = SessionFactory.create(session_id="test-session")
        MockProcessManager.return_value.is_running.return_value = False
        MockPopen.side_effect = Exception("Unexpected failure")

        generator = service.execute_instruction_stream(session, "test instruction")
        events = list(generator)

        assert events[0] == {"type": "start", "session_id": "test-session"}
        assert events[1] == {"error": "Unexpected failure"}

    @patch("pipe.core.services.session_instruction_service.subprocess.Popen")
    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_cleanup_on_finally(self, MockProcessManager, MockPopen, service):
        """Test process termination in finally block."""
        session = SessionFactory.create(session_id="test-session")
        MockProcessManager.return_value.is_running.return_value = False

        mock_process = MagicMock()
        MockPopen.return_value = mock_process
        mock_process.poll.side_effect = [
            None,
            None,
            0,
        ]  # Still running when finally hits
        mock_process.stdout.readline.side_effect = Exception("Force exit")

        generator = service.execute_instruction_stream(session, "test instruction")
        events = list(generator)

        assert any("Force exit" in str(e.get("error")) for e in events)
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called()

    @patch("pipe.core.services.session_instruction_service.subprocess.Popen")
    @patch("pipe.core.services.session_instruction_service.ProcessManagerService")
    def test_cleanup_kill_on_timeout(self, MockProcessManager, MockPopen, service):
        """Test process kill when terminate times out."""
        session = SessionFactory.create(session_id="test-session")
        MockProcessManager.return_value.is_running.return_value = False

        mock_process = MagicMock()
        MockPopen.return_value = mock_process
        mock_process.poll.return_value = None
        mock_process.stdout.readline.side_effect = Exception("Force exit")
        mock_process.wait.side_effect = [
            subprocess.TimeoutExpired(cmd="", timeout=3),
            0,
        ]

        generator = service.execute_instruction_stream(session, "test instruction")
        events = list(generator)

        assert any("Force exit" in str(e.get("error")) for e in events)
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
