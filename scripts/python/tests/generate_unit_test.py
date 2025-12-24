#!/usr/bin/env python3
"""
Automated test generation orchestration script.

This script:
1. Scans target paths for Python source files
2. Launches Test Conductor agent via takt
3. Polls for conductor completion and checks TODOs
4. Continues processing with 120s wait between files (TPM/RPM mitigation)
5. Repeats until all files processed or timeout

Usage:
    poetry run python scripts/python/tests/generate_unit_test.py <targets...> [options]

Examples:
    # Generate tests for all files in a directory
    poetry run python scripts/python/tests/generate_unit_test.py \
        src/pipe/core/repositories

    # Generate tests for specific files
    poetry run python scripts/python/tests/generate_unit_test.py \
        src/pipe/core/repositories/archive_repository.py \
        src/pipe/core/repositories/session_repository.py

    # Resume existing conductor session
    poetry run python scripts/python/tests/generate_unit_test.py \
        --session abc123 src/pipe/core/repositories

    # Custom timeout (default: 600s)
    poetry run python scripts/python/tests/generate_unit_test.py \
        --timeout 1200 src/pipe/core/repositories
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def find_python_files(targets: list[str]) -> list[str]:
    """
    Find all Python source files from target paths (files or directories).

    Args:
        targets: List of file or directory paths

    Returns:
        List of relative file paths (relative to current working directory)
    """
    python_files = []
    cwd = Path.cwd()

    for target in targets:
        target_path = Path(target)

        if not target_path.exists():
            print(f"Error: Path not found: {target}", file=sys.stderr)
            sys.exit(1)

        if target_path.is_file():
            # Single file
            if target_path.suffix == ".py":
                # Convert to relative path
                try:
                    rel_path = target_path.absolute().relative_to(cwd)
                    python_files.append(str(rel_path))
                except ValueError:
                    # If not relative to cwd, use absolute
                    python_files.append(str(target_path.absolute()))
        elif target_path.is_dir():
            # Directory - recursively find files
            for py_file in target_path.rglob("*.py"):
                # Skip __init__.py
                if py_file.name == "__init__.py":
                    continue

                # Skip test files
                if py_file.name.startswith("test_"):
                    continue

                # Skip files in tests/ directory
                if "tests/" in str(py_file) or "/tests/" in str(py_file):
                    continue

                # Skip __pycache__
                if "__pycache__" in str(py_file):
                    continue

                # Convert to relative path
                try:
                    rel_path = py_file.absolute().relative_to(cwd)
                    python_files.append(str(rel_path))
                except ValueError:
                    # If not relative to cwd, use absolute
                    python_files.append(str(py_file.absolute()))

    return sorted(python_files)


def detect_layer(file_path: str) -> str | None:
    """
    Detect layer name from file path.

    Args:
        file_path: Absolute path to Python file

    Returns:
        Layer name (repositories, services, models, etc.) or None
    """
    parts = Path(file_path).parts

    # Look for src/pipe/core/{layer}
    try:
        core_idx = parts.index("core")
        if core_idx + 1 < len(parts):
            layer = parts[core_idx + 1]
            # Validate known layers
            known_layers = {
                "repositories",
                "services",
                "models",
                "collections",
                "domains",
                "tools",
                "agents",
                "validators",
                "factories",
                "utils",
            }
            if layer in known_layers:
                return layer
    except ValueError:
        pass

    return None


def build_file_metadata(files: list[str]) -> list[dict]:
    """
    Build metadata for each file.

    Args:
        files: List of file paths

    Returns:
        List of file metadata dicts
    """
    metadata = []
    for file_path in files:
        layer = detect_layer(file_path)
        if not layer:
            print(f"Warning: Could not detect layer for {file_path}, skipping")
            continue

        filename = Path(file_path).stem
        test_path = f"tests/unit/core/{layer}/test_{filename}.py"

        metadata.append(
            {
                "source_file": file_path,
                "test_file": test_path,
                "layer": layer,
                "filename": filename,
            }
        )

    return metadata


def get_session_result_path(session_id: str) -> Path:
    """Get path to serial result file for session."""
    return Path(f".pipe_sessions/{session_id}_serial_result.json")


def get_session_todos_path(session_id: str) -> Path:
    """Get path to todos file for session."""
    return Path(f".pipe_sessions/{session_id}_todos.json")


def wait_for_conductor_completion(
    session_id: str, timeout: int = 600, poll_interval: int = 5
) -> bool:
    """
    Poll for conductor completion by checking serial result file.

    Args:
        session_id: Conductor session ID
        timeout: Maximum wait time in seconds
        poll_interval: Polling interval in seconds

    Returns:
        True if completed successfully, False if timeout or failure
    """
    result_path = get_session_result_path(session_id)
    start_time = time.time()

    print(f"\n[Polling] Waiting for conductor completion (timeout: {timeout}s)...")
    print(f"[Polling] Result file: {result_path}")

    while True:
        elapsed = time.time() - start_time

        if elapsed > timeout:
            print(f"\n[Polling] ⏱️  Timeout after {timeout}s")
            return False

        # Check if result file exists
        if result_path.exists():
            try:
                with open(result_path) as f:
                    result = json.load(f)

                status = result.get("status")
                print(f"\n[Polling] ✓ Conductor completed with status: {status}")

                # Delete result file for next iteration
                result_path.unlink()

                return status == "success"

            except (OSError, json.JSONDecodeError) as e:
                print(f"\n[Polling] Warning: Failed to read result file: {e}")
                # Continue polling

        # Show progress
        print(f"[Polling] Waiting... ({int(elapsed)}s elapsed)", end="\r", flush=True)
        time.sleep(poll_interval)


def get_remaining_todos(session_id: str) -> list[dict]:
    """
    Get pending TODO items from conductor session.

    Args:
        session_id: Conductor session ID

    Returns:
        List of pending TODO items
    """
    todos_path = get_session_todos_path(session_id)

    if not todos_path.exists():
        print(f"[TODO] No TODO file found: {todos_path}")
        return []

    try:
        with open(todos_path) as f:
            data = json.load(f)

        todos = data.get("todos", [])
        pending = [t for t in todos if t.get("status") == "pending"]

        print(
            f"\n[TODO] Found {len(pending)} pending items (out of {len(todos)} total)"
        )
        return pending

    except (OSError, json.JSONDecodeError) as e:
        print(f"[TODO] Error reading TODO file: {e}")
        return []


def launch_conductor(
    file_metadata: list[dict], session_id: str | None = None
) -> str | None:
    """
    Launch Test Conductor agent via takt.

    Args:
        file_metadata: List of file metadata
        session_id: Optional session ID to resume

    Returns:
        Session ID (new or resumed)
    """
    if not file_metadata and not session_id:
        print("No files to process")
        return None

    # Build takt command
    takt_cmd = ["poetry", "run", "takt"]

    if session_id:
        # Resume existing session
        print(f"\n[Conductor] Resuming session: {session_id}")
        takt_cmd.extend(["--session", session_id])
        takt_cmd.extend(
            [
                "--instruction",
                "Continue test generation for remaining pending files in TODO list. "
                "Process ONLY THE NEXT PENDING FILE via invoke_serial_children, "
                "then exit. "
                "DO NOT process all remaining files at once.",
            ]
        )
        resume_mode = True
    else:
        # Start new session with conductor role + procedure
        print(f"\n[Conductor] Starting new session for {len(file_metadata)} files")

        takt_cmd.extend(
            [
                "--purpose",
                f"Automated test generation for {len(file_metadata)} "
                "Python source files",
            ]
        )
        takt_cmd.extend(
            [
                "--background",
                "Orchestrate test generation by delegating to child agents "
                "via invoke_serial_children",
            ]
        )
        takt_cmd.extend(["--roles", "roles/conductor.md"])
        takt_cmd.extend(["--procedure", "procedures/python_unit_test_conductor.md"])

        # Build initial instruction
        file_list = "\n".join(
            [
                f"- {m['source_file']} → {m['test_file']} (layer: {m['layer']})"
                for m in file_metadata
            ]
        )
        instruction_template = (
            "Follow @procedures/python_unit_test_conductor.md to generate tests "
            "for the following files:\n\n"
            "{file_list}\n\n"
            "Execute all steps in the procedure:\n"
            "1. Receive and parse file list (done above)\n"
            "2. Create TODO list via edit_todos\n"
            "3. Process ONLY THE FIRST FILE via invoke_serial_children\n"
            "4. DO NOT process remaining files - wait for script to call you again\n\n"
            "IMPORTANT: Process only ONE file per invocation, then exit."
        )
        instruction = instruction_template.format(file_list=file_list)
        takt_cmd.extend(["--instruction", instruction])
        resume_mode = False

    # Execute takt and capture session ID
    print(f"[Conductor] Command: {' '.join(takt_cmd)}\n")

    try:
        result = subprocess.run(takt_cmd, check=False, capture_output=True, text=True)

        # Extract session ID from output
        if not resume_mode:
            session_id_from_stdout = None
            for line in result.stdout.strip().split("\n"):
                if line.strip().startswith("{"):
                    try:
                        data = json.loads(line.strip())
                        if "session_id" in data:
                            session_id_from_stdout = data["session_id"]
                            print(
                                f"[Conductor] Created session: {session_id_from_stdout}"
                            )
                            session_id = session_id_from_stdout
                            break  # Found session_id, exit loop
                    except json.JSONDecodeError:
                        print(
                            "[Conductor] Warning: Could not parse "
                            "session ID from stdout"
                        )
                        continue  # Continue to next line if JSON fails

            # If session_id not found in stdout, try to find the latest session file
            if session_id is None:  # Check session_id for the overall status
                print(
                    "[Conductor] Session ID not in stdout, searching for "
                    "latest session file..."
                )
                sessions_dir = Path("sessions")
                if sessions_dir.exists():
                    # Find the most recently created session file
                    session_files = sorted(
                        [
                            f
                            for f in sessions_dir.glob("*.json")
                            if not f.name.startswith(".")
                        ],
                        key=lambda f: f.stat().st_mtime,
                        reverse=True,
                    )
                    for session_file in session_files[:5]:  # Check last 5 sessions
                        try:
                            with open(session_file) as f:
                                session_data = json.load(f)
                                candidate_id = session_data.get("session_id")
                                purpose = session_data.get("purpose", "")
                                # Match purpose to ensure we get the right session
                                if (
                                    candidate_id
                                    and "Automated test generation" in purpose
                                ):
                                    session_id = candidate_id
                                    print(
                                        f"[Conductor] Found session from file: "
                                        f"{session_id}"
                                    )
                                    break
                        except (OSError, json.JSONDecodeError):
                            continue

        if session_id is None:
            print("[Conductor] Error: Could not determine session ID")
            print(f"[Conductor] stdout: {result.stdout}")
            print(f"[Conductor] stderr: {result.stderr}")
            raise SystemExit(1)

        # Check exit code after we have session_id
        if result.returncode != 0:
            print(f"[Conductor] Warning: takt exited with code {result.returncode}")
            if result.stderr:
                print(f"[Conductor] stderr: {result.stderr}")
            # Don't exit here - conductor may have called invoke_serial_children

    except FileNotFoundError:
        print("Error: takt command not found. Is Poetry installed?")
        raise SystemExit(1)

    return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate tests for Python source files"
    )
    parser.add_argument(
        "targets",
        nargs="+",
        help="Files or directories containing source files to test",
    )
    parser.add_argument(
        "--session", "-s", help="Session ID to resume conductor session", default=None
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=600,
        help="Timeout for conductor completion (seconds, default: 600)",
    )
    parser.add_argument(
        "--wait",
        "-w",
        type=int,
        default=120,
        help="Wait time between file processing (seconds, default: 120)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Automated Test Generation")
    print("=" * 70)
    print(f"Targets: {', '.join(args.targets)}")
    print(f"Timeout: {args.timeout}s per file")
    print(f"Wait between files: {args.wait}s")
    if args.session:
        print(f"Resume session: {args.session}")
    print("")

    # Find Python files (only needed for new sessions)
    if not args.session:
        python_files = find_python_files(args.targets)
        print(f"[Scan] Found {len(python_files)} Python source files")

        if not python_files:
            print("No Python files found to test")
            sys.exit(0)

        # Build metadata
        file_metadata = build_file_metadata(python_files)

        if not file_metadata:
            print("No files with detectable layers found")
            sys.exit(0)

        print(f"[Scan] {len(file_metadata)} files have detectable layers:\n")
        for meta in file_metadata:
            print(f"  • {meta['source_file']}")
            print(f"    → {meta['test_file']} (layer: {meta['layer']})\n")
    else:
        file_metadata = []  # Not needed for resume

    # Main orchestration loop
    session_id = args.session
    iteration = 0
    max_iterations = 100  # Safety limit

    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 70}")
        print(f"Iteration {iteration}")
        print(f"{'=' * 70}")

        # Launch or resume conductor
        session_id = launch_conductor(file_metadata, session_id)

        if not session_id:
            print("\n[Error] Failed to get session ID")
            sys.exit(1)

        # Wait for conductor completion
        success = wait_for_conductor_completion(session_id, timeout=args.timeout)

        if not success:
            print("\n[Error] Conductor did not complete successfully")
            print(f"[Info] You can resume with: --session {session_id}")
            sys.exit(1)

        # Check remaining TODOs
        pending_todos = get_remaining_todos(session_id)

        if not pending_todos:
            print("\n" + "=" * 70)
            print("✅ All files processed successfully!")
            print("=" * 70)
            sys.exit(0)

        # Wait before next iteration (TPM/RPM mitigation)
        print(f"\n[Wait] Sleeping {args.wait}s before processing next file...")
        print(f"[Wait] Remaining files: {len(pending_todos)}")
        time.sleep(args.wait)

        # Continue with same session
        # file_metadata will be ignored on resume

    print("\n[Error] Maximum iterations reached")
    sys.exit(1)


if __name__ == "__main__":
    main()
