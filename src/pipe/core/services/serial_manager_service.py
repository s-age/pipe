"""
Serial Task Manager Service

Executes tasks sequentially with immediate abort on failure (Short-Circuit).

Environment: Poetry-managed Python project
CLI Entry Point: poetry run python -m pipe.core.services.serial_manager_service
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

from pipe.core.models.task import (
    AgentTask,
    PipelineResult,
    ScriptTask,
    Task,
    TaskExecutionResult,
)
from pipe.core.services.task_executor_base import (
    execute_agent_task,
    execute_script_task,
)
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import create_directory, read_json_file
from pipe.core.utils.path import get_project_root

logger = logging.getLogger(__name__)


def load_task_metadata(
    parent_session_id: str, project_root: str
) -> tuple[list[Task], str | None, str | None, str | None]:
    """
    Load task metadata from file and parse into Pydantic models.

    Args:
        parent_session_id: Parent session ID
        project_root: Project root path

    Returns:
        Tuple of (tasks, child_session_id, purpose, background)

    Raises:
        FileNotFoundError: Task definition file not found
        ValueError: JSON parse error or unknown task type
    """
    tasks_file = (
        Path(project_root) / ".pipe_sessions" / f"{parent_session_id}_tasks.json"
    )

    # Use existing utility for JSON reading
    metadata = read_json_file(str(tasks_file))

    # Extract metadata
    child_session_id = metadata.get("child_session_id")
    purpose = metadata.get("purpose")
    background = metadata.get("background")
    tasks_data = metadata.get("tasks", [])

    # Parse into Pydantic models
    tasks: list[Task] = []
    for task_data in tasks_data:
        if task_data["type"] == "agent":
            tasks.append(AgentTask(**task_data))
        elif task_data["type"] == "script":
            tasks.append(ScriptTask(**task_data))
        else:
            raise ValueError(f"Unknown task type: {task_data.get('type')}")

    return tasks, child_session_id, purpose, background


def execute_tasks_serially(
    tasks: list[Task],
    child_session_id: str | None,
    parent_session_id: str,
    project_root: str,
    purpose: str | None,
    background: str | None,
) -> list[TaskExecutionResult]:
    """
    Execute tasks sequentially with Short-Circuit on failure.

    Args:
        tasks: List of tasks to execute
        child_session_id: Child session ID (None = create new sessions)
        parent_session_id: Parent session ID (for script tasks)
        project_root: Project root path
        purpose: Purpose for new child sessions
        background: Background for new child sessions

    Returns:
        List of execution results (aborted at first failure)

    Note:
        If any task fails (exit_code != 0), immediately returns
        including the failed task's result (Short-Circuit behavior).

        For script tasks with max_retries > 0, retry logic works as follows:
        1. Find the preceding agent task (backtrack through previous tasks)
        2. Re-execute the agent task with error information
        3. Re-execute the script task
        4. Repeat up to max_retries times

        SPECIAL HANDLING for exit_code 2:
        - exit_code 2 indicates a PERMANENT FAILURE (e.g., unauthorized file modifications)
        - Immediately aborts without retries, regardless of max_retries setting
        - This prevents wasted effort on issues that cannot be fixed through retries
    """
    results: list[TaskExecutionResult] = []
    # Track last created session ID for each agent task
    last_agent_session_id: str | None = None

    for i, task in enumerate(tasks):
        print(
            f"[serial_manager] ===== Task {i+1}/{len(tasks)}: {task.type} =====",
            flush=True,
        )

        # Execute based on task type
        if task.type == "agent":
            result = execute_agent_task(
                task,
                child_session_id,
                project_root,
                parent_session_id,
                purpose,
                background,
            )

            # Extract session ID from output for retry purposes
            if result.output_preview:
                import re

                match = re.search(
                    r"\[CREATED_SESSION:([a-f0-9/]+)\]", result.output_preview
                )
                if match:
                    last_agent_session_id = match.group(1)
                elif child_session_id:
                    # Using existing session
                    last_agent_session_id = child_session_id

        elif task.type == "script":
            # Execute script task with retry logic
            result = None
            max_attempts = task.max_retries + 1

            for attempt in range(max_attempts):
                if attempt > 0:
                    print(
                        f"[serial_manager] Retry attempt {attempt}/{task.max_retries} "
                        f"for script task {i+1}",
                        flush=True,
                    )

                    # Find the preceding agent task to re-execute
                    agent_task_index = None
                    for j in range(i - 1, -1, -1):
                        if tasks[j].type == "agent":
                            agent_task_index = j
                            break

                    if agent_task_index is None:
                        print(
                            "[serial_manager] WARNING: No preceding agent task found "
                            "for retry. Retrying script only.",
                            flush=True,
                        )
                    else:
                        # Re-execute the agent task with error information
                        agent_task = tasks[agent_task_index]
                        error_info = (
                            result.output_preview
                            if result and result.output_preview
                            else "Script validation failed"
                        )

                        # Create instruction with error context
                        retry_instruction = (
                            f"{agent_task.instruction}\n\n"
                            f"PREVIOUS ATTEMPT FAILED:\n"
                            f"Error output from validation script:\n"
                            f"```\n{error_info}\n```\n\n"
                            f"Please fix the issues and try again."
                        )

                        # Create a new agent task with error context
                        retry_agent_task = AgentTask(
                            type="agent", instruction=retry_instruction
                        )

                        print(
                            f"[serial_manager] Re-executing agent task "
                            f"{agent_task_index+1} with error context",
                            flush=True,
                        )

                        # Re-execute agent using session from previous execution
                        agent_result = execute_agent_task(
                            retry_agent_task,
                            last_agent_session_id,  # Continue existing session
                            project_root,
                            parent_session_id,
                            purpose,
                            background,
                        )

                        if agent_result.exit_code != 0:
                            print(
                                f"[serial_manager] Agent re-execution FAILED "
                                f"(exit code {agent_result.exit_code})",
                                flush=True,
                            )
                            # Don't save agent retry result, but abort retry loop
                            break

                        print(
                            "[serial_manager] Agent re-execution completed "
                            "successfully",
                            flush=True,
                        )

                # Execute (or re-execute) the script task
                result = execute_script_task(task, parent_session_id, project_root)

                # Success - stop retrying
                if result.exit_code == 0:
                    if attempt > 0:
                        print(
                            f"[serial_manager] Script succeeded on retry "
                            f"attempt {attempt}",
                            flush=True,
                        )
                    break

                # Exit code 2: ABORT - Permanent failure, do not retry
                if result.exit_code == 2:
                    print(
                        "[serial_manager] Script ABORTED with exit code 2 "
                        "(permanent failure, no retries)",
                        flush=True,
                    )
                    if result.output_preview:
                        print(
                            f"[serial_manager] Abort reason:\n{result.output_preview}",
                            flush=True,
                        )
                    break

                # Failure - log and continue to next attempt if retries remain
                if attempt < task.max_retries:
                    print(
                        f"[serial_manager] Script failed with exit code "
                        f"{result.exit_code}",
                        flush=True,
                    )
                else:
                    # Final attempt failed
                    print(
                        f"[serial_manager] Script failed after {max_attempts} attempts "
                        f"(exit code {result.exit_code})",
                        flush=True,
                    )
        else:
            raise ValueError(f"Unknown task type: {task.type}")

        # Set task index
        result.task_index = i
        results.append(result)

        # Log result
        if result.exit_code == 0:
            print(
                f"[serial_manager] Task {i+1} completed successfully "
                f"(duration: {result.duration_seconds:.2f}s)",
                flush=True,
            )
        else:
            print(
                f"[serial_manager] Task {i+1} FAILED with exit code {result.exit_code}",
                flush=True,
            )
            print("[serial_manager] Aborting pipeline (Short-Circuit)", flush=True)
            break  # Immediate abort on failure

    return results


def save_pipeline_result(
    session_id: str, results: list[TaskExecutionResult], project_root: str
) -> list[str]:
    """
    Save pipeline execution result to JSON file.

    Args:
        session_id: Session ID
        results: List of task execution results
        project_root: Project root path

    Returns:
        List of child session IDs extracted from results
    """
    all_success = all(r.exit_code == 0 for r in results)

    # Extract child session IDs from output_preview
    child_session_ids = []
    for result in results:
        if result.task_type == "agent" and result.output_preview:
            # Look for [CREATED_SESSION:xxx] marker
            # Session ID format: parent_id/child_id or just session_id
            import re

            match = re.search(
                r"\[CREATED_SESSION:([a-f0-9/]+)\]", result.output_preview
            )
            if match:
                child_session_ids.append(match.group(1))

    pipeline_result = PipelineResult(
        status="success" if all_success else "failed",
        total_tasks=len(results),
        completed_tasks=len(results),
        child_session_ids=child_session_ids,
        results=results,
        timestamp=get_current_timestamp(),
    )

    sessions_dir = Path(project_root) / ".pipe_sessions"
    create_directory(str(sessions_dir))

    result_file = sessions_dir / f"{session_id}_serial_result.json"

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(pipeline_result.model_dump(), f, indent=2, ensure_ascii=False)

    print(f"[serial_manager] Results saved to: {result_file}", flush=True)

    return child_session_ids


def invoke_parent_session(
    session_id: str,
    child_session_ids: list[str],
    project_root: str,
    results: list[TaskExecutionResult] | None = None,
) -> None:
    """
    Invoke parent session to notify completion with child session IDs.

    Args:
        session_id: Parent session ID
        child_session_ids: List of child session IDs created
        project_root: Project root path
        results: List of task execution results (optional, for error reporting)

    Note:
        Sends instruction to parent session with information about how to
        retrieve child session results using get_sessions_final_turns tool
    """
    print(f"[serial_manager] Invoking parent session: {session_id}", flush=True)

    # Check for abort (exit_code 2)
    abort_result = None
    if results:
        for result in results:
            if result.exit_code == 2:
                abort_result = result
                break

    # Build instruction with abort information or child session IDs
    if abort_result:
        instruction = (
            f"🚨 Task execution ABORTED (exit code 2 - permanent failure)\n\n"
            f"Task {abort_result.task_index + 1} failed with exit code 2, "
            f"indicating a permanent failure that cannot be fixed through retries.\n\n"
        )
        if abort_result.output_preview:
            instruction += f"Abort reason:\n```\n{abort_result.output_preview}\n```\n\n"
        instruction += (
            "This typically indicates:\n"
            "- Unauthorized file modifications detected\n"
            "- Validation failures that require manual investigation\n"
            "- Configuration issues that cannot be auto-fixed\n\n"
            "Please investigate the issue manually before retrying."
        )
    elif child_session_ids:
        session_ids_json = json.dumps(child_session_ids)
        instruction = (
            f"Child agent tasks completed successfully. "
            f"To retrieve the results, use get_sessions_final_turns "
            f"with the following session IDs:\n"
            f"session_ids={session_ids_json}\n\n"
            f"Example:\n"
            f"get_sessions_final_turns(session_ids={session_ids_json})"
        )
    else:
        instruction = (
            "Task execution completed. No child sessions were created. "
            "Check the serial result file for details."
        )

    cmd = [
        "poetry",
        "run",
        "takt",
        "--session",
        session_id,
        "--instruction",
        instruction,
    ]

    subprocess.run(cmd, cwd=project_root)


def main() -> None:
    """Main entry point for serial manager"""
    parser = argparse.ArgumentParser(
        description="Serial Task Manager - Execute tasks sequentially"
    )
    parser.add_argument("--parent-session", required=True, help="Parent session ID")
    args = parser.parse_args()

    parent_session_id = args.parent_session
    project_root = get_project_root()

    print(
        f"[serial_manager] Starting serial execution for "
        f"parent session: {parent_session_id}"
    )
    print(f"[serial_manager] Project root: {project_root}")

    try:
        # Load task metadata
        tasks, child_session_id, purpose, background = load_task_metadata(
            parent_session_id, project_root
        )
        print(f"[serial_manager] Loaded {len(tasks)} tasks")
        if child_session_id:
            print(f"[serial_manager] Using child session: {child_session_id}")
        else:
            print(
                f"[serial_manager] Will create new child sessions "
                f"with purpose: {purpose}"
            )

        # Execute tasks sequentially
        results = execute_tasks_serially(
            tasks,
            child_session_id,
            parent_session_id,
            project_root,
            purpose,
            background,
        )

        # Save results and get child session IDs
        child_session_ids = save_pipeline_result(
            parent_session_id, results, project_root
        )

        # Determine success/failure
        all_success = all(r.exit_code == 0 for r in results)

        if all_success:
            print("[serial_manager] ✓ All tasks completed successfully")
        else:
            print("[serial_manager] ✗ Pipeline failed")

        # Invoke parent session with child session IDs and results
        invoke_parent_session(
            parent_session_id, child_session_ids, project_root, results
        )

        # Exit with appropriate code
        sys.exit(0 if all_success else 1)

    except Exception as e:
        import traceback

        print(f"[serial_manager] Fatal error: {e}", file=sys.stderr)
        print("[serial_manager] Traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        logger.exception("Serial manager failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
