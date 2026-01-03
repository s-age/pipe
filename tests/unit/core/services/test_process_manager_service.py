"""Unit tests for ProcessManagerService."""

import signal
from unittest.mock import patch

import pytest
from pipe.core.services.process_manager_service import ProcessManagerService


@pytest.fixture
def mock_repository_class():
    """Fixture to patch ProcessFileRepository class."""
    with patch(
        "pipe.core.services.process_manager_service.ProcessFileRepository"
    ) as mock:
        yield mock


@pytest.fixture
def mock_psutil():
    """Fixture to patch psutil module."""
    with patch("pipe.core.services.process_manager_service.psutil") as mock:
        yield mock


@pytest.fixture
def service(mock_repository_class):
    """Fixture to create ProcessManagerService instance with mocked repository."""
    return ProcessManagerService(project_root="/mock/root")


class TestProcessManagerServiceInit:
    """Tests for ProcessManagerService.__init__."""

    def test_init(self, mock_repository_class):
        """Test initialization and repository setup."""
        project_root = "/mock/root"
        service = ProcessManagerService(project_root)

        assert service.project_root == project_root
        mock_repository_class.assert_called_once()
        # Verify processes_dir calculation
        args, _ = mock_repository_class.call_args
        assert args[0].endswith(".processes")


class TestProcessManagerServiceRegisterProcess:
    """Tests for ProcessManagerService.register_process."""

    def test_register_new_process(self, service, mock_psutil):
        """Test registering a process when no existing process is running."""
        service.repository.read_pid.return_value = None

        service.register_process("session-1", 1234)

        service.repository.write_pid.assert_called_once_with("session-1", 1234)

    def test_register_already_running_raises_error(self, service, mock_psutil):
        """Test that registering an already running session raises RuntimeError."""
        service.repository.read_pid.return_value = 1234
        mock_psutil.pid_exists.return_value = True

        with pytest.raises(RuntimeError, match="already running"):
            service.register_process("session-1", 5678)

    def test_register_stale_process_cleans_up(self, service, mock_psutil):
        """Test that registering over a stale process file cleans it up first."""
        service.repository.read_pid.return_value = 1234
        mock_psutil.pid_exists.return_value = False

        service.register_process("session-1", 5678)

        service.repository.delete_pid_file.assert_called_once_with("session-1")
        service.repository.write_pid.assert_called_once_with("session-1", 5678)


class TestProcessManagerServiceGetPid:
    """Tests for ProcessManagerService.get_pid."""

    def test_get_pid_found(self, service):
        """Test getting PID when it exists."""
        service.repository.read_pid.return_value = 1234
        assert service.get_pid("session-1") == 1234

    def test_get_pid_not_found(self, service):
        """Test getting PID when it doesn't exist."""
        service.repository.read_pid.return_value = None
        assert service.get_pid("session-1") is None


class TestProcessManagerServiceIsRunning:
    """Tests for ProcessManagerService.is_running."""

    def test_is_running_true(self, service, mock_psutil):
        """Test is_running returns True when process exists."""
        service.repository.read_pid.return_value = 1234
        mock_psutil.pid_exists.return_value = True

        assert service.is_running("session-1") is True

    def test_is_running_false_no_pid(self, service):
        """Test is_running returns False when no PID file exists."""
        service.repository.read_pid.return_value = None
        assert service.is_running("session-1") is False

    def test_is_running_false_stale_cleans_up(self, service, mock_psutil):
        """Test is_running returns False and cleans up for stale process."""
        service.repository.read_pid.return_value = 1234
        mock_psutil.pid_exists.return_value = False

        assert service.is_running("session-1") is False
        service.repository.delete_pid_file.assert_called_once_with("session-1")


class TestProcessManagerServiceKillProcess:
    """Tests for ProcessManagerService.kill_process."""

    @patch("pipe.core.services.process_manager_service.os.kill")
    @patch("pipe.core.services.process_manager_service.time.sleep")
    def test_kill_process_graceful(self, mock_sleep, mock_kill, service, mock_psutil):
        """Test graceful termination with SIGTERM."""
        service.repository.read_pid.return_value = 1234
        # First check: exists. After SIGTERM: doesn't exist.
        mock_psutil.pid_exists.side_effect = [True, False]

        result = service.kill_process("session-1")

        assert result is True
        mock_kill.assert_called_once_with(1234, signal.SIGTERM)

    @patch("pipe.core.services.process_manager_service.os.kill")
    @patch("pipe.core.services.process_manager_service.time.sleep")
    def test_kill_process_forceful(self, mock_sleep, mock_kill, service, mock_psutil):
        """Test forceful kill with SIGKILL after SIGTERM timeout."""
        service.repository.read_pid.return_value = 1234
        # 1 (initial check) + 30 (wait loop) + 1 (final check)
        # Let's make it stay alive during wait loop, then die after SIGKILL
        mock_psutil.pid_exists.side_effect = [True] + [True] * 30 + [False]

        result = service.kill_process("session-1")

        assert result is True
        mock_kill.assert_any_call(1234, signal.SIGTERM)
        mock_kill.assert_any_call(1234, signal.SIGKILL)

    def test_kill_process_not_found(self, service):
        """Test kill_process returns False when no PID file exists."""
        service.repository.read_pid.return_value = None
        assert service.kill_process("session-1") is False

    def test_kill_process_already_dead(self, service, mock_psutil):
        """Test kill_process returns False when process doesn't exist in system."""
        service.repository.read_pid.return_value = 1234
        mock_psutil.pid_exists.return_value = False

        assert service.kill_process("session-1") is False

    @patch("pipe.core.services.process_manager_service.os.kill")
    def test_kill_process_lookup_error(self, mock_kill, service, mock_psutil):
        """Test handling of ProcessLookupError during kill."""
        service.repository.read_pid.return_value = 1234
        mock_psutil.pid_exists.return_value = True
        mock_kill.side_effect = ProcessLookupError()

        assert service.kill_process("session-1") is True

    @patch("pipe.core.services.process_manager_service.os.kill")
    def test_kill_process_exception(self, mock_kill, service, mock_psutil):
        """Test handling of generic exception during kill."""
        service.repository.read_pid.return_value = 1234
        mock_psutil.pid_exists.return_value = True
        mock_kill.side_effect = Exception("Unexpected error")

        assert service.kill_process("session-1") is False


class TestProcessManagerServiceCleanupProcess:
    """Tests for ProcessManagerService.cleanup_process."""

    def test_cleanup_process(self, service):
        """Test cleaning up process information."""
        service.cleanup_process("session-1")
        service.repository.delete_pid_file.assert_called_once_with("session-1")


class TestProcessManagerServiceCleanupStaleProcesses:
    """Tests for ProcessManagerService.cleanup_stale_processes."""

    def test_cleanup_stale_processes(self, service, mock_psutil):
        """Test cleaning up multiple stale process files."""
        service.repository.list_all_session_ids.return_value = ["s1", "s2", "s3"]
        service.repository.read_pid.side_effect = [101, 102, 103]
        # s1: running, s2: stale, s3: stale
        mock_psutil.pid_exists.side_effect = [True, False, False]

        service.cleanup_stale_processes()

        assert service.repository.delete_pid_file.call_count == 2
        service.repository.delete_pid_file.assert_any_call("s2")
        service.repository.delete_pid_file.assert_any_call("s3")

    def test_cleanup_stale_processes_none_stale(self, service, mock_psutil):
        """Test cleanup when no processes are stale."""
        service.repository.list_all_session_ids.return_value = ["s1"]
        service.repository.read_pid.return_value = 101
        mock_psutil.pid_exists.return_value = True

        service.cleanup_stale_processes()

        service.repository.delete_pid_file.assert_not_called()
