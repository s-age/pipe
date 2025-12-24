import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pipe.core.utils.task_launcher import launch_manager


class TestLaunchManager:
    """Tests for task_launcher utility."""

    @pytest.fixture
    def mock_project_root(self, tmp_path):
        """Mock get_project_root to return a temporary directory."""
        with patch("pipe.core.utils.task_launcher.get_project_root") as mock:
            mock.return_value = str(tmp_path)
            yield str(tmp_path)

    @pytest.fixture
    def mock_popen(self):
        """Mock subprocess.Popen."""
        with patch("subprocess.Popen") as mock:
            yield mock

    @pytest.fixture
    def mock_sys_exit(self):
        """Mock sys.exit to prevent the test process from exiting."""
        with patch("sys.exit") as mock:
            yield mock

    @pytest.fixture
    def mock_process_manager(self):
        """Mock ProcessManagerService."""
        with patch(
            "pipe.core.services.process_manager_service.ProcessManagerService"
        ) as mock_class:
            mock_instance = mock_class.return_value
            yield mock_instance

    def test_launch_manager_serial(
        self, mock_project_root, mock_popen, mock_sys_exit, mock_process_manager
    ):
        """Test launching a serial manager."""
        tasks = [{"id": "task1", "type": "shell", "command": "echo test"}]
        parent_id = "parent123"

        launch_manager(
            manager_type="serial",
            tasks=tasks,
            parent_session_id=parent_id,
        )

        # Verify JSON metadata file was created and contains correct data
        sessions_dir = Path(mock_project_root) / ".pipe_sessions"
        tasks_file = sessions_dir / f"{parent_id}_tasks.json"
        assert tasks_file.exists()

        with open(tasks_file, encoding="utf-8") as f:
            data = json.load(f)
            assert data["parent_session_id"] == parent_id
            assert data["tasks"] == tasks
            assert data["child_session_id"] is None

        # Verify subprocess.Popen was called with correct arguments
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        cmd = args[0]

        assert cmd[0] == "poetry"
        assert cmd[1] == "run"
        assert "pipe.core.services.serial_manager_service" in cmd
        assert "--parent-session" in cmd
        assert parent_id in cmd

        assert kwargs["cwd"] == mock_project_root
        assert kwargs["start_new_session"] is True
        assert kwargs["stdout"] is not None  # It should be a file object
        assert kwargs["stderr"] == -2  # subprocess.STDOUT is -2

        # Verify process cleanup was called before exit
        mock_process_manager.cleanup_process.assert_called_once_with(parent_id)

        # Verify sys.exit(0) was called
        mock_sys_exit.assert_called_once_with(0)

    def test_launch_manager_parallel(
        self, mock_project_root, mock_popen, mock_sys_exit, mock_process_manager
    ):
        """Test launching a parallel manager with extra arguments."""
        tasks = [{"id": "task1"}]
        parent_id = "parent456"

        launch_manager(
            manager_type="parallel",
            tasks=tasks,
            parent_session_id=parent_id,
            max_workers=8,
        )

        # Verify subprocess.Popen was called with parallel manager and max-workers
        mock_popen.assert_called_once()
        args, _ = mock_popen.call_args
        cmd = args[0]

        assert "pipe.core.services.parallel_manager_service" in cmd
        assert "--max-workers" in cmd
        assert "8" in cmd

        # Verify metadata file
        tasks_file = (
            Path(mock_project_root) / ".pipe_sessions" / f"{parent_id}_tasks.json"
        )
        assert tasks_file.exists()

        # Verify process cleanup was called before exit
        mock_process_manager.cleanup_process.assert_called_once_with(parent_id)

        mock_sys_exit.assert_called_once_with(0)

    def test_launch_manager_with_child_session(
        self, mock_project_root, mock_popen, mock_sys_exit, mock_process_manager
    ):
        """Test launching manager with child session info."""
        tasks = [{"id": "task1"}]
        parent_id = "p1"
        child_id = "c1"
        purpose = "testing"
        background = "env"

        launch_manager(
            manager_type="serial",
            tasks=tasks,
            parent_session_id=parent_id,
            child_session_id=child_id,
            purpose=purpose,
            background=background,
        )

        # Verify JSON metadata file contains all info
        tasks_file = (
            Path(mock_project_root) / ".pipe_sessions" / f"{parent_id}_tasks.json"
        )
        with open(tasks_file, encoding="utf-8") as f:
            data = json.load(f)
            assert data["child_session_id"] == child_id
            assert data["purpose"] == purpose
            assert data["background"] == background

        # Verify process cleanup was called before exit
        mock_process_manager.cleanup_process.assert_called_once_with(parent_id)

        mock_sys_exit.assert_called_once_with(0)

    def test_launch_manager_unknown_type(
        self, mock_project_root, mock_popen, mock_sys_exit
    ):
        """Test that unknown manager type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown manager type: invalid"):
            launch_manager(
                manager_type="invalid",
                tasks=[],
                parent_session_id="test",
            )

        # Verify no process was launched and sys.exit was not called
        mock_popen.assert_not_called()
        mock_sys_exit.assert_not_called()

    def test_launch_manager_creates_log_file(
        self, mock_project_root, mock_popen, mock_sys_exit, mock_process_manager
    ):
        """Test that log file is created in the sessions directory."""
        parent_id = "log_test"
        launch_manager(
            manager_type="serial",
            tasks=[],
            parent_session_id=parent_id,
        )

        log_file = (
            Path(mock_project_root)
            / ".pipe_sessions"
            / f"{parent_id}_serial_manager.log"
        )
        assert log_file.exists()

        # Verify process cleanup was called before exit
        mock_process_manager.cleanup_process.assert_called_once_with(parent_id)

        mock_sys_exit.assert_called_once_with(0)
