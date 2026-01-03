"""
Unit tests for Serial Task Manager Service.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest
from pipe.core.models.task import (
    AgentTask,
    ScriptTask,
    TaskExecutionResult,
)
from pipe.core.services.serial_manager_service import (
    execute_tasks_serially,
    invoke_parent_session,
    load_task_metadata,
    main,
    save_pipeline_result,
)


class TestLoadTaskMetadata:
    """Tests for load_task_metadata function."""

    @patch("pipe.core.services.serial_manager_service.read_json_file")
    @patch("pipe.core.services.serial_manager_service.Path")
    def test_load_task_metadata_success(self, mock_path, mock_read_json):
        """Test successful loading of task metadata."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.__truediv__.return_value = mock_path_instance
        mock_path_instance.__str__.return_value = "/fake/path/tasks.json"  # type: ignore[attr-defined]

        mock_read_json.return_value = {
            "child_session_id": "child-123",
            "purpose": "test purpose",
            "background": "test background",
            "tasks": [
                {"type": "agent", "instruction": "task 1"},
                {"type": "script", "script": "ls", "max_retries": 2},
            ],
        }

        tasks, child_id, purpose, background = load_task_metadata(
            "parent-123", "/fake/root"
        )

        assert len(tasks) == 2
        assert isinstance(tasks[0], AgentTask)
        assert isinstance(tasks[1], ScriptTask)
        assert tasks[0].instruction == "task 1"
        assert tasks[1].script == "ls"
        assert child_id == "child-123"
        assert purpose == "test purpose"
        assert background == "test background"

    @patch("pipe.core.services.serial_manager_service.read_json_file")
    def test_load_task_metadata_unknown_type(self, mock_read_json):
        """Test loading task metadata with unknown task type."""
        mock_read_json.return_value = {
            "tasks": [{"type": "unknown"}],
        }

        with pytest.raises(ValueError, match="Unknown task type: unknown"):
            load_task_metadata("parent-123", "/fake/root")

    @patch("pipe.core.services.serial_manager_service.read_json_file")
    def test_load_task_metadata_file_not_found(self, mock_read_json):
        """Test loading task metadata when file is not found."""
        mock_read_json.side_effect = FileNotFoundError("File not found")
        with pytest.raises(FileNotFoundError):
            load_task_metadata("parent-123", "/fake/root")


class TestExecuteTasksSerially:
    """Tests for execute_tasks_serially function."""

    @pytest.fixture
    def tasks(self):
        """Create a list of tasks for testing."""
        return [
            AgentTask(type="agent", instruction="task 1"),
            ScriptTask(type="script", script="ls", max_retries=1),
        ]

    @patch("pipe.core.services.serial_manager_service.execute_script_task")
    @patch("pipe.core.services.serial_manager_service.execute_agent_task")
    def test_execute_tasks_serially_success(
        self, mock_execute_agent, mock_execute_script, tasks
    ):
        """Test successful serial execution of tasks."""
        mock_execute_agent.return_value = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=0,
            output_preview="[CREATED_SESSION:abc/123]",
            duration_seconds=1.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:01Z",
        )
        mock_execute_script.return_value = TaskExecutionResult(
            task_index=1,
            task_type="script",
            exit_code=0,
            output_preview="success",
            duration_seconds=0.5,
            started_at="2025-01-01T00:00:01Z",
            completed_at="2025-01-01T00:00:01.5Z",
        )

        results = execute_tasks_serially(
            tasks, None, "parent-123", "/fake/root", "purpose", "background"
        )

        assert len(results) == 2
        assert results[0].exit_code == 0
        assert results[1].exit_code == 0
        assert mock_execute_agent.call_count == 1
        assert mock_execute_script.call_count == 1

    @patch("pipe.core.services.serial_manager_service.execute_agent_task")
    def test_execute_tasks_serially_short_circuit(self, mock_execute_agent, tasks):
        """Test short-circuit behavior on task failure."""
        mock_execute_agent.return_value = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=1,
            output_preview="failed",
            duration_seconds=1.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:01Z",
        )

        results = execute_tasks_serially(
            tasks, None, "parent-123", "/fake/root", "purpose", "background"
        )

        assert len(results) == 1
        assert results[0].exit_code == 1
        # Second task (script) should not be executed
        assert mock_execute_agent.call_count == 1

    @patch("pipe.core.services.serial_manager_service.execute_script_task")
    @patch("pipe.core.services.serial_manager_service.execute_agent_task")
    def test_execute_tasks_serially_retry_logic(
        self, mock_execute_agent, mock_execute_script, tasks
    ):
        """Test retry logic for script tasks."""
        # First agent task succeeds
        agent_result = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=0,
            output_preview="[CREATED_SESSION:abc/123]",
            duration_seconds=1.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:01Z",
        )
        # Script task fails first, then succeeds on retry
        script_fail = TaskExecutionResult(
            task_index=1,
            task_type="script",
            exit_code=1,
            output_preview="error",
            duration_seconds=0.5,
            started_at="2025-01-01T00:00:01Z",
            completed_at="2025-01-01T00:00:01.5Z",
        )
        script_success = TaskExecutionResult(
            task_index=1,
            task_type="script",
            exit_code=0,
            output_preview="success",
            duration_seconds=0.5,
            started_at="2025-01-01T00:00:02Z",
            completed_at="2025-01-01T00:00:02.5Z",
        )

        mock_execute_agent.side_effect = [agent_result, agent_result]
        mock_execute_script.side_effect = [script_fail, script_success]

        results = execute_tasks_serially(
            tasks, None, "parent-123", "/fake/root", "purpose", "background"
        )

        assert len(results) == 2
        assert results[1].exit_code == 0
        # Agent executed twice (initial + retry)
        assert mock_execute_agent.call_count == 2
        # Script executed twice (initial + retry)
        assert mock_execute_script.call_count == 2

    @patch("pipe.core.services.serial_manager_service.execute_script_task")
    @patch("pipe.core.services.serial_manager_service.execute_agent_task")
    def test_execute_tasks_serially_abort_on_exit_2(
        self, mock_execute_agent, mock_execute_script, tasks
    ):
        """Test that exit code 2 causes immediate abort without retries."""
        mock_execute_agent.return_value = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=0,
            output_preview="[CREATED_SESSION:abc/123]",
            duration_seconds=1.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:01Z",
        )
        mock_execute_script.return_value = TaskExecutionResult(
            task_index=1,
            task_type="script",
            exit_code=2,
            output_preview="permanent failure",
            duration_seconds=0.5,
            started_at="2025-01-01T00:00:01Z",
            completed_at="2025-01-01T00:00:01.5Z",
        )

        results = execute_tasks_serially(
            tasks, None, "parent-123", "/fake/root", "purpose", "background"
        )

        assert len(results) == 2
        assert results[1].exit_code == 2
        # Script executed only once despite max_retries=1
        assert mock_execute_script.call_count == 1

    @patch("pipe.core.services.serial_manager_service.execute_script_task")
    def test_execute_tasks_serially_script_retry_no_agent(self, mock_execute_script):
        """Test script retry when no preceding agent task exists."""
        tasks = [ScriptTask(type="script", script="ls", max_retries=1)]
        mock_execute_script.side_effect = [
            TaskExecutionResult(
                task_index=0,
                task_type="script",
                exit_code=1,
                output_preview="error",
                duration_seconds=0.5,
                started_at="2025-01-01T00:00:00Z",
                completed_at="2025-01-01T00:00:00.5Z",
            ),
            TaskExecutionResult(
                task_index=0,
                task_type="script",
                exit_code=0,
                output_preview="success",
                duration_seconds=0.5,
                started_at="2025-01-01T00:00:01Z",
                completed_at="2025-01-01T00:00:01.5Z",
            ),
        ]

        results = execute_tasks_serially(
            tasks, None, "parent-123", "/fake/root", "purpose", "background"
        )

        assert len(results) == 1
        assert results[0].exit_code == 0
        assert mock_execute_script.call_count == 2

    @patch("pipe.core.services.serial_manager_service.execute_script_task")
    @patch("pipe.core.services.serial_manager_service.execute_agent_task")
    def test_execute_tasks_serially_agent_retry_failure(
        self, mock_execute_agent, mock_execute_script
    ):
        """Test script retry when agent re-execution fails."""
        tasks = [
            AgentTask(type="agent", instruction="task 1"),
            ScriptTask(type="script", script="ls", max_retries=1),
        ]
        # Initial agent success
        agent_success = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=0,
            output_preview="[CREATED_SESSION:abc/123]",
            duration_seconds=1.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:01Z",
        )
        # Script failure
        script_fail = TaskExecutionResult(
            task_index=1,
            task_type="script",
            exit_code=1,
            output_preview="error",
            duration_seconds=0.5,
            started_at="2025-01-01T00:00:01Z",
            completed_at="2025-01-01T00:00:01.5Z",
        )
        # Agent retry failure
        agent_fail = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=1,
            output_preview="retry failed",
            duration_seconds=1.0,
            started_at="2025-01-01T00:00:02Z",
            completed_at="2025-01-01T00:00:03Z",
        )

        mock_execute_agent.side_effect = [agent_success, agent_fail]
        mock_execute_script.return_value = script_fail

        results = execute_tasks_serially(
            tasks, None, "parent-123", "/fake/root", "purpose", "background"
        )

        assert len(results) == 2
        assert results[1].exit_code == 1
        assert mock_execute_agent.call_count == 2
        assert mock_execute_script.call_count == 1

    @patch("pipe.core.services.serial_manager_service.execute_agent_task")
    def test_execute_tasks_serially_agent_no_output_match(self, mock_execute_agent):
        """Test execute_tasks_serially when agent output doesn't match regex but child_session_id is provided."""
        tasks = [AgentTask(type="agent", instruction="task 1")]
        mock_execute_agent.return_value = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=0,
            output_preview="no match",
            duration_seconds=1.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:01Z",
        )
        # This should hit line 147 if child_session_id is provided
        results = execute_tasks_serially(
            tasks, "child-123", "parent-123", "/fake/root", None, None
        )
        assert len(results) == 1
        assert mock_execute_agent.call_count == 1

    def test_execute_tasks_serially_unknown_type(self):
        """Test execute_tasks_serially with unknown task type."""
        mock_task = MagicMock()
        mock_task.type = "unknown"
        with pytest.raises(ValueError, match="Unknown task type: unknown"):
            execute_tasks_serially(
                [mock_task], None, "parent-123", "/fake/root", None, None
            )


class TestSavePipelineResult:
    """Tests for save_pipeline_result function."""

    @patch("pipe.core.services.serial_manager_service.open", new_callable=mock_open)
    @patch("pipe.core.services.serial_manager_service.create_directory")
    @patch("pipe.core.services.serial_manager_service.get_current_timestamp")
    @patch("pipe.core.services.serial_manager_service.Path")
    def test_save_pipeline_result(
        self, mock_path, mock_timestamp, mock_create_dir, mock_file
    ):
        """Test saving pipeline results to file."""
        import json

        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.__truediv__.return_value = mock_path_instance
        mock_path_instance.__str__.return_value = (  # type: ignore[attr-defined]
            "/fake/root/.pipe_sessions/session-123_serial_result.json"
        )

        mock_timestamp.return_value = "2025-01-01T00:00:00+09:00"

        results = [
            TaskExecutionResult(
                task_index=0,
                task_type="agent",
                exit_code=0,
                output_preview="[CREATED_SESSION:abc/123]",
                duration_seconds=1.0,
                started_at="2025-01-01T00:00:00Z",
                completed_at="2025-01-01T00:00:01Z",
            )
        ]

        child_ids = save_pipeline_result("session-123", results, "/fake/root")

        # Verify return value
        assert child_ids == ["abc/123"]
        mock_create_dir.assert_called_once()
        mock_file.assert_called_once()

        # Verify file content written by json.dump()
        handle = mock_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        data = json.loads(written_content)

        assert data["status"] == "success"
        assert data["child_session_ids"] == ["abc/123"]
        assert data["total_tasks"] == 1
        assert data["completed_tasks"] == 1
        assert data["timestamp"] == "2025-01-01T00:00:00+09:00"

    @patch("pipe.core.services.serial_manager_service.open", new_callable=mock_open)
    @patch("pipe.core.services.serial_manager_service.create_directory")
    @patch("pipe.core.services.serial_manager_service.get_current_timestamp")
    @patch("pipe.core.services.serial_manager_service.Path")
    def test_save_pipeline_result_no_match(
        self, mock_path, mock_timestamp, mock_create_dir, mock_file
    ):
        """Test saving pipeline results when no session ID is found in output."""
        import json

        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.__truediv__.return_value = mock_path_instance
        mock_path_instance.__str__.return_value = "/fake/root/result.json"  # type: ignore[attr-defined]

        mock_timestamp.return_value = "2025-01-01T00:00:00+09:00"

        results = [
            TaskExecutionResult(
                task_index=0,
                task_type="agent",
                exit_code=0,
                output_preview="no session id here",
                duration_seconds=1.0,
                started_at="2025-01-01T00:00:00Z",
                completed_at="2025-01-01T00:00:01Z",
            )
        ]

        child_ids = save_pipeline_result("session-123", results, "/fake/root")

        # Verify return value
        assert child_ids == []

        # Verify file content
        handle = mock_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        data = json.loads(written_content)

        assert data["status"] == "success"
        assert data["child_session_ids"] == []


class TestInvokeParentSession:
    """Tests for invoke_parent_session function."""

    @patch("pipe.core.services.serial_manager_service.subprocess.run")
    def test_invoke_parent_session_success(self, mock_run):
        """Test invoking parent session on success."""
        invoke_parent_session("parent-123", ["abc/123"], "/fake/root")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "parent-123" in args
        assert "✅" in args[args.index("--instruction") + 1]

    @patch("pipe.core.services.serial_manager_service.subprocess.run")
    def test_invoke_parent_session_failure(self, mock_run):
        """Test invoking parent session on failure."""
        results = [
            TaskExecutionResult(
                task_index=0,
                task_type="script",
                exit_code=1,
                output_preview="error",
                duration_seconds=0.5,
                started_at="2025-01-01T00:00:00Z",
                completed_at="2025-01-01T00:00:00.5Z",
            )
        ]
        invoke_parent_session("parent-123", [], "/fake/root", results=results)

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "❌" in args[args.index("--instruction") + 1]

    @patch("pipe.core.services.serial_manager_service.subprocess.run")
    def test_invoke_parent_session_abort(self, mock_run):
        """Test invoking parent session on abort (exit code 2)."""
        results = [
            TaskExecutionResult(
                task_index=0,
                task_type="script",
                exit_code=2,
                output_preview="permanent failure",
                duration_seconds=0.5,
                started_at="2025-01-01T00:00:00Z",
                completed_at="2025-01-01T00:00:00.5Z",
            )
        ]
        invoke_parent_session("parent-123", [], "/fake/root", results=results)

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "🚨" in args[args.index("--instruction") + 1]

    @patch("pipe.core.services.serial_manager_service.subprocess.run")
    def test_invoke_parent_session_no_children(self, mock_run):
        """Test invoking parent session when no child sessions were created."""
        invoke_parent_session("parent-123", [], "/fake/root", results=[])

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "No child sessions were created" in args[args.index("--instruction") + 1]


class TestMain:
    """Tests for main function."""

    @patch(
        "pipe.core.services.serial_manager_service.argparse.ArgumentParser.parse_args"
    )
    @patch("pipe.core.services.serial_manager_service.get_project_root")
    @patch("pipe.core.services.serial_manager_service.load_task_metadata")
    @patch("pipe.core.services.serial_manager_service.execute_tasks_serially")
    @patch("pipe.core.services.serial_manager_service.save_pipeline_result")
    @patch("pipe.core.services.serial_manager_service.invoke_parent_session")
    @patch("sys.exit")
    def test_main_success(
        self,
        mock_exit,
        mock_invoke,
        mock_save,
        mock_execute,
        mock_load,
        mock_get_root,
        mock_parse_args,
    ):
        """Test main function success path."""
        mock_parse_args.return_value = MagicMock(parent_session="parent-123")
        mock_get_root.return_value = "/root"
        mock_load.return_value = ([], "child-456", "purpose", "background")
        mock_execute.return_value = []
        mock_save.return_value = []

        main()

        mock_load.assert_called_once_with("parent-123", "/root")
        mock_execute.assert_called_once()
        mock_save.assert_called_once()
        mock_invoke.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch(
        "pipe.core.services.serial_manager_service.argparse.ArgumentParser.parse_args"
    )
    @patch("pipe.core.services.serial_manager_service.load_task_metadata")
    @patch("sys.exit")
    def test_main_exception(self, mock_exit, mock_load, mock_parse_args):
        """Test main function exception handling."""
        mock_parse_args.return_value = MagicMock(parent_session="parent-123")
        mock_load.side_effect = Exception("Fatal error")

        main()

        mock_exit.assert_called_once_with(1)

    @patch(
        "pipe.core.services.serial_manager_service.argparse.ArgumentParser.parse_args"
    )
    @patch("pipe.core.services.serial_manager_service.get_project_root")
    @patch("pipe.core.services.serial_manager_service.load_task_metadata")
    @patch("pipe.core.services.serial_manager_service.execute_tasks_serially")
    @patch("pipe.core.services.serial_manager_service.save_pipeline_result")
    @patch("pipe.core.services.serial_manager_service.invoke_parent_session")
    @patch("sys.exit")
    def test_main_with_child_id(
        self,
        mock_exit,
        mock_invoke,
        mock_save,
        mock_execute,
        mock_load,
        mock_get_root,
        mock_parse_args,
    ):
        """Test main function when child_session_id is provided."""
        mock_parse_args.return_value = MagicMock(parent_session="parent-123")
        mock_get_root.return_value = "/root"
        mock_load.return_value = ([], "child-456", "purpose", "background")
        mock_execute.return_value = []
        mock_save.return_value = []

        main()

        mock_load.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch(
        "pipe.core.services.serial_manager_service.argparse.ArgumentParser.parse_args"
    )
    @patch("pipe.core.services.serial_manager_service.get_project_root")
    @patch("pipe.core.services.serial_manager_service.load_task_metadata")
    @patch("pipe.core.services.serial_manager_service.execute_tasks_serially")
    @patch("pipe.core.services.serial_manager_service.save_pipeline_result")
    @patch("pipe.core.services.serial_manager_service.invoke_parent_session")
    @patch("sys.exit")
    def test_main_failure(
        self,
        mock_exit,
        mock_invoke,
        mock_save,
        mock_execute,
        mock_load,
        mock_get_root,
        mock_parse_args,
    ):
        """Test main function failure path."""
        mock_parse_args.return_value = MagicMock(parent_session="parent-123")
        mock_get_root.return_value = "/root"
        mock_load.return_value = ([], None, "purpose", "background")
        mock_execute.return_value = [
            TaskExecutionResult(
                task_index=0,
                task_type="agent",
                exit_code=1,
                output_preview="failed",
                duration_seconds=1.0,
                started_at="2025-01-01T00:00:00Z",
                completed_at="2025-01-01T00:00:01Z",
            )
        ]
        mock_save.return_value = []

        main()

        mock_exit.assert_called_once_with(1)
