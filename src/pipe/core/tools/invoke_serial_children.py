"""Tool for invoking serial task execution.

Environment: Poetry-managed Python project
"""

import os

from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.task_launcher import launch_manager


def invoke_serial_children(
    tasks: list[dict],
    child_session_id: str | None = None,
    purpose: str | None = None,
    background: str | None = None,
) -> ToolResult:
    """
    Execute multiple tasks serially in child agent sessions and exit parent process.

    Args:
        tasks: List of task definitions
            Example for agent tasks: [
                {"type": "agent", "instruction": "Implement feature"},
                {"type": "agent", "instruction": "Run tests"}
            ]
            Example for script tasks: [
                {"type": "script", "script": "lint_with_retry.sh", "args": ["3"]}
            ]
        child_session_id: Child session ID (optional)
            - If provided: Use existing child session for agent tasks
            - If None: Create new child session for each agent task
        purpose: Purpose for new child sessions
            (required if child_session_id is None)
        background: Background for new child sessions
            (required if child_session_id is None)

    Returns:
        ToolResult (actually never returns - process exits)

    Note:
        This function exits the parent process immediately.
        After all tasks complete, serial_manager_service will invoke
        the parent session, making result files available for review.

        For agent tasks:
        - If child_session_id is provided: All agent tasks use that session
        - If child_session_id is None: Each agent task creates a new session
          (requires purpose and background)

        For script tasks:
        - Scripts run in the parent session context (via PIPE_SESSION_ID env var)

    Example with new child sessions:
        >>> invoke_serial_children(
        ...     tasks=[
        ...         {"type": "agent", "instruction": "Add function to main.py"},
        ...         {"type": "agent", "instruction": "Run tests"}
        ...     ],
        ...     purpose="Feature implementation",
        ...     background="Adding new feature"
        ... )

    Example with existing child session:
        >>> invoke_serial_children(
        ...     tasks=[
        ...         {"type": "agent", "instruction": "Fix bug in auth"},
        ...     ],
        ...     child_session_id="abc123"
        ... )
    """
    # Get parent session ID from environment variable
    parent_session_id = os.getenv("PIPE_SESSION_ID")

    if not parent_session_id:
        raise ValueError(
            "Parent session ID not found. Please ensure PIPE_SESSION_ID environment "
            "variable is set."
        )

    # Validate new session parameters if creating new child sessions
    if child_session_id is None:
        # Check if any agent tasks exist
        has_agent_tasks = any(task.get("type") == "agent" for task in tasks)
        if has_agent_tasks and (not purpose or not background):
            raise ValueError(
                "When child_session_id is not provided and agent tasks exist, "
                "both 'purpose' and 'background' are required for creating "
                "new child sessions."
            )

    # Validate task definitions
    if not tasks:
        raise ValueError("At least one task is required")

    for task in tasks:
        if "type" not in task:
            raise ValueError("Task must have 'type' field")
        if task["type"] not in ("agent", "script"):
            raise ValueError(f"Invalid task type: {task['type']}")

    # Launch manager and exit parent process
    # Pass both parent and child session info, plus session creation parameters
    launch_manager(
        manager_type="serial",
        tasks=tasks,
        parent_session_id=parent_session_id,
        child_session_id=child_session_id,
        purpose=purpose,
        background=background,
    )

    # Never reaches here (launch_manager calls sys.exit)
    return ToolResult(data={"status": "launched"})
