#!/usr/bin/env python3
"""
Automated Storybook story generation orchestration script.

This script implements a two-phase approach:

Phase 1: Initialize Session (new sessions only)
1. Scans target paths for TypeScript React component files
2. Launches Test Conductor to create TODO list via edit_todos
   - Each TODO contains metadata: component_file, story_file, layer
3. Conductor exits immediately after TODO creation

Phase 2: Process TODOs (iterative)
1. Reads unchecked TODOs from sessions/${sessionId}.json
2. Parses metadata from TODO description
3. Sends fully-formed invoke_serial_children instruction to conductor with:
   - Expanded roles (storybook.md + layer-specific role)
   - File paths and layer information
   - Complete task structure with agent + validation script
4. Polls .processes/${sessionId}.pid for deletion (completion)
5. Continues with next TODO if unchecked items remain
6. Waits 120s between iterations (TPM/RPM mitigation)

Key Improvements:
- No more vague "mark as in_progress" instructions (pipe doesn't use that state)
- Fully expanded invoke_serial_children parameters in the instruction
- Includes both storybook.md and layer-specific roles
- Complete task structure with retry configuration

Usage:
    poetry run python scripts/typescript/tests/generate_storybook.py <targets...> [options]

Examples:
    # Generate stories for all components in a directory
    poetry run python scripts/typescript/tests/generate_storybook.py \
        src/web/components/atoms

    # Generate stories for specific components
    poetry run python scripts/typescript/tests/generate_storybook.py \
        src/web/components/atoms/Button \
        src/web/components/molecules/InputText

    # Resume existing conductor session
    poetry run python scripts/typescript/tests/generate_storybook.py \
        --session abc123

    # Custom timeout (default: 600s)
    poetry run python scripts/typescript/tests/generate_storybook.py \
        --timeout 1200 src/web/components/atoms
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def find_component_files(targets: list[str]) -> list[str]:
    """
    Find all TypeScript React component files from target paths (files or directories).

    Args:
        targets: List of file or directory paths

    Returns:
        List of relative file paths (relative to current working directory)
    """
    component_files = []
    cwd = Path.cwd()

    for target in targets:
        target_path = Path(target)

        if not target_path.exists():
            print(f"Error: Path not found: {target}", file=sys.stderr)
            sys.exit(1)

        if target_path.is_file():
            # Single file - must be index.tsx
            if target_path.name == "index.tsx":
                try:
                    rel_path = target_path.absolute().relative_to(cwd)
                    component_files.append(str(rel_path))
                except ValueError:
                    component_files.append(str(target_path.absolute()))
        elif target_path.is_dir():
            # Directory - recursively find index.tsx files
            for tsx_file in target_path.rglob("index.tsx"):
                # Skip node_modules
                if "node_modules" in str(tsx_file):
                    continue

                # Skip __stories__ directories
                if "__stories__" in str(tsx_file):
                    continue

                # Convert to relative path
                try:
                    rel_path = tsx_file.absolute().relative_to(cwd)
                    component_files.append(str(rel_path))
                except ValueError:
                    component_files.append(str(tsx_file.absolute()))

    return sorted(component_files)


def detect_layer(file_path: str) -> tuple[str, str] | None:
    """
    Detect atomic design layer from file path.

    Args:
        file_path: Path to component file

    Returns:
        Tuple of (component_type, layer) where component_type is 'atoms', 'molecules', or 'organisms'
        Returns None if layer cannot be detected
    """
    parts = Path(file_path).parts

    # Look for src/web/components/{layer}
    try:
        components_idx = parts.index("components")
        if components_idx + 1 < len(parts):
            layer = parts[components_idx + 1]
            # Validate known atomic design layers
            known_layers = {"atoms", "molecules", "organisms"}
            if layer in known_layers:
                return (layer, layer)
    except ValueError:
        pass

    return None


def build_file_metadata(files: list[str]) -> list[dict]:
    """
    Build metadata for each component file.

    Args:
        files: List of component file paths

    Returns:
        List of file metadata dicts
    """
    metadata = []
    for file_path in files:
        layer_info = detect_layer(file_path)
        if not layer_info:
            print(f"Warning: Could not detect layer for {file_path}, skipping")
            continue

        component_type, layer = layer_info
        parent_dir = Path(file_path).parent
        component_name = parent_dir.name

        # Story file path: ComponentName/__stories__/ComponentName.stories.tsx
        story_path = parent_dir / "__stories__" / f"{component_name}.stories.tsx"

        metadata.append(
            {
                "component_file": file_path,
                "story_file": str(story_path),
                "component_type": component_type,
                "layer": layer,
                "component_name": component_name,
            }
        )

    return metadata


def create_stories_directories(file_metadata: list[dict]) -> None:
    """
    Create __stories__ directories for all components.

    This pre-creates the directory structure so agents don't need to.

    Args:
        file_metadata: List of file metadata
    """
    print("\n[Setup] Creating __stories__ directories...")
    created_count = 0

    for meta in file_metadata:
        story_path = Path(meta["story_file"])
        stories_dir = story_path.parent

        if not stories_dir.exists():
            stories_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {stories_dir}")
            created_count += 1

    if created_count > 0:
        print(f"[Setup] Created {created_count} __stories__ directories")
    else:
        print("[Setup] All __stories__ directories already exist")


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
    # Expected format: "component_file=..., story_file=..., component_type=..., layer=..."
    component_file = ""
    story_file = ""
    component_type = ""
    layer = ""
    component_name = ""

    try:
        # Parse description to extract metadata
        for part in todo_description.split(", "):
            if "=" in part:
                key, value = part.split("=", 1)
                if key.strip() == "component_file":
                    component_file = value.strip()
                elif key.strip() == "story_file":
                    story_file = value.strip()
                elif key.strip() == "component_type":
                    component_type = value.strip()
                elif key.strip() == "layer":
                    layer = value.strip()
                elif key.strip() == "component_name":
                    component_name = value.strip()
    except Exception as e:
        print(f"[Execute] Warning: Failed to parse TODO description: {e}")
        print(f"[Execute] Description: {todo_description}")

    if not component_file or not layer:
        print("[Execute] Error: Could not extract component_file or layer from TODO")
        return False

    # Derive component_name if not provided
    if not component_name:
        component_name = Path(component_file).parent.name

    print(f"[Execute] Component: {component_file}")
    print(f"[Execute] Story: {story_file}")
    print(f"[Execute] Type: {component_type}")
    print(f"[Execute] Layer: {layer}")

    # Build references_persist list
    references = [component_file]

    # Build task instruction with proper formatting (no newlines that need escaping)
    task_instruction = (
        "🎯 CRITICAL MISSION: Implement comprehensive Storybook stories\n\n"
        "📋 Target Specification:\n"
        f"- Component target file: {component_file}\n"
        f"- Story output path: {story_file}\n"
        f"- Component type: {component_type}\n"
        f"- Atomic design layer: {layer}\n\n"
        "⚠️ ABSOLUTE REQUIREMENTS:\n"
        "1. Stories that fail to render have NO VALUE - ALL checks must pass\n"
        "2. Follow @procedures/typescript/tests/storybook_generation.md (all steps, no shortcuts)\n"
        "3. Story count: Follow ts_test_strategist recommendations (non-negotiable)\n"
        f"4. ONLY modify {story_file} - any other file changes = immediate abort\n"
        "5. The __stories__ directory already exists - DO NOT create it\n\n"
        "✅ Success Criteria:\n"
        "- [ ] TypeScript Compiler (tsc --noEmit): Pass\n"
        "- [ ] Validation Script (validate_code.sh): Pass\n"
        "- [ ] Story count matches ts_test_strategist recommendation\n\n"
        "🔧 Tool Execution Protocol:\n"
        "- **EXECUTE, DON'T DISPLAY:** Do NOT write tool calls in markdown text or code blocks\n"
        "- **IGNORE DOC FORMATTING:** Code blocks in procedures are illustrations only - convert them to actual tool invocations\n"
        "- **IMMEDIATE INVOCATION:** Your response must be tool use requests, not text descriptions\n"
        "- **NO PREAMBLE:** No 'I will now...', 'Okay...', 'Let me...' - invoke Step 1a tool immediately\n"
        "- **COMPLETE ALL STEPS:** Continue invoking tools through all steps until all checks pass"
    )

    # Build tasks array as proper Python structure (will be properly JSON-serialized)
    tasks = [
        {
            "type": "agent",
            "instruction": task_instruction,
            "roles": [
                "roles/typescript/tests/storybook.md",
                f"roles/typescript/components/{layer}.md",
            ],
            "references_persist": references,
            "procedure": "procedures/typescript/tests/storybook_generation.md",
        },
        {
            "type": "script",
            "script": "typescript/validate_code.sh",
            "args": ["--ignore-external-changes"],
            "max_retries": 2,
        },
    ]

    # Format tasks as readable JSON for the instruction
    tasks_json = json.dumps(tasks, indent=2, ensure_ascii=False)
    references_json = json.dumps(references, ensure_ascii=False)
    roles_json = json.dumps(
        [
            "roles/typescript/tests/storybook.md",
            f"roles/typescript/components/{layer}.md",
        ],
        ensure_ascii=False,
    )

    # Build comprehensive instruction with all necessary parameters
    instruction = f"""Process the next TODO item: {todo_title}

Component Details:
- Component file: {component_file}
- Story output: {story_file}
- Component type: {component_type}
- Layer: {layer}
- Component name: {component_name}

IMPORTANT: The __stories__ directory has already been created. DO NOT create it again.

Follow @procedures/typescript_storybook_conductor.md Step 3b-3c:

Step 3b: Construct task sequence (agent task + validation script)
Step 3c: Invoke invoke_serial_children tool with EXACTLY these parameters:

invoke_serial_children(
    roles={roles_json},
    references_persist={references_json},
    purpose="Generate Storybook stories for {component_name}",
    background="Complete ALL steps in storybook_generation.md for {component_file}. Verify TypeScript compilation, validation script, and Storybook visual rendering. DO NOT exit until all quality checks pass.",
    procedure="procedures/typescript/tests/storybook_generation.md",
    tasks={tasks_json}
)

After calling invoke_serial_children, EXIT IMMEDIATELY and wait for completion notification.

When you receive the completion notification:
- ✅ On success: Call get_sessions_final_turns with provided session IDs, then edit_todos to mark as completed
- ❌ On failure: Do NOT retry. Mark as failed with edit_todos and report error
- 🚨 On abort: Do NOT retry. Mark as aborted with edit_todos and report abort reason

CRITICAL RULES:
1. Call invoke_serial_children tool directly using the EXACT parameters shown above
2. Do NOT modify the JSON structures - use them as-is
3. NEVER call invoke_serial_children again to retry - retry logic is handled by invoke_serial_children itself
4. Follow the response instructions in the completion notification exactly
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
    print(f"\n[Conductor] Starting new session for {len(file_metadata)} components")

    takt_cmd = ["poetry", "run", "takt"]

    takt_cmd.extend(
        [
            "--purpose",
            f"Automated Storybook story generation for {len(file_metadata)} "
            "React components",
        ]
    )
    takt_cmd.extend(
        [
            "--background",
            "Orchestrate Storybook story generation by delegating to child agents "
            "via invoke_serial_children",
        ]
    )
    takt_cmd.extend(["--roles", "roles/conductor.md"])
    takt_cmd.extend(["--procedure", "procedures/typescript_storybook_conductor.md"])

    # Build initial instruction
    file_list = "\n".join(
        [
            f"- {m['component_file']} → {m['story_file']} (type: {m['component_type']}, layer: {m['layer']})"
            for m in file_metadata
        ]
    )

    instruction_template = (
        "Follow @procedures/typescript_storybook_conductor.md to generate Storybook stories "
        "for the following components:\n\n"
        "{file_list}\n\n"
        "Execute ONLY step 2:\n"
        "2. Create TODO list via edit_todos with all components listed above\n\n"
        "IMPORTANT: For each TODO, the description field MUST contain metadata in this format:\n"
        '  description: "component_file=<path>, story_file=<path>, component_type=<type>, layer=<layer>, component_name=<name>"\n\n'
        "Example (atom):\n"
        '  title: "Generate stories for Button"\n'
        '  description: "component_file=src/web/components/atoms/Button/index.tsx, '
        "story_file=src/web/components/atoms/Button/__stories__/Button.stories.tsx, "
        'component_type=atoms, layer=atoms, component_name=Button"\n\n'
        "Example (molecule):\n"
        '  title: "Generate stories for InputText"\n'
        '  description: "component_file=src/web/components/molecules/InputText/index.tsx, '
        "story_file=src/web/components/molecules/InputText/__stories__/InputText.stories.tsx, "
        'component_type=molecules, layer=molecules, component_name=InputText"\n\n'
        "Example (organism):\n"
        '  title: "Generate stories for Form"\n'
        '  description: "component_file=src/web/components/organisms/Form/index.tsx, '
        "story_file=src/web/components/organisms/Form/__stories__/Form.stories.tsx, "
        'component_type=organisms, layer=organisms, component_name=Form"\n\n'
        "After successfully creating TODOs with edit_todos, EXIT IMMEDIATELY.\n"
        "DO NOT process any components yet - the script will call you again "
        "to process each component one by one.\n\n"
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
                        break
                except json.JSONDecodeError:
                    print("[Conductor] Warning: Could not parse session ID from stdout")
                    continue

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
                            if (
                                candidate_id
                                and "Automated Storybook story generation" in purpose
                            ):
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

    except FileNotFoundError:
        print("Error: takt command not found. Is Poetry installed?")
        raise SystemExit(1)

    return session_id


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Storybook stories for React components"
    )
    parser.add_argument(
        "targets",
        nargs="+",
        help="Component files or directories to generate stories for",
    )
    parser.add_argument(
        "--session",
        "-s",
        help="Session ID to resume conductor session",
        default=None,
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
        help="Wait time between component processing (seconds, default: 120)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Automated Storybook Story Generation")
    print("=" * 70)
    print(f"Targets: {', '.join(args.targets)}")
    print(f"Timeout: {args.timeout}s per component")
    print(f"Wait between components: {args.wait}s")
    if args.session:
        print(f"Resume session: {args.session}")
    print("")

    # Find component files (only needed for new sessions)
    if not args.session:
        component_files = find_component_files(args.targets)
        print(f"[Scan] Found {len(component_files)} React component files")

        if not component_files:
            print("No component files found")
            sys.exit(0)

        # Build metadata
        file_metadata = build_file_metadata(component_files)

        if not file_metadata:
            print("No components with detectable layers found")
            sys.exit(0)

        print(f"[Scan] {len(file_metadata)} components have detectable layers:\n")
        for meta in file_metadata:
            print(f"  • {meta['component_file']}")
            print(
                f"    → {meta['story_file']} (type: {meta['component_type']}, layer: {meta['layer']})\n"
            )

        # Create __stories__ directories upfront
        create_stories_directories(file_metadata)
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
            print("✅ All components processed successfully!")
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
            print(f"\n[Wait] Sleeping {args.wait}s before processing next component...")
            time.sleep(args.wait)

    print("\n[Error] Maximum iterations reached")
    sys.exit(1)


if __name__ == "__main__":
    main()
