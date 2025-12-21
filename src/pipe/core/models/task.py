"""Task execution models for serial/parallel execution."""

from typing import Literal

from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    """Agent execution task"""

    type: Literal["agent"] = "agent"
    instruction: str = Field(..., description="Instruction for the agent")


class ScriptTask(BaseModel):
    """Script execution task"""

    type: Literal["script"] = "script"
    script: str = Field(..., description="Script name (under scripts/ directory)")
    args: list[str] = Field(default_factory=list, description="Script arguments")


# Unified task type
Task = AgentTask | ScriptTask


class TaskExecutionResult(BaseModel):
    """Task execution result"""

    task_index: int = Field(..., description="Task index (0-based)")
    task_type: Literal["agent", "script"] = Field(..., description="Task type")
    exit_code: int = Field(..., description="Exit code (0=success)")
    started_at: str = Field(..., description="Start time (ISO 8601)")
    completed_at: str = Field(..., description="Completion time (ISO 8601)")
    duration_seconds: float = Field(..., description="Execution duration (seconds)")
    output_preview: str | None = Field(
        None, description="First 500 characters of output (optional)"
    )


class PipelineResult(BaseModel):
    """Overall pipeline execution result"""

    status: Literal["success", "failed"] = Field(..., description="Overall status")
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    child_session_ids: list[str] = Field(
        default_factory=list, description="Child session IDs created during execution"
    )
    results: list[TaskExecutionResult] = Field(
        default_factory=list, description="Individual task results"
    )
    timestamp: str = Field(..., description="Result save timestamp (ISO 8601)")
