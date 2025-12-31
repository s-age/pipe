#!/usr/bin/env python3
"""
Automated test generation orchestration script.

This script implements a two-phase approach:

Phase 1: Initialize Session (new sessions only)
1. Scans target paths for Python source files
2. Launches Test Conductor to create TODO list via edit_todos
   - Each TODO contains metadata: source_file, test_file, layer
3. Conductor exits immediately after TODO creation

Phase 2: Process TODOs (iterative)
1. Reads unchecked TODOs from sessions/${sessionId}.json
2. Parses metadata from TODO description
3. Sends fully-formed invoke_serial_children instruction to conductor with:
   - Expanded roles (tests.md + layer-specific role)
   - File paths and layer information
   - Complete task structure with agent + validation script
4. Polls .processes/${sessionId}.pid for deletion (completion)
5. Continues with next TODO if unchecked items remain
6. Waits 120s between iterations (TPM/RPM mitigation)

Key Improvements:
- No more vague "mark as in_progress" instructions (pipe doesn't use that state)
- Fully expanded invoke_serial_children parameters in the instruction
- Includes both tests.md and layer-specific roles
- Complete task structure with retry configuration

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
        --session abc123

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


def get_session_json_path(session_id: str) -> Path:
    """Get path to session JSON file."""
    return Path(f"sessions/{session_id}.json")


def get_pid_file_path(session_id: str) -> Path:
    """Get path to PID file for session."""
    return Path(f".processes/{session_id}.pid")


def wait_for_conductor_completion(
    session_id: str, timeout: int = 600, poll_interval: int = 5
) -> bool:
    """
    Poll for conductor completion by checking PID file deletion.

    Args:
        session_id: Conductor session ID
        timeout: Maximum wait time in seconds
        poll_interval: Polling interval in seconds

    Returns:
        True if completed (PID deleted), False if timeout
    """
    pid_path = get_pid_file_path(session_id)
    start_time = time.time()

    print(f"\n[Polling] Waiting for conductor completion (timeout: {timeout}s)...")
    print(f"[Polling] Monitoring PID file: {pid_path}")

    # Wait for PID file to be deleted
    while True:
        elapsed = time.time() - start_time

        if elapsed > timeout:
            print(f"\n[Polling] ⏱️  Timeout after {timeout}s")
            return False

        # Check if PID file has been deleted (or never existed)
        if not pid_path.exists():
            print("\n[Polling] ✓ Conductor completed (PID file deleted)")
            return True

        # Show progress
        print(
            f"[Polling] Waiting for PID deletion... ({int(elapsed)}s)",
            end="\r",
            flush=True,
        )
        time.sleep(poll_interval)


def get_todos_from_session(session_id: str) -> tuple[list[dict], list[dict]]:
    """
    Get TODO items from session JSON file.

    Args:
        session_id: Conductor session ID

    Returns:
        Tuple of (all_todos, unchecked_todos)
    """
    session_path = get_session_json_path(session_id)

    if not session_path.exists():
        print(f"[TODO] Session file not found: {session_path}")
        return [], []

    try:
        with open(session_path) as f:
            data = json.load(f)

        todos = data.get("todos", [])
        unchecked = [t for t in todos if not t.get("checked", False)]

        print(
            f"\n[TODO] Found {len(unchecked)} unchecked items (out of {len(todos)} total)"
        )
        for idx, todo in enumerate(unchecked, 1):
            print(
                f"  {idx}. {todo.get('title', 'Untitled')}: {todo.get('description', '')}"
            )

        return todos, unchecked

    except (OSError, json.JSONDecodeError) as e:
        print(f"[TODO] Error reading session file: {e}")
        return [], []


def execute_next_todo(session_id: str) -> bool:
    """
    Execute the next unchecked TODO by sending instruction to conductor.

    Args:
        session_id: Conductor session ID

    Returns:
        True if instruction sent successfully, False otherwise
    """
    _, unchecked_todos = get_todos_from_session(session_id)

    if not unchecked_todos:
        print("\n[TODO] No unchecked TODOs found")
        return False

    # Get the first unchecked TODO
    next_todo = unchecked_todos[0]
    todo_title = next_todo.get("title", "")
    todo_description = next_todo.get("description", "")

    print(f"\n[Execute] Processing next TODO: {todo_title}")

    # Parse file metadata from description
    # Expected format: "source_file=..., test_file=..., layer=..."
    source_file = ""
    test_file = ""
    layer = ""

    try:
        # Parse description to extract metadata
        for part in todo_description.split(", "):
            if "=" in part:
                key, value = part.split("=", 1)
                if key.strip() == "source_file":
                    source_file = value.strip()
                elif key.strip() == "test_file":
                    test_file = value.strip()
                elif key.strip() == "layer":
                    layer = value.strip()
    except Exception as e:
        print(f"[Execute] Warning: Failed to parse TODO description: {e}")
        print(f"[Execute] Description: {todo_description}")

    if not source_file or not layer:
        print("[Execute] Error: Could not extract source_file or layer from TODO")
        return False

    # Derive test_file if not provided
    if not test_file:
        filename = Path(source_file).stem
        test_file = f"tests/unit/core/{layer}/test_{filename}.py"

    filename = Path(source_file).stem

    print(f"[Execute] Source: {source_file}")
    print(f"[Execute] Test: {test_file}")
    print(f"[Execute] Layer: {layer}")

    # Build comprehensive instruction with all necessary parameters
    instruction = f"""Process the next TODO item: {todo_title}

Follow @procedures/python_unit_test_conductor.md Step 3b-3c:

File Details:
- Source file: {source_file}
- Test output: {test_file}
- Layer: {layer}
- Filename: {filename}

Execute invoke_serial_children with the following exact parameters:

invoke_serial_children(
{{
  "roles": ["roles/python/tests/tests.md", "roles/python/tests/core/{layer}.md"],
  "references_persist": ["{source_file}"],
  "purpose": "Generate tests for {filename}.py",
  "tasks": [
    {{
      "type": "agent",
      "instruction": "Follow @procedures/python_unit_test_generation.md to write tests. Target: {source_file}. Output: {test_file}. Execute all 7 steps sequentially. Coverage: 95%+.\\n\\nTool Usage Guidelines:\\n- When using tools like py_analyze_code, py_test_strategist, etc., do not output the function call as text - just execute it.\\n- If a tool needs to be called, call it directly without describing the call in your response.",
      "roles": ["roles/python/tests/tests.md", "roles/python/tests/core/{layer}.md"],
      "references_persist": ["{source_file}"],
      "procedure": "procedures/python_unit_test_generation.md"
    }},
    {{
      "type": "script",
      "script": "python/validate_code.sh",
      "max_retries": 2
    }}
  ],
  "background": "Write comprehensive pytest tests for {source_file}",
  "child_session_id": null,
  "procedure": "procedures/python_unit_test_generation.md"
}})

After calling invoke_serial_children, EXIT IMMEDIATELY.

Tool Usage Guidelines:
- Do not output the function call as text - just execute it.
- Call the tool directly without describing the call in your response.
"""

    # Execute takt with instruction
    takt_cmd = [
        "poetry",
        "run",
        "takt",
        "--session",
        session_id,
        "--instruction",
        instruction,
    ]

    print(f"[Execute] Command: {' '.join(takt_cmd[:6])}...")

    try:
        result = subprocess.run(takt_cmd, check=False, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[Execute] Warning: takt exited with code {result.returncode}")
            if result.stderr:
                print(f"[Execute] stderr: {result.stderr}")

        return True

    except FileNotFoundError:
        print("[Execute] Error: takt command not found")
        return False


def launch_conductor_for_init(file_metadata: list[dict]) -> str | None:
    """
    Launch Test Conductor agent to create TODO list only.

    Args:
        file_metadata: List of file metadata

    Returns:
        Session ID of created session
    """
    if not file_metadata:
        print("No files to process")
        return None

    # Start new session with conductor role + procedure
    print(f"\n[Conductor] Starting new session for {len(file_metadata)} files")

    takt_cmd = ["poetry", "run", "takt"]

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
        "Execute ONLY step 2:\n"
        "2. Create TODO list via edit_todos with all files listed above\n\n"
        "IMPORTANT: For each TODO, the description field MUST contain metadata in this format:\n"
        '  description: "source_file=<path>, test_file=<path>, layer=<layer>"\n\n'
        "Example:\n"
        '  title: "Generate tests for gemini_api_static_payload.py"\n'
        '  description: "source_file=src/pipe/core/domains/gemini_api_static_payload.py, '
        'test_file=tests/unit/core/domains/test_gemini_api_static_payload.py, layer=domains"\n\n'
        "After successfully creating TODOs with edit_todos, EXIT IMMEDIATELY.\n"
        "DO NOT process any files yet - the script will call you again "
        "to process each file one by one.\n\n"
        "IMPORTANT: Only create the TODO list, then exit. "
        "Do NOT call invoke_serial_children in this invocation."
    )
    instruction = instruction_template.format(file_list=file_list)
    takt_cmd.extend(["--instruction", instruction])

    # Execute takt and capture session ID
    print(f"[Conductor] Command: {' '.join(takt_cmd)}\n")

    try:
        result = subprocess.run(takt_cmd, check=False, capture_output=True, text=True)

        # Extract session ID from output
        session_id = None
        for line in result.stdout.strip().split("\n"):
            if line.strip().startswith("{"):
                try:
                    data = json.loads(line.strip())
                    if "session_id" in data:
                        session_id = data["session_id"]
                        print(f"[Conductor] Created session: {session_id}")
                        break  # Found session_id, exit loop
                except json.JSONDecodeError:
                    print("[Conductor] Warning: Could not parse session ID from stdout")
                    continue  # Continue to next line if JSON fails

        # If session_id not found in stdout, try to find the latest session file
        if session_id is None:
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
                            if candidate_id and "Automated test generation" in purpose:
                                session_id = candidate_id
                                print(
                                    f"[Conductor] Found session from file: {session_id}"
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

    return session_id


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

    # Phase 1: Initialize session and create TODOs (only for new sessions)
    session_id = args.session

    if not session_id:
        print("\n" + "=" * 70)
        print("Phase 1: Initialize Session and Create TODOs")
        print("=" * 70)

        # Launch conductor to create TODO list only
        session_id = launch_conductor_for_init(file_metadata)

        if not session_id:
            print("\n[Error] Failed to create session")
            sys.exit(1)

        # Wait for TODO creation to complete
        success = wait_for_conductor_completion(session_id, timeout=args.timeout)

        if not success:
            print("\n[Error] Failed to create TODO list")
            print(f"[Info] You can resume with: --session {session_id}")
            sys.exit(1)

        print("\n[Init] TODO list created successfully")

    # Phase 2: Process TODOs one by one
    print("\n" + "=" * 70)
    print("Phase 2: Process TODOs")
    print("=" * 70)

    iteration = 0
    max_iterations = 100  # Safety limit

    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 70}")
        print(f"Iteration {iteration}")
        print(f"{'=' * 70}")

        # Check TODOs before processing
        _, unchecked_todos = get_todos_from_session(session_id)

        if not unchecked_todos:
            print("\n" + "=" * 70)
            print("✅ All files processed successfully!")
            print("=" * 70)
            sys.exit(0)

        # Execute next TODO
        print(f"\n[Process] {len(unchecked_todos)} TODOs remaining")
        success = execute_next_todo(session_id)

        if not success:
            print("\n[Error] Failed to execute TODO")
            print(f"[Info] You can resume with: --session {session_id}")
            sys.exit(1)

        # Wait for conductor completion
        success = wait_for_conductor_completion(session_id, timeout=args.timeout)

        if not success:
            print("\n[Error] Conductor did not complete successfully")
            print(f"[Info] You can resume with: --session {session_id}")
            sys.exit(1)

        # Wait before next iteration (TPM/RPM mitigation)
        if iteration < max_iterations:
            print(f"\n[Wait] Sleeping {args.wait}s before processing next file...")
            time.sleep(args.wait)

    print("\n[Error] Maximum iterations reached")
    sys.exit(1)


if __name__ == "__main__":
    main()
