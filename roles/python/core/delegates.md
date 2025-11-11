# Delegates Layer

## Purpose

Delegates are **high-level workflow orchestrators**. When the dispatcher receives a command, it hands control to a delegate, which orchestrates the entire workflow by coordinating services, agents, and other components.

## Responsibilities

1. **Command Execution** - Execute high-level commands (run, fork, help, etc.)
2. **Workflow Orchestration** - Coordinate multiple services and agents
3. **User Interaction** - Handle CLI output and user feedback
4. **Error Handling** - Catch and report errors to users
5. **Entry Point Logic** - Bridge between CLI and core logic

## Characteristics

- ✅ High-level workflow coordination
- ✅ Call multiple services and agents
- ✅ Handle user-facing output
- ✅ Error reporting and logging
- ❌ **NO low-level logic** - delegate to services/domains
- ❌ **NO direct file I/O** - use repositories via services
- ❌ **NO business logic** - orchestrate, don't implement

## File Structure

```
delegates/
├── gemini_api_delegate.py    # Gemini API workflow
├── gemini_cli_delegate.py    # Gemini CLI workflow
├── fork_delegate.py           # Session forking
├── dry_run_delegate.py        # Dry run mode
└── help_delegate.py           # Help display
```

## Dependencies

**Allowed:**

- ✅ `services/` - Coordinate services
- ✅ `agents/` - Call agents for AI interactions
- ✅ `models/` - For type definitions
- ✅ `utils/` - For utilities

**Forbidden:**

- ❌ `repositories/` - Access via services only
- ❌ `domains/` - Use via services
- ❌ `collections/` - Access via services/models

## Template

```python
"""
Delegate for [command/workflow].
"""

import logging
import sys
from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService
from pipe.core.models.args import TaktArgs

logger = logging.getLogger(__name__)


def execute_workflow(
    session_service: SessionService,
    prompt_service: PromptService,
    args: TaktArgs,
    project_root: str,
) -> None:
    """
    Executes [workflow name].

    This delegate:
    1. Validates inputs
    2. Coordinates services
    3. Handles errors
    4. Reports results

    Args:
        session_service: Service for session management
        prompt_service: Service for prompt construction
        args: Parsed command-line arguments
        project_root: Path to project root
    """
    try:
        logger.info("Starting workflow")

        # Step 1: Validate inputs
        if not args.session_id:
            print("Error: Session ID is required", file=sys.stderr)
            return

        # Step 2: Orchestrate services
        session = session_service.load_session(args.session_id)
        prompt = prompt_service.build_prompt(session.id)

        # Step 3: Execute main workflow
        _execute_main_logic(session, prompt)

        # Step 4: Report success
        print(f"✓ Workflow completed successfully")
        logger.info("Workflow completed")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def _execute_main_logic(session, prompt):
    """
    Internal workflow logic.

    Private helper functions encapsulate workflow steps.
    """
    # Workflow implementation
    pass
```

## Real Examples

### gemini_api_delegate.py - Gemini API Workflow

**Key Responsibilities:**

- Orchestrate complete AI interaction workflow
- Coordinate session, prompt, and agent services
- Handle tool execution loop
- Manage conversation state

```python
"""
Delegate for Gemini API workflow.
"""

import logging
import sys
from pipe.core.agents.gemini_api import call_gemini_api
from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings

logger = logging.getLogger(__name__)


def run_gemini_api_workflow(
    session_service: SessionService,
    prompt_service: PromptService,
    args: TaktArgs,
    settings: Settings,
    project_root: str,
) -> None:
    """
    Executes Gemini API workflow.

    Workflow:
    1. Load or create session
    2. Add user instruction as turn
    3. Call Gemini API (agent handles this)
    4. Process response and tool calls
    5. Save session state
    """
    try:
        logger.info("Starting Gemini API workflow")

        # Step 1: Get or create session
        if args.session_id:
            session_id = args.session_id
            session_service.load_session(session_id)
        else:
            session_id = session_service.start_session(
                purpose=args.purpose,
                background=args.background,
                roles=args.roles,
                parent_id=args.parent_id,
            )

        # Step 2: Add user instruction
        session_service.set_current_instruction(args.instruction)

        # Step 3: Call agent (agent handles API interaction)
        call_gemini_api(
            session_service=session_service,
            prompt_service=prompt_service,
            session_id=session_id,
            model_name=settings.default_model,
            settings=settings,
            project_root=project_root,
        )

        # Step 4: Report completion
        print(f"\n✓ Session {session_id[:8]}... completed")
        print(f"  View: takt --session {session_id}")

        logger.info(f"Workflow completed for session {session_id}")

    except KeyboardInterrupt:
        print("\n✗ Workflow interrupted by user", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
```

### fork_delegate.py - Session Forking Workflow

```python
"""
Delegate for session forking workflow.
"""

import logging
import sys
from pipe.core.services.session_service import SessionService
from pipe.core.models.args import TaktArgs

logger = logging.getLogger(__name__)


def fork_session_workflow(
    session_service: SessionService,
    args: TaktArgs,
) -> None:
    """
    Executes session forking workflow.

    Workflow:
    1. Validate source session exists
    2. Validate turn index
    3. Fork session via service
    4. Report new session ID
    """
    try:
        logger.info(f"Forking session {args.fork} at turn {args.at_turn}")

        # Validate inputs
        if not args.fork:
            raise ValueError("Source session ID required for fork")

        if args.at_turn is None:
            raise ValueError("Turn index required for fork (--at-turn)")

        # Fork session (service handles the logic)
        new_session_id = session_service.fork_session(
            source_session_id=args.fork,
            at_turn_index=args.at_turn,
        )

        # Report success
        print(f"✓ Session forked successfully")
        print(f"  Source: {args.fork[:8]}...")
        print(f"  New:    {new_session_id[:8]}...")
        print(f"  Fork point: Turn {args.at_turn}")
        print(f"\n  Continue: takt --session {new_session_id} --instruction '...'")

        logger.info(f"Fork completed: {new_session_id}")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        logger.error(f"Fork failed: {e}", exc_info=True)
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
```

### help_delegate.py - Help Display

```python
"""
Delegate for displaying help information.
"""

import sys


def show_help() -> None:
    """
    Displays help information.

    This is a simple delegate that just formats and displays help.
    """
    help_text = """
takt - AI-powered conversation management

USAGE:
    takt [OPTIONS]

NEW SESSION:
    takt --purpose "Goal" --background "Context" --instruction "Task"

CONTINUE SESSION:
    takt --session <ID> --instruction "Next task"

FORK SESSION:
    takt --fork <ID> --at-turn <N>

OPTIONS:
    --session <ID>              Continue existing session
    --purpose <TEXT>            Purpose for new session
    --background <TEXT>         Background for new session
    --instruction <TEXT>        Current task instruction
    --roles <PATH>,<PATH>       Role definition files
    --references <PATH>,<PATH>  File references
    --fork <ID>                 Fork session ID
    --at-turn <N>              Turn index for fork
    --help                      Show this help

EXAMPLES:
    # Start new session
    takt --purpose "Build CLI" --background "Python tool" --instruction "Design models"

    # Continue session
    takt --session abc123... --instruction "Implement the design"

    # Fork at turn 5
    takt --fork abc123... --at-turn 5
"""
    print(help_text)
```

### dry_run_delegate.py - Dry Run Mode

```python
"""
Delegate for dry run mode (shows what would be executed).
"""

import logging
from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService
from pipe.core.models.args import TaktArgs

logger = logging.getLogger(__name__)


def dry_run_workflow(
    session_service: SessionService,
    prompt_service: PromptService,
    args: TaktArgs,
) -> None:
    """
    Shows what would be executed without actually running.

    Useful for debugging and understanding workflows.
    """
    print("=== DRY RUN MODE ===\n")

    # Show what would happen
    if args.session_id:
        print(f"Would continue session: {args.session_id}")
        session = session_service.load_session(args.session_id)
        print(f"  Purpose: {session.purpose}")
        print(f"  Turns: {len(session.turns)}")
    else:
        print("Would create new session:")
        print(f"  Purpose: {args.purpose}")
        print(f"  Background: {args.background}")

    print(f"\nWould add instruction:")
    print(f"  {args.instruction}")

    if args.references:
        print(f"\nWould add references:")
        for ref in args.references:
            print(f"  - {ref}")

    print("\n=== END DRY RUN ===")
```

## Delegate Patterns

### Pattern 1: Multi-Step Workflow with Rollback

```python
def execute_with_rollback(
    session_service: SessionService,
    args: TaktArgs,
) -> None:
    """
    Executes workflow with rollback on error.
    """
    original_state = None

    try:
        # Save state for rollback
        session = session_service.load_session(args.session_id)
        original_state = session.model_copy()

        # Execute workflow steps
        step1_result = _execute_step1(session_service)
        step2_result = _execute_step2(session_service, step1_result)
        step3_result = _execute_step3(session_service, step2_result)

        # Commit changes
        session_service.save_current_session()
        print("✓ Workflow completed")

    except Exception as e:
        # Rollback on error
        if original_state:
            logger.warning("Rolling back changes")
            session_service.save_session(original_state)

        print(f"✗ Error (changes rolled back): {e}", file=sys.stderr)
        sys.exit(1)
```

### Pattern 2: Progress Reporting

```python
def execute_with_progress(
    session_service: SessionService,
    steps: list[str],
) -> None:
    """
    Executes workflow with progress reporting.
    """
    total_steps = len(steps)

    for i, step in enumerate(steps, 1):
        print(f"[{i}/{total_steps}] {step}...", end=" ", flush=True)

        try:
            _execute_step(session_service, step)
            print("✓")
        except Exception as e:
            print(f"✗ {e}")
            sys.exit(1)

    print(f"\n✓ All {total_steps} steps completed")
```

### Pattern 3: Confirmation Prompt

```python
def execute_with_confirmation(
    session_service: SessionService,
    action: str,
) -> None:
    """
    Executes workflow with user confirmation.
    """
    # Show what will happen
    print(f"About to {action}")
    print("This will:")
    print("  - Modify session state")
    print("  - Create backup")
    print("  - Call external API")

    # Ask for confirmation
    response = input("\nProceed? [y/N]: ")

    if response.lower() != 'y':
        print("Cancelled")
        return

    # Execute
    _execute_action(session_service)
    print("✓ Completed")
```

## Testing

### Unit Testing Delegates

```python
# tests/core/delegates/test_gemini_api_delegate.py
from unittest.mock import Mock, patch
import pytest

def test_gemini_api_workflow_success():
    # Setup mocks
    mock_session_service = Mock()
    mock_prompt_service = Mock()
    mock_settings = Mock(default_model="gemini-2.0-flash")

    mock_session_service.start_session.return_value = "test123"

    args = Mock(
        session_id=None,
        purpose="Test",
        background="Testing",
        instruction="Test task",
        roles=None,
        parent_id=None,
    )

    # Execute (mock the agent call)
    with patch('pipe.core.delegates.gemini_api_delegate.call_gemini_api'):
        run_gemini_api_workflow(
            mock_session_service,
            mock_prompt_service,
            args,
            mock_settings,
            "/test",
        )

    # Verify workflow steps
    mock_session_service.start_session.assert_called_once()
    mock_session_service.set_current_instruction.assert_called_once()


def test_fork_workflow_missing_turn_index():
    mock_service = Mock()
    args = Mock(fork="test123", at_turn=None)

    with pytest.raises(SystemExit):
        fork_session_workflow(mock_service, args)
```

## Best Practices

### 1. Keep Delegates Thin

```python
# ✅ GOOD: Delegate orchestrates, doesn't implement
def run_workflow(services, args):
    session = services.session.load(args.session_id)  # Service handles this
    prompt = services.prompt.build(session.id)  # Service handles this
    services.agent.call(prompt)  # Agent handles this

# ❌ BAD: Delegate contains implementation
def run_workflow(services, args):
    # Complex logic here...
    session_data = read_json(f"{args.session_id}.json")
    # More implementation...
```

### 2. Handle Errors at the Top Level

```python
# ✅ GOOD: Delegate catches and reports all errors
def run_workflow(services, args):
    try:
        _execute_workflow(services, args)
    except ValueError as e:
        print(f"✗ Validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

# ❌ BAD: Let errors propagate
def run_workflow(services, args):
    _execute_workflow(services, args)  # Errors not handled
```

### 3. Provide Clear User Feedback

```python
# ✅ GOOD: Clear, actionable feedback
print("✓ Session created: abc123...")
print("  Continue with: takt --session abc123... --instruction '...'")

# ❌ BAD: Vague feedback
print("Done")
```

### 4. Log for Debugging

```python
# ✅ GOOD: Log workflow steps
logger.info("Starting workflow")
logger.debug(f"Session ID: {session_id}")
logger.info("Workflow completed")

# ❌ BAD: No logging
# (No logs means no debugging info)
```

## Summary

Delegates are the **orchestration layer**:

- ✅ High-level workflow coordination
- ✅ User-facing entry points
- ✅ Error handling and reporting
- ✅ Progress feedback
- ❌ No implementation details
- ❌ No business logic
- ❌ No direct persistence

Delegates conduct the symphony, while services play the instruments.
