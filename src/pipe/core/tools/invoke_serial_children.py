"""Tool for invoking serial task execution.

Environment: Poetry-managed Python project
"""

import json
import os

from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.task_launcher import launch_manager


def invoke_serial_children(
    tasks: list[dict | str],
    child_session_id: str | None = None,
    purpose: str | None = None,
    background: str | None = None,
    roles: list[str] | str | None = None,
    procedure: str | None = None,
    references: list[str] | str | None = None,
    references_persist: list[str] | str | None = None,
    artifacts: list[str] | str | None = None,
) -> ToolResult:
    """
    Execute multiple tasks serially in child agent sessions and exit parent process.
    """
    # Get parent session ID from environment variable
    parent_session_id = os.getenv("PIPE_SESSION_ID")

    if not parent_session_id:
        raise ValueError(
            "Parent session ID not found. Please ensure PIPE_SESSION_ID environment "
            "variable is set."
        )

    # Normalize tasks: convert string tasks to dict if necessary
    normalized_tasks: list[dict] = []
    for task in tasks:
        if isinstance(task, str):
            try:
                normalized_tasks.append(json.loads(task))
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse task as JSON: {task}")
        else:
            normalized_tasks.append(task)

    # Normalize list arguments that might be passed as strings
    def normalize_list(val: list[str] | str | None) -> list[str] | None:
        if isinstance(val, str):
            if val.startswith("[") and val.endswith("]"):
                try:
                    return json.loads(val)
                except json.JSONDecodeError:
                    pass
            return [v.strip() for v in val.split(",") if v.strip()]
        return val

    roles_list = normalize_list(roles)
    references_list = normalize_list(references)
    references_persist_list = normalize_list(references_persist)
    artifacts_list = normalize_list(artifacts)

    # Validate new session parameters if creating new child sessions
    if child_session_id is None:
        # Check if any agent tasks exist
        has_agent_tasks = any(task.get("type") == "agent" for task in normalized_tasks)
        if has_agent_tasks and (not purpose or not background):
            raise ValueError(
                "When child_session_id is not provided and agent tasks exist, "
                "both 'purpose' and 'background' are required for creating "
                "new child sessions."
            )

    # Validate task definitions
    if not normalized_tasks:
        raise ValueError("At least one task is required")

    # Inject roles, procedure, references, artifacts into agent tasks if not already set
    processed_tasks = []
    for task in normalized_tasks:
        if "type" not in task:
            raise ValueError("Task must have 'type' field")
        if task["type"] not in ("agent", "script"):
            raise ValueError(f"Invalid task type: {task['type']}")

        # For agent tasks, inject parameters if not already present
        if task["type"] == "agent":
            task_copy = task.copy()
            if "roles" not in task_copy and roles_list:
                task_copy["roles"] = roles_list
            if "procedure" not in task_copy and procedure:
                task_copy["procedure"] = procedure
            if "references" not in task_copy and references_list:
                task_copy["references"] = references_list
            if "references_persist" not in task_copy and references_persist_list:
                task_copy["references_persist"] = references_persist_list
            if "artifacts" not in task_copy and artifacts_list:
                task_copy["artifacts"] = artifacts_list
            processed_tasks.append(task_copy)
        else:
            processed_tasks.append(task)


    # Launch manager and exit parent process
    # Pass both parent and child session info, plus session creation parameters
    launch_manager(
        manager_type="serial",
        tasks=processed_tasks,
        parent_session_id=parent_session_id,
        child_session_id=child_session_id,
        purpose=purpose,
        background=background,
    )

    # Never reaches here (launch_manager calls sys.exit)
    return ToolResult(data={"status": "launched"})
