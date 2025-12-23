"""Common task execution logic for serial/parallel managers.

Environment: Poetry-managed Python project
"""

import os
import subprocess
import time

from pipe.core.models.task import AgentTask, ScriptTask, TaskExecutionResult
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.script_validator import validate_script_path


def execute_agent_task(
    task: AgentTask,
    session_id: str | None,
    project_root: str,
    parent_session_id: str | None = None,
    purpose: str | None = None,
    background: str | None = None,
) -> TaskExecutionResult:
    """
    Execute agent task (common logic)

    Args:
        task: Agent task definition
        session_id: Session ID (if None, creates new session)
        project_root: Project root path
        parent_session_id: Parent session ID (for new child sessions)
        purpose: Purpose for new session (required if session_id is None)
        background: Background for new session (required if session_id is None)

    Returns:
        Execution result
    """
    start_time = time.time()
    started_at = get_current_timestamp()

    # Build takt command
    cmd = ["poetry", "run", "takt"]

    if session_id:
        # Use existing session
        cmd.extend(["--session", session_id, "--instruction", task.instruction])
    else:
        # Create new session
        if not purpose or not background:
            raise ValueError(
                "purpose and background are required when creating new session"
            )
        cmd.extend(
            [
                "--purpose",
                purpose,
                "--background",
                background,
            ]
        )
        # Add parent option if specified
        if parent_session_id:
            cmd.extend(["--parent", parent_session_id])

        # Add optional takt parameters
        if task.roles:
            for role in task.roles:
                cmd.extend(["--roles", role])

        if task.procedure:
            cmd.extend(["--procedure", task.procedure])

        if task.references:
            for ref in task.references:
                cmd.extend(["--references", ref])

        if task.references_persist:
            for ref in task.references_persist:
                cmd.extend(["--references-persist", ref])

        if task.artifacts:
            for artifact in task.artifacts:
                cmd.extend(["--artifacts", artifact])

        # Instruction comes last
        cmd.extend(["--instruction", task.instruction])

    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

    completed_at = get_current_timestamp()
    duration = time.time() - start_time

    # Extract session_id from stdout for new sessions
    # The takt CLI outputs session info as JSON (last line of stdout)
    created_session_id = None
    if result.stdout and not session_id:
        import json

        # Try to parse the last line as JSON
        try:
            lines = result.stdout.strip().split("\n")
            # The JSON response is usually on the last line
            for line in reversed(lines):
                if line.strip().startswith("{"):
                    session_data = json.loads(line.strip())
                    if "session_id" in session_data:
                        created_session_id = session_data["session_id"]
                        break
        except (json.JSONDecodeError, KeyError, IndexError):
            # Fallback: try regex extraction
            import re

            session_id_match = re.search(
                r'"session_id":\s*"([a-f0-9]+)"', result.stdout
            )
            if session_id_match:
                created_session_id = session_id_match.group(1)

    # Log errors to streaming log if execution failed
    if result.returncode != 0 and parent_session_id:
        from pathlib import Path

        from pipe.core.repositories.streaming_repository import StreamingRepository

        streaming_logs_dir = str(Path(project_root) / "sessions" / "streaming")
        streaming_repo = StreamingRepository(streaming_logs_dir)

        error_log = (
            f"[task_executor] Agent task failed with exit code {result.returncode}\n"
        )
        if result.stderr:
            error_log += f"[task_executor] STDERR:\n{result.stderr}\n"
        if result.stdout:
            error_log += f"[task_executor] STDOUT:\n{result.stdout}\n"
        if created_session_id:
            error_log += f"[task_executor] Created session: {created_session_id}\n"

        streaming_repo.append(parent_session_id, error_log)

    # Include created session ID in output preview if available
    output_preview = result.stdout[:500] if result.stdout else None
    if created_session_id:
        # Always include session ID marker if session was created
        preview_text = output_preview or ""
        output_preview = f"[CREATED_SESSION:{created_session_id}]\n{preview_text}"

    return TaskExecutionResult(
        task_index=-1,  # Set by caller
        task_type="agent",
        exit_code=result.returncode,
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=duration,
        output_preview=output_preview,
    )


def execute_script_task(
    task: ScriptTask, session_id: str, project_root: str
) -> TaskExecutionResult:
    """
    Execute script task (common logic)

    Args:
        task: Script task definition
        session_id: Session ID
        project_root: Project root path

    Returns:
        Execution result

    Note:
        Passes session info via environment variables:
        - PIPE_SESSION_ID
        - PIPE_PROJECT_ROOT

        Retry logic is handled at the serial manager level,
        not within this function.
    """
    start_time = time.time()
    started_at = get_current_timestamp()

    # Validate script path (security check)
    script_path = validate_script_path(task.script, project_root)

    # Set environment variables
    env = os.environ.copy()
    env["PIPE_SESSION_ID"] = session_id
    env["PIPE_PROJECT_ROOT"] = project_root

    # Execute script
    result = subprocess.run(
        [str(script_path)] + task.args,
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
    )

    completed_at = get_current_timestamp()
    duration = time.time() - start_time

    return TaskExecutionResult(
        task_index=-1,
        task_type="script",
        exit_code=result.returncode,
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=duration,
        output_preview=(result.stdout + result.stderr)[:500]
        if (result.stdout or result.stderr)
        else None,
    )
