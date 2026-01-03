"""Unit tests for task_executor_base.py."""

from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from pipe.core.models.task import AgentTask, ScriptTask
from pipe.core.services.task_executor_base import (
    execute_agent_task,
    execute_script_task,
)


@pytest.fixture
def mock_agent_task():
    """Create a mock AgentTask."""
    return AgentTask(
        instruction="Test instruction",
        roles=["role1.md"],
        procedure="procedure1.md",
        references=["ref1.py"],
        references_persist=["ref2.py"],
        artifacts=["art1.txt"],
    )


@pytest.fixture
def mock_script_task():
    """Create a mock ScriptTask."""
    return ScriptTask(
        script="test_script.sh",
        args=["arg1", "arg2"],
    )


class TestExecuteAgentTask:
    """Tests for execute_agent_task function."""

    @freeze_time("2025-01-01 10:00:00")
    @patch("pipe.core.services.task_executor_base.subprocess.run")
    def test_execute_agent_task_existing_session(self, mock_run, mock_agent_task):
        """Test executing agent task with an existing session."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout='{"session_id": "test-session"}', stderr=""
        )

        result = execute_agent_task(
            task=mock_agent_task,
            session_id="existing-session",
            project_root="/tmp/project",
        )

        assert result.exit_code == 0
        assert result.task_type == "agent"
        assert result.started_at == "2025-01-01T10:00:00+00:00"
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert "--session" in cmd
        assert "existing-session" in cmd
        assert "--instruction" in cmd
        assert "Test instruction" in cmd
        assert kwargs["cwd"] == "/tmp/project"

    @freeze_time("2025-01-01 10:00:00")
    @patch("pipe.core.services.task_executor_base.subprocess.run")
    def test_execute_agent_task_new_session(self, mock_run, mock_agent_task):
        """Test executing agent task and creating a new session."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout='{"session_id": "new-session"}', stderr=""
        )

        result = execute_agent_task(
            task=mock_agent_task,
            session_id=None,
            project_root="/tmp/project",
            purpose="Test Purpose",
            background="Test Background",
            parent_session_id="parent-123",
        )

        assert result.exit_code == 0
        assert "[CREATED_SESSION:new-session]" in result.output_preview
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "--purpose" in cmd
        assert "Test Purpose" in cmd
        assert "--background" in cmd
        assert "Test Background" in cmd
        assert "--parent" in cmd
        assert "parent-123" in cmd
        assert "--roles" in cmd
        assert "role1.md" in cmd
        assert "--procedure" in cmd
        assert "procedure1.md" in cmd
        assert "--references" in cmd
        assert "ref1.py" in cmd
        assert "--references-persist" in cmd
        assert "ref2.py" in cmd
        assert "--artifacts" in cmd
        assert "art1.txt" in cmd

    def test_execute_agent_task_new_session_missing_args(self, mock_agent_task):
        """Test that ValueError is raised when purpose or background is missing."""
        with pytest.raises(ValueError, match="purpose and background are required"):
            execute_agent_task(
                task=mock_agent_task,
                session_id=None,
                project_root="/tmp/project",
            )

    @patch("pipe.core.services.task_executor_base.subprocess.run")
    def test_execute_agent_task_extract_session_id_json_multiline(
        self, mock_run, mock_agent_task
    ):
        """Test session ID extraction from multiline stdout JSON."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Log line 1\nLog line 2\n{"session_id": "json-session"}',
            stderr="",
        )

        result = execute_agent_task(
            task=mock_agent_task,
            session_id=None,
            project_root="/tmp/project",
            purpose="P",
            background="B",
        )

        assert "[CREATED_SESSION:json-session]" in result.output_preview

    @patch("pipe.core.services.task_executor_base.subprocess.run")
    def test_execute_agent_task_extract_session_id_regex_stdout(
        self, mock_run, mock_agent_task
    ):
        """Test session ID extraction from stdout using regex."""
        # Regex expects [a-f0-9/]+
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Some text "session_id": "abc123def" more text',
            stderr="",
        )

        result = execute_agent_task(
            task=mock_agent_task,
            session_id=None,
            project_root="/tmp/project",
            purpose="P",
            background="B",
        )

        assert "[CREATED_SESSION:abc123def]" in result.output_preview

    @patch("pipe.core.services.task_executor_base.subprocess.run")
    def test_execute_agent_task_extract_session_id_regex_stderr(
        self, mock_run, mock_agent_task
    ):
        """Test session ID extraction from stderr using regex."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Normal output",
            stderr="New session created: stderr-session",
        )

        result = execute_agent_task(
            task=mock_agent_task,
            session_id=None,
            project_root="/tmp/project",
            purpose="P",
            background="B",
        )

        assert "[CREATED_SESSION:stderr-session]" in result.output_preview

    @patch("pipe.core.repositories.streaming_log_repository.StreamingLogRepository")
    @patch("pipe.core.repositories.settings_repository.SettingsRepository")
    @patch("pipe.core.services.task_executor_base.subprocess.run")
    def test_execute_agent_task_failure_logging(
        self, mock_run, mock_settings_repo_cls, mock_streaming_repo_cls, mock_agent_task
    ):
        """Test that errors are logged to StreamingLogRepository on failure."""
        mock_run.return_value = MagicMock(
            returncode=1, stdout="Some output", stderr="Some error"
        )
        mock_settings = MagicMock()
        mock_settings_repo_cls.return_value.load.return_value = mock_settings
        mock_streaming_instance = mock_streaming_repo_cls.return_value

        execute_agent_task(
            task=mock_agent_task,
            session_id="session-1",
            project_root="/tmp/project",
            parent_session_id="parent-1",
        )

        mock_streaming_instance.append_log.assert_called_once()
        log_msg = mock_streaming_instance.append_log.call_args[0][0]
        assert "Agent task failed with exit code 1" in log_msg
        assert "STDERR:\nSome error" in log_msg
        assert "STDOUT:\nSome output" in log_msg

    @patch("pipe.core.services.task_executor_base.subprocess.run")
    def test_execute_agent_task_failure_logging_with_created_session(
        self, mock_run, mock_agent_task
    ):
        """Test failure logging when a session was created but command failed."""
        # This covers the case where created_session_id is found even on failure
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='{"session_id": "failed-but-created"}',
            stderr="Command failed",
        )

        with (
            patch(
                "pipe.core.repositories.settings_repository.SettingsRepository"
            ) as mock_settings_repo_cls,
            patch(
                "pipe.core.repositories.streaming_log_repository.StreamingLogRepository"
            ) as mock_streaming_repo_cls,
        ):
            mock_settings = MagicMock()
            mock_settings_repo_cls.return_value.load.return_value = mock_settings
            mock_streaming_instance = mock_streaming_repo_cls.return_value

            execute_agent_task(
                task=mock_agent_task,
                session_id=None,
                project_root="/tmp/project",
                purpose="P",
                background="B",
                parent_session_id="parent-1",
            )

            log_msg = mock_streaming_instance.append_log.call_args[0][0]
            assert "Created session: failed-but-created" in log_msg


class TestExecuteScriptTask:
    """Tests for execute_script_task function."""

    @freeze_time("2025-01-01 10:00:00")
    @patch("pipe.core.services.task_executor_base.subprocess.run")
    @patch("pipe.core.services.task_executor_base.validate_script_path")
    def test_execute_script_task_success(
        self, mock_validate, mock_run, mock_script_task
    ):
        """Test successful script task execution."""
        mock_validate.return_value = "/tmp/project/scripts/test_script.sh"
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Script output", stderr=""
        )

        result = execute_script_task(
            task=mock_script_task,
            session_id="session-1",
            project_root="/tmp/project",
        )

        assert result.exit_code == 0
        assert result.task_type == "script"
        assert result.output_preview == "Script output"
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == ["/tmp/project/scripts/test_script.sh", "arg1", "arg2"]
        assert kwargs["env"]["PIPE_SESSION_ID"] == "session-1"
        assert kwargs["env"]["PIPE_PROJECT_ROOT"] == "/tmp/project"

    @patch("pipe.core.services.task_executor_base.validate_script_path")
    def test_execute_script_task_validation_not_found(
        self, mock_validate, mock_script_task
    ):
        """Test script task execution when script is not found."""
        mock_validate.side_effect = FileNotFoundError("Script not found")

        with pytest.raises(FileNotFoundError, match="Script not found"):
            execute_script_task(
                task=mock_script_task,
                session_id="session-1",
                project_root="/tmp/project",
            )

    @patch("pipe.core.services.task_executor_base.validate_script_path")
    def test_execute_script_task_validation_error(
        self, mock_validate, mock_script_task
    ):
        """Test script task execution when validation raises generic error."""
        mock_validate.side_effect = Exception("Validation error")

        with pytest.raises(Exception, match="Validation error"):
            execute_script_task(
                task=mock_script_task,
                session_id="session-1",
                project_root="/tmp/project",
            )
