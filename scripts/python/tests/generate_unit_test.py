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
- Dynamic dependency injection via AST analysis

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
import ast
import json
import subprocess
import sys
import time
from pathlib import Path


def extract_local_dependencies(
    file_path: str, project_root: Path | None = None
) -> list[str]:
    """
    Extract project-internal dependencies from a Python file via AST analysis.

    Analyzes import statements to identify dependencies on other modules within
    the project (modules starting with 'pipe.'). Returns resolved file paths for
    these dependencies.

    Args:
        file_path: Path to the Python file to analyze
        project_root: Project root directory (defaults to cwd)

    Returns:
        Sorted list of unique file paths for project-internal dependencies.
        Returns empty list on parse errors (fail-safe).

    Examples:
        >>> extract_local_dependencies('src/pipe/core/services/session_service.py')
        ['src/pipe/core/models/turn.py', 'src/pipe/core/repositories/session_repository.py']
    """
    if project_root is None:
        project_root = Path.cwd()

    dependencies = set()

    try:
        # Read and parse the target file
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=file_path)

        # Walk AST to find import statements
        for node in ast.walk(tree):
            module_name = None

            if isinstance(node, ast.ImportFrom):
                # from pipe.core.models import Turn
                if node.module and node.module.startswith("pipe."):
                    module_name = node.module
            elif isinstance(node, ast.Import):
                # import pipe.core.utils.datetime
                for alias in node.names:
                    if alias.name.startswith("pipe."):
                        module_name = alias.name

            if module_name:
                # Convert module name to file path
                # pipe.core.models.turn -> src/pipe/core/models/turn
                relative_path = module_name.replace(".", "/")
                base_path = project_root / "src" / relative_path

                # Priority 1: Check for .py file
                py_file = base_path.with_suffix(".py")
                if py_file.exists():
                    # Convert to relative path from project root
                    try:
                        rel = py_file.relative_to(project_root)
                        dependencies.add(str(rel))
                        continue
                    except ValueError:
                        pass

                # Priority 2: Check for __init__.py
                init_file = base_path / "__init__.py"
                if init_file.exists():
                    try:
                        rel = init_file.relative_to(project_root)
                        dependencies.add(str(rel))
                    except ValueError:
                        pass

    except (OSError, SyntaxError, UnicodeDecodeError):
        # Fail-safe: Return empty list on any error
        pass

    return sorted(dependencies)


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


def detect_layer(file_path: str) -> tuple[str, str | None] | None:
    """
    Detect layer name and module from file path.

    Args:
        file_path: Absolute path to Python file

    Returns:
        Tuple of (module, layer) where module is 'core' or 'web', and layer can be None
        for web root files, or None if layer cannot be detected
    """
    parts = Path(file_path).parts

    # Look for src/pipe/core/{layer}
    try:
        core_idx = parts.index("core")
        if core_idx + 1 < len(parts):
            layer = parts[core_idx + 1]
            # Validate known core layers
            known_core_layers = {
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
                "delegates",
            }
            if layer in known_core_layers:
                return ("core", layer)
    except ValueError:
        pass

    # Look for src/pipe/web/{layer}
    try:
        web_idx = parts.index("web")
        if web_idx + 1 < len(parts):
            layer = parts[web_idx + 1]

            # If the next part is a .py file (not a directory), it's a direct web layer file
            # e.g., src/pipe/web/action_responses.py -> tests/unit/web/test_action_responses.py
            if layer.endswith(".py"):
                # Return None for layer to indicate this is a web root file
                # This will be handled specially in build_file_metadata
                return ("web", None)

            # Validate known web layers (subdirectories)
            known_web_layers = {
                "requests",
                "responses",
                "actions",
                "controllers",
                "middleware",
                "validators",
            }
            if layer in known_web_layers:
                return ("web", layer)
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
        layer_info = detect_layer(file_path)
        if not layer_info:
            print(f"Warning: Could not detect layer for {file_path}, skipping")
            continue

        module, layer = layer_info
        filename = Path(file_path).stem

        # Handle web root files (layer is None)
        # e.g., src/pipe/web/action_responses.py -> tests/unit/web/test_action_responses.py
        if layer is None:
            test_path = f"tests/unit/{module}/test_{filename}.py"
            # Use module name as layer for role resolution
            effective_layer = module
        else:
            test_path = f"tests/unit/{module}/{layer}/test_{filename}.py"
            effective_layer = layer

        metadata.append(
            {
                "source_file": file_path,
                "test_file": test_path,
                "module": module,
                "layer": effective_layer,
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


def check_session_exit_code(session_id: str) -> int | None:
    """
    Check the last turn in session for exit code error messages.

    Args:
        session_id: Conductor session ID

    Returns:
        Exit code if found in error message, None otherwise
    """
    session_path = get_session_json_path(session_id)

    if not session_path.exists():
        return None

    try:
        with open(session_path) as f:
            data = json.load(f)

        turns = data.get("turns", [])
        if not turns:
            return None

        # Check last turn for exit code messages
        last_turn = turns[-1]
        if last_turn.get("type") == "user_task":
            instruction = last_turn.get("instruction", "")
            # Check for exit code 2 (permanent failure)
            if "exit code 2" in instruction.lower():
                return 2
            # Check for exit code 1 (retryable failure)
            if "exit code 1" in instruction.lower():
                return 1

        return None

    except (OSError, json.JSONDecodeError) as e:
        print(f"[Session] Error reading session file: {e}")
        return None


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
    # Expected format: "source_file=..., test_file=..., module=..., layer=..."
    source_file = ""
    test_file = ""
    module = ""
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
                elif key.strip() == "module":
                    module = value.strip()
                elif key.strip() == "layer":
                    layer = value.strip()
    except Exception as e:
        print(f"[Execute] Warning: Failed to parse TODO description: {e}")
        print(f"[Execute] Description: {todo_description}")

    if not source_file or not layer:
        print("[Execute] Error: Could not extract source_file or layer from TODO")
        return False

    # Derive module if not provided (default to core for backward compatibility)
    if not module:
        module = "core"

    # Derive test_file if not provided
    if not test_file:
        filename = Path(source_file).stem
        test_file = f"tests/unit/{module}/{layer}/test_{filename}.py"

    filename = Path(source_file).stem

    print(f"[Execute] Source: {source_file}")
    print(f"[Execute] Test: {test_file}")
    print(f"[Execute] Module: {module}")
    print(f"[Execute] Layer: {layer}")

    # Dynamic dependency analysis
    print(f"[Execute] Analyzing dependencies for {source_file}...")
    dynamic_dependencies = extract_local_dependencies(source_file)

    if dynamic_dependencies:
        print(f"[Execute] Found {len(dynamic_dependencies)} project dependencies:")
        for dep in dynamic_dependencies:
            print(f"[Execute]   - {dep}")
    else:
        print("[Execute] No project dependencies found")

    # Build references_persist list
    base_references = [
        source_file,
        "src/pipe/core/factories/prompt_factory.py",
        "src/pipe/core/factories/service_factory.py",
        "src/pipe/core/factories/settings_factory.py",
        "src/pipe/core/factories/file_repository_factory.py",
    ]

    # Merge and deduplicate
    all_references = sorted(list(set(base_references + dynamic_dependencies)))

    print(f"[Execute] Total references_persist: {len(all_references)} files")

    # Build JSON structure for references_persist
    references_json = json.dumps(all_references, indent=6)

    # Build comprehensive instruction with all necessary parameters
    instruction = f"""Process the next TODO item: {todo_title}

Follow @procedures/python_unit_test_conductor.md Step 3b-3c:

File Details:
- Source file: {source_file}
- Test output: {test_file}
- Module: {module}
- Layer: {layer}
- Filename: {filename}

Execute invoke_serial_children with the following exact parameters:

invoke_serial_children(
{{
  "roles": ["roles/python/tests/tests.md", "roles/python/tests/{module}/{layer}.md"],
  "references_persist": {references_json},
  "purpose": "Generate tests for {filename}.py",
  "tasks": [
    {{
      "type": "agent",
      "instruction": "🎯 CRITICAL MISSION: Implement comprehensive pytest tests\\n\\n📋 Target Specification:\\n- Test target file: {source_file}\\n- Test output path: {test_file}\\n- Architecture module: {module}\\n- Architecture layer: {layer}\\n\\n⚠️ ABSOLUTE REQUIREMENTS:\\n1. Tests that fail have NO VALUE - ALL checks must pass\\n2. Follow @procedures/python_unit_test_generation.md (all 7 steps, no shortcuts)\\n3. Coverage target: 95%+ (non-negotiable)\\n4. ONLY modify {test_file} - any other file changes = immediate abort\\n\\n✅ Success Criteria (Test Execution Report):\\n- [ ] Linter (Ruff/Format): Pass\\n- [ ] Type Check (MyPy): Pass\\n- [ ] Test Result (Pytest): Pass (0 failures)\\n- [ ] Coverage: 95%+ achieved\\n\\nRefer to @roles/python/tests/tests.md 'Test Execution Report' section for the required checklist format.\\n\\n🔧 Tool Execution Protocol:\\n- **EXECUTE, DON'T DISPLAY:** Do NOT write tool calls in markdown text or code blocks\\n- **IGNORE DOC FORMATTING:** Code blocks in procedures are illustrations only - convert them to actual tool invocations\\n- **IMMEDIATE INVOCATION:** Your response must be tool use requests, not text descriptions\\n- **NO PREAMBLE:** No 'I will now...', 'Okay...', 'Let me...' - invoke Step 1a tool immediately\\n- **COMPLETE ALL 7 STEPS:** Continue invoking tools through all steps until Test Execution Report is done",
      "roles": ["roles/python/tests/tests.md", "roles/python/tests/{module}/{layer}.md"],
      "references_persist": {references_json},
      "procedure": "procedures/python_unit_test_generation.md"
    }},
    {{
      "type": "script",
      "script": "python/validate_code.sh",
      "max_retries": 2
    }}
  ],
  "background": "Complete ALL 7 steps in python_unit_test_generation.md for {source_file}. Verify Test Execution Report checklist: Linter Pass, Type Check Pass, Pytest Pass (0 failures), Coverage 95%+. DO NOT exit until all checklist items are completed.",
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
            f"- {m['source_file']} → {m['test_file']} (module: {m['module']}, layer: {m['layer']})"
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
        '  description: "source_file=<path>, test_file=<path>, module=<module>, layer=<layer>"\n\n'
        "Example:\n"
        '  title: "Generate tests for gemini_api_static_payload.py"\n'
        '  description: "source_file=src/pipe/core/domains/gemini_api_static_payload.py, '
        'test_file=tests/unit/core/domains/test_gemini_api_static_payload.py, module=core, layer=domains"\n\n'
        "Example (web):\n"
        '  title: "Generate tests for therapist_requests.py"\n'
        '  description: "source_file=src/pipe/web/requests/therapist_requests.py, '
        'test_file=tests/unit/web/requests/test_therapist_requests.py, module=web, layer=requests"\n\n'
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
            print(
                f"    → {meta['test_file']} (module: {meta['module']}, layer: {meta['layer']})\n"
            )
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

        # Check for permanent failure (exit code 2)
        exit_code = check_session_exit_code(session_id)
        if exit_code == 2:
            print("\n" + "=" * 70)
            print("🚨 PERMANENT FAILURE DETECTED (exit code 2)")
            print("=" * 70)
            print("[Error] The conductor encountered a permanent failure that")
            print("[Error] cannot be fixed through retries. This typically indicates:")
            print("[Error] - Unauthorized file modifications detected")
            print("[Error] - Validation failures requiring manual investigation")
            print("[Error] - Configuration issues that cannot be auto-fixed")
            print("")
            print("[Action] Please check the session logs for details:")
            print(f"[Action]   sessions/{session_id}.json")
            print("")
            print("[Action] After fixing the issue, you can resume with:")
            print(f"[Action]   --session {session_id}")
            print("=" * 70)
            sys.exit(2)

        # Wait before next iteration (TPM/RPM mitigation)
        if iteration < max_iterations:
            print(f"\n[Wait] Sleeping {args.wait}s before processing next file...")
            time.sleep(args.wait)

    print("\n[Error] Maximum iterations reached")
    sys.exit(1)


if __name__ == "__main__":
    main()
