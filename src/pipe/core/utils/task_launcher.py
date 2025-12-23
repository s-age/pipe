"""Common launcher for task managers (serial/parallel).

Environment: Poetry-managed Python project
"""

import json
import subprocess
import sys
from pathlib import Path

from pipe.core.utils.file import create_directory
from pipe.core.utils.path import get_project_root


def launch_manager(
    manager_type: str,
    tasks: list[dict],
    parent_session_id: str,
    child_session_id: str | None = None,
    purpose: str | None = None,
    background: str | None = None,
    **kwargs,
) -> None:
    """
    Launch task manager as detached process and exit parent process.

    Args:
        manager_type: "serial" or "parallel"
        tasks: List of task definitions (dict format)
        parent_session_id: Parent session ID (for result reporting)
        child_session_id: Child session ID (optional, for agent tasks)
        purpose: Purpose for new child sessions
            (required if child_session_id is None and agent tasks exist)
        background: Background for new child sessions
            (required if child_session_id is None and agent tasks exist)
        **kwargs: Manager-specific options

    Note:
        This function exits the parent process (sys.exit), so it never returns.
        project_root is automatically detected via get_project_root()
    """
    project_root = get_project_root()

    # Save task definition file
    sessions_dir = Path(project_root) / ".pipe_sessions"
    create_directory(str(sessions_dir))

    # Save tasks with session metadata
    task_metadata = {
        "parent_session_id": parent_session_id,
        "child_session_id": child_session_id,
        "purpose": purpose,
        "background": background,
        "tasks": tasks,
    }

    tasks_file = sessions_dir / f"{parent_session_id}_tasks.json"

    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(task_metadata, f, indent=2, ensure_ascii=False)

    # Select manager module
    if manager_type == "serial":
        module = "pipe.core.services.serial_manager_service"
        extra_args: list[str] = []
    elif manager_type == "parallel":
        module = "pipe.core.services.parallel_manager_service"
        max_workers = kwargs.get("max_workers", 4)
        extra_args = ["--max-workers", str(max_workers)]
    else:
        raise ValueError(f"Unknown manager type: {manager_type}")

    # Launch command via Poetry
    cmd = [
        "poetry",
        "run",
        "python",
        "-m",
        module,
        "--parent-session",
        parent_session_id,
    ] + extra_args

    # Launch as detached process with logging
    log_file = sessions_dir / f"{parent_session_id}_{manager_type}_manager.log"

    with open(log_file, "w", encoding="utf-8") as log_f:
        subprocess.Popen(
            cmd,
            cwd=project_root,
            start_new_session=True,  # Independent from parent process
            stdout=log_f,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout (same log file)
            stdin=subprocess.DEVNULL,
        )

    print(f"[task_launcher] Launched {manager_type} manager (detached)")
    print(f"[task_launcher] Log file: {log_file}")
    print("[task_launcher] Parent process exiting to save tokens...")

    # Exit parent process immediately
    sys.exit(0)
