import pytest
from pipe.core.models.task import (
    AgentTask,
    PipelineResult,
    ScriptTask,
    TaskExecutionResult,
)
from pydantic import ValidationError


class TestTaskModels:
    """Tests for task execution models."""

    def test_agent_task_creation(self):
        """Test creating a valid AgentTask."""
        task = AgentTask(instruction="Run analysis")
        assert task.type == "agent"
        assert task.instruction == "Run analysis"

    def test_script_task_creation(self):
        """Test creating a valid ScriptTask with default arguments."""
        task = ScriptTask(script="analyze.sh")
        assert task.type == "script"
        assert task.script == "analyze.sh"
        assert task.args == []

    def test_script_task_with_args(self):
        """Test creating a ScriptTask with arguments."""
        task = ScriptTask(script="test.py", args=["--verbose", "debug"])
        assert task.args == ["--verbose", "debug"]

    def test_task_execution_result_creation(self):
        """Test creating a valid TaskExecutionResult."""
        result = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:10Z",
            duration_seconds=10.0,
            output_preview="Success",
        )
        assert result.task_index == 0
        assert result.exit_code == 0
        assert result.output_preview == "Success"

    def test_pipeline_result_creation(self):
        """Test creating a valid PipelineResult."""
        task_result = TaskExecutionResult(
            task_index=0,
            task_type="agent",
            exit_code=0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:10Z",
            duration_seconds=10.0,
        )
        pipeline_result = PipelineResult(
            status="success",
            total_tasks=1,
            completed_tasks=1,
            child_session_ids=["child-123"],
            results=[task_result],
            timestamp="2025-01-01T00:00:11Z",
        )
        assert pipeline_result.status == "success"
        assert len(pipeline_result.results) == 1
        assert pipeline_result.child_session_ids == ["child-123"]

    def test_pipeline_result_validation_error(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            PipelineResult(status="success")

    def test_model_serialization_by_alias(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        result = TaskExecutionResult(
            task_index=1,
            task_type="script",
            exit_code=1,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:05Z",
            duration_seconds=5.0,
        )
        dumped = result.model_dump(by_alias=True)
        # Should use camelCase aliases
        assert "taskIndex" in dumped
        assert "taskType" in dumped
        assert "exitCode" in dumped
        assert "startedAt" in dumped
        assert "completedAt" in dumped
        assert "durationSeconds" in dumped

        assert dumped["taskIndex"] == 1
        assert dumped["taskType"] == "script"

    def test_pipeline_result_serialization_by_alias(self):
        """Test PipelineResult serialization with camelCase aliases."""
        pipeline_result = PipelineResult(
            status="failed",
            total_tasks=2,
            completed_tasks=1,
            child_session_ids=["child-1"],
            results=[],
            timestamp="2025-01-01T00:00:20Z",
        )
        dumped = pipeline_result.model_dump(by_alias=True)
        assert "totalTasks" in dumped
        assert "completedTasks" in dumped
        assert "childSessionIds" in dumped
        assert dumped["totalTasks"] == 2
        assert dumped["childSessionIds"] == ["child-1"]

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = PipelineResult(
            status="failed",
            total_tasks=2,
            completed_tasks=1,
            child_session_ids=[],
            results=[
                TaskExecutionResult(
                    task_index=0,
                    task_type="agent",
                    exit_code=0,
                    started_at="2025-01-01T00:00:00Z",
                    completed_at="2025-01-01T00:00:10Z",
                    duration_seconds=10.0,
                )
            ],
            timestamp="2025-01-01T00:00:20Z",
        )

        # Serialize to JSON (with camelCase)
        json_str = original.model_dump_json(by_alias=True)
        assert "totalTasks" in json_str

        # Deserialize back
        restored = PipelineResult.model_validate_json(json_str)

        assert restored.status == original.status
        assert restored.total_tasks == original.total_tasks
        assert len(restored.results) == 1
        assert restored.results[0].task_index == 0
