"""Unit tests for invoke_serial_children tool."""

import json
from unittest.mock import patch

import pytest
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.invoke_serial_children import invoke_serial_children


class TestInvokeSerialChildren:
    """Tests for invoke_serial_children function."""

    @pytest.fixture
    def mock_env(self):
        """Mock environment variables."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "parent-session-123"
            yield mock_getenv

    @pytest.fixture
    def mock_launch(self):
        """Mock launch_manager."""
        with patch(
            "pipe.core.tools.invoke_serial_children.launch_manager"
        ) as mock_launch:
            yield mock_launch

    def test_missing_parent_session_id(self, mock_launch):
        """Test error when PIPE_SESSION_ID is not set."""
        with patch("os.getenv", return_value=None):
            result = invoke_serial_children(
                tasks=[{"type": "script", "command": "echo hello"}]
            )

        assert isinstance(result, ToolResult)
        assert result.is_success is False
        assert "Parent session ID not found" in result.error

    def test_invalid_task_json(self, mock_env, mock_launch):
        """Test error when task string is invalid JSON."""
        result = invoke_serial_children(tasks=["invalid-json"])

        assert result.is_success is False
        assert "Failed to parse task as JSON" in result.error

    def test_missing_purpose_background(self, mock_env, mock_launch):
        """Test error when purpose/background missing for new child session with agent tasks."""
        tasks = [{"type": "agent", "instruction": "test"}]
        result = invoke_serial_children(tasks=tasks, child_session_id=None)

        assert result.is_success is False
        assert "both 'purpose' and 'background' are required" in result.error

    def test_empty_tasks(self, mock_env, mock_launch):
        """Test error when tasks list is empty."""
        result = invoke_serial_children(tasks=[])

        assert result.is_success is False
        assert "At least one task is required" in result.error

    def test_task_missing_type(self, mock_env, mock_launch):
        """Test error when task missing 'type' field."""
        result = invoke_serial_children(tasks=[{"command": "echo hello"}])

        assert result.is_success is False
        assert "Task must have 'type' field" in result.error

    def test_invalid_task_type(self, mock_env, mock_launch):
        """Test error when task type is invalid."""
        result = invoke_serial_children(tasks=[{"type": "invalid"}])

        assert result.is_success is False
        assert "Invalid task type" in result.error

    def test_successful_launch_agent_injection(self, mock_env, mock_launch):
        """Test successful launch with agent task and parameter injection."""
        tasks = [{"type": "agent", "instruction": "test"}]
        roles = "role1, role2"
        references = "ref1, ref2"
        references_persist = '["persist1", "persist2"]'
        artifacts = "art1"
        procedure = "proc1.md"

        result = invoke_serial_children(
            tasks=tasks,
            purpose="test purpose",
            background="test background",
            roles=roles,
            references=references,
            references_persist=references_persist,
            artifacts=artifacts,
            procedure=procedure,
        )

        assert result.is_success is True
        assert result.data == {"status": "launched"}

        mock_launch.assert_called_once()
        _, kwargs = mock_launch.call_args

        # Verify injected tasks
        processed_tasks = kwargs["tasks"]
        assert len(processed_tasks) == 1
        agent_task = processed_tasks[0]
        assert agent_task["roles"] == ["role1", "role2"]
        assert agent_task["references"] == ["ref1", "ref2"]
        assert agent_task["references_persist"] == ["persist1", "persist2"]
        assert agent_task["artifacts"] == ["art1"]
        assert agent_task["procedure"] == "proc1.md"

        # Verify other parameters
        assert kwargs["manager_type"] == "serial"
        assert kwargs["parent_session_id"] == "parent-session-123"
        assert kwargs["purpose"] == "test purpose"
        assert kwargs["background"] == "test background"

    def test_successful_launch_script(self, mock_env, mock_launch):
        """Test successful launch with script task (no injection)."""
        tasks = [{"type": "script", "command": "echo hello"}]

        result = invoke_serial_children(
            tasks=tasks,
            roles="role1",
        )

        assert result.is_success is True
        mock_launch.assert_called_once()
        processed_tasks = mock_launch.call_args.kwargs["tasks"]
        assert processed_tasks[0] == tasks[0]  # No injection for script tasks

    def test_task_as_json_string(self, mock_env, mock_launch):
        """Test tasks passed as JSON strings."""
        task_dict = {"type": "script", "command": "echo hello"}
        tasks = [json.dumps(task_dict)]

        result = invoke_serial_children(tasks=tasks)

        assert result.is_success is True
        mock_launch.assert_called_once()
        processed_tasks = mock_launch.call_args.kwargs["tasks"]
        assert processed_tasks[0] == task_dict

    def test_child_session_id_provided(self, mock_env, mock_launch):
        """Test when child_session_id is provided (purpose/background not required)."""
        tasks = [{"type": "agent", "instruction": "test"}]
        result = invoke_serial_children(tasks=tasks, child_session_id="child-123")

        assert result.is_success is True
        assert mock_launch.call_args.kwargs["child_session_id"] == "child-123"

    def test_normalize_list_json_failure(self, mock_env, mock_launch):
        """Test normalize_list fallback when JSON parsing fails."""
        # "[invalid" is a string starting with [ but not valid JSON
        # It should fallback to split(",")
        result = invoke_serial_children(
            tasks=[{"type": "agent", "instruction": "test"}],
            purpose="p",
            background="b",
            roles="[invalid, role2",
        )

        assert result.is_success is True
        processed_tasks = mock_launch.call_args.kwargs["tasks"]
        # "[invalid, role2" -> ["[invalid", "role2"]
        assert processed_tasks[0]["roles"] == ["[invalid", "role2"]
