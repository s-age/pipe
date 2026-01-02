# Procedure: Python Unit Test Generation Conductor

## Purpose
Orchestrate automated test generation for multiple Python source files by delegating to child agents via `invoke_serial_children`.

## Applicability
Used by conductor agents managing batch test generation. Invoked via `scripts/python/tests/generate_unit_test.py` script.

---

## Step-by-Step Execution

### Step 1: Receive Target File List

**Input**: List of files from user instruction
**Actions**:
1. Parse file list from instruction
2. Identify layer for each file (repositories, services, models, etc.)
3. Determine test output path for each file

**Output**: Structured list of files to process

---

### Step 2: Create TODO List

**Actions**:
1. Use `edit_todos` tool
2. Create one TODO item per file:
   - Status: "pending"
   - Content: "Generate tests for {file_path}"

**Output**: TODO list initialized

---

### Step 3: Process Files Sequentially

For **each file** in the list, execute Steps 3a-3d:

#### Step 3a: Mark TODO as In Progress

**Actions**:
```python
edit_todos: Update current file status to "in_progress"
```

#### Step 3b: Construct Task Sequence

**Actions**:
Build task list with agent task and validation script:

```python
tasks = [
    {
        "type": "agent",
        "instruction": f"Follow @procedures/python_unit_test_generation.md to write tests. Target: {target_file_path}. Output: {test_output_path}. Execute all 7 steps sequentially. Coverage: 95%+.\n\nTool Usage Guidelines:\n- When using tools like py_analyze_code, py_test_strategist, etc., do not output the function call as text - just execute it.\n- If a tool needs to be called, call it directly without describing the call in your response.",
        "roles": [f"roles/python/tests/core/{layer}.md"],
        "procedure": "procedures/python_unit_test_generation.md",
        "references_persist": [target_file_path]
    },
    {
        "type": "script",
        "script": "python/validate_code.sh",
        "max_retries": 2  # Total 3 attempts (initial + 2 retries)
    }
]
```

**Notes**:
- Agent task properties: `roles`, `procedure`, `references_persist` specify takt parameters
- `artifacts` is optional - omit to allow factory file creation
- `max_retries=2` means 3 total attempts (1 initial + 2 retries)

#### Step 3c: Invoke Serial Children

**Actions**:
```python
invoke_serial_children(
    tasks=tasks,
    child_session_id=None,  # NEW session per file
    purpose=f"Generate tests for {filename}",
    background=f"Write comprehensive pytest tests for {target_file_path}",
    roles=[f"roles/python/tests/core/{layer}.md"],
    procedure="procedures/python_unit_test_generation.md",
    references_persist=[target_file_path]
)
```

**Notes**:
- `roles`, `procedure`, `references_persist` are specified at tool level
- These parameters are injected into agent tasks that don't already have them
- This ensures agents follow the correct procedure and role constraints

**Result**: Conductor exits immediately

#### Step 3d: Handle Serial Manager Response

**Actions** (when conductor resumes after `invoke_serial_children`):

The serial manager will send one of three types of messages:

##### Case 1: Success (✅)
**Message pattern**: "✅ Child agent tasks completed successfully"

**Actions**:
1. Call `get_sessions_final_turns` with provided session IDs to retrieve results
2. Use `edit_todos` to mark current file as "completed"
3. Move to next file

**Example**:
```python
# Receive: "✅ Child agent tasks completed successfully. Session IDs: [...]"
# Response:
get_sessions_final_turns(session_ids=[...])
edit_todos(status="completed" for current file)
# Continue to next file
```

##### Case 2: Normal Failure (❌)
**Message pattern**: "❌ Task execution FAILED" + "DO NOT retry or call invoke_serial_children again"

**Actions**:
1. **STOP immediately** - do NOT call `invoke_serial_children` again
2. Use `edit_todos` to mark current file as "failed"
3. Report error to user with details from the message
4. **Do NOT process remaining files** - stop the conductor

**Example**:
```python
# Receive: "❌ Task execution FAILED ... DO NOT retry ..."
# Response:
edit_todos(status="failed" for current file)
# Report to user: "Test generation failed for {file}. Error: {details}"
# STOP - do not continue to next file
```

##### Case 3: Permanent Failure (🚨)
**Message pattern**: "🚨 Task execution ABORTED (exit code 2 - permanent failure)" + "DO NOT retry"

**Actions**:
1. **STOP immediately** - do NOT call `invoke_serial_children` again
2. Use `edit_todos` to mark current file as "aborted"
3. Report abort reason to user (e.g., unauthorized file modifications)
4. **Do NOT process remaining files** - stop the conductor

**Example**:
```python
# Receive: "🚨 Task execution ABORTED ... DO NOT retry ..."
# Response:
edit_todos(status="aborted" for current file)
# Report to user: "Test generation aborted for {file}. Reason: {abort_reason}"
# STOP - manual investigation required
```

**Critical Rule**:
- **NEVER** call `invoke_serial_children` again if the message contains "DO NOT retry"
- Failures (❌ or 🚨) require stopping the conductor and reporting to the user
- Only on success (✅) should processing continue to the next file

---

### Step 4: Report Final Summary

**Actions**:
1. Count completed files
2. List generated test files
3. Report to user:
```
✅ Test generation complete

Summary:
- Files processed: {count}
- Tests generated: {list_of_test_files}
- All quality gates passed
```

**Output**: Final report

---

## Constraints (Must Not)

- ❌ Never write test code directly
- ❌ Never run quality commands directly
- ❌ Never reuse child sessions (create new session per file)
- ❌ Never wait after `invoke_serial_children` (exit immediately)
- ❌ Never skip TODO updates
- ❌ **CRITICAL**: Never retry `invoke_serial_children` when receiving "DO NOT retry" message
- ❌ **CRITICAL**: Never continue to next file after receiving failure (❌) or abort (🚨) messages

---

## Tool Usage

### Primary Tools
1. **edit_todos**: Create and update TODO list
2. **invoke_serial_children**: Delegate test generation + validation

### Task Structure
```python
# Agent task: Write tests
{
    "type": "agent",
    "instruction": "<detailed instruction with procedure reference>"
}

# Script task: Validate quality (with retry)
{
    "type": "script",
    "script": "python/validate_code.sh",
    "max_retries": 2  # Optional: retry on failure (default: 0)
}
```

**Retry Behavior**:
- `max_retries=0`: No retry (default), fails immediately
- `max_retries=2`: Retry up to 2 times (3 total attempts)
- Serial manager handles retries automatically by:
  1. Finding the preceding agent task
  2. Re-executing the agent with error information from failed script
  3. Re-executing the script task
  4. Repeating up to max_retries times
- Conductor only sees final result (success or failure)

**Exit Code 2 - ABORT (Permanent Failure)**:
- Scripts can exit with code 2 to signal a permanent failure that should NOT be retried
- Serial manager immediately aborts without retries, regardless of `max_retries` setting
- Use cases for exit code 2:
  - Unauthorized file modifications detected (e.g., changes outside `tests/`)
  - Validation failures requiring manual investigation
  - Configuration issues that cannot be auto-fixed
- The abort reason is automatically reported to the parent session for investigation

---

## Example Execution

```
Input:
  - src/pipe/core/repositories/archive_repository.py
  - src/pipe/core/repositories/session_repository.py

Step 1: Parse files, identify layer=repositories
Step 2: edit_todos (2 pending items)

Step 3 (File 1):
  3a: edit_todos (archive_repository → in_progress)
  3b: Construct instruction + tasks
  3c: invoke_serial_children (NEW session)
  [Conductor exits]
  [Child agent executes]
  [Script validates]
  [Conductor resumes]
  3d: edit_todos (archive_repository → completed)

Step 3 (File 2):
  3a: edit_todos (session_repository → in_progress)
  3b: Construct instruction + tasks
  3c: invoke_serial_children (NEW session)
  [Repeat]

Step 4: Report summary (2 files, 2 tests)
```

---

## Notes

- **One session per file**: Prevents context window bloat
- **Sequential processing**: One file at a time
- **No waiting**: Conductor exits after delegation
- **Error handling**: Script task detects failures
- **Resumable**: Can restart from TODO list
