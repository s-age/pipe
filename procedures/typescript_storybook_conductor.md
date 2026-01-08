# Procedure: TypeScript Storybook Generation Conductor

## Purpose
Orchestrate automated Storybook story generation for multiple React components by delegating to child agents via `invoke_serial_children`.

## Applicability
Used by conductor agents managing batch story generation. Invoked via `scripts/typescript/tests/generate_storybook.py` script.

---

## Workflow Diagram

```mermaid
graph TD
    Start([Start: Receive component list]) --> Step1[Step 1: Parse component metadata]
    Step1 --> Step2[Step 2: Create TODO list via edit_todos]
    Step2 --> Step3A[Step 3a: Mark TODO as in progress]

    Step3A --> Step3B[Step 3b: Construct task sequence]
    Step3B --> Step3C[Step 3c: invoke_serial_children]

    Step3C --> Exit1[Conductor EXITS]
    Exit1 -.->|Serial manager executes| Agent[Child agent writes stories]
    Agent --> Script[Validation script runs]
    Script -.->|Completion notification| Resume[Conductor RESUMES]

    Resume --> Step3D{Step 3d: Check response type}

    Step3D -->|✅ Success| Success[Get results + Mark completed]
    Step3D -->|❌ Failure| Failure[Mark failed + STOP]
    Step3D -->|🚨 Abort| Abort[Mark aborted + STOP]

    Success --> HasMore{More TODOs?}
    HasMore -->|Yes| Step3A
    HasMore -->|No| Step4[Step 4: Report summary]

    Failure --> End([END: Report error])
    Abort --> End
    Step4 --> End

    style Start fill:#e1f5e1
    style Exit1 fill:#fff4e1
    style Resume fill:#e1f0ff
    style Success fill:#ccffcc
    style Failure fill:#ffcccc
    style Abort fill:#ff9999
    style End fill:#e1f5e1
    style Step3D fill:#ffe1f0
```

**Key Points**:
- Conductor EXITS immediately after calling `invoke_serial_children`
- Serial manager executes child tasks and sends completion notification
- Conductor RESUMES only when receiving notification
- **CRITICAL**: On failure (❌) or abort (🚨), conductor STOPS and reports error
- **CRITICAL**: Conductor NEVER calls `invoke_serial_children` again on failure

---

## Step-by-Step Execution

### Step 1: Receive Component List

**Input**: List of components from user instruction with metadata:
- `component_file`: Source component path (e.g., `src/web/components/atoms/Button/index.tsx`)
- `story_file`: Target story path (e.g., `src/web/components/atoms/Button/__stories__/Button.stories.tsx`)
- `component_type`: Atomic design type (`atoms`, `molecules`, `organisms`)
- `layer`: Component layer (`atoms`, `molecules`, `organisms`)
- `component_name`: Component name (e.g., `Button`)

**Actions**:
1. Parse component list from instruction
2. Validate metadata completeness
3. Identify layer for each component

**Output**: Structured list of components to process

---

### Step 2: Create TODO List

**Actions**:
1. Use `edit_todos` tool
2. Create one TODO item per component:
   - Title: `"Generate stories for {component_name}"`
   - Description: `"component_file={path}, story_file={path}, component_type={type}, layer={layer}, component_name={name}"`
   - Status: Not specified (defaults to unchecked)

**Example**:
```python
edit_todos([
    {
        "title": "Generate stories for Button",
        "description": "component_file=src/web/components/atoms/Button/index.tsx, story_file=src/web/components/atoms/Button/__stories__/Button.stories.tsx, component_type=atoms, layer=atoms, component_name=Button"
    }
])
```

**Output**: TODO list initialized

---

### Step 3: Process Components Sequentially

For **each component** in the list, execute Steps 3a-3d:

#### Step 3a: Receive Next TODO Instruction

**Actions**: The orchestration script sends a detailed instruction containing:
- Component metadata (file paths, layer, name)
- Fully constructed `invoke_serial_children` parameters
- Explicit instruction to call the tool and exit

**Important**: This instruction comes from the external script, not from the conductor itself.

#### Step 3b: Construct Task Sequence

**Actions**: Build task list with agent task and validation script:

```python
tasks = [
    {
        "type": "agent",
        "instruction": f"""🎯 CRITICAL MISSION: Implement comprehensive Storybook stories

📋 Target Specification:
- Component target file: {component_file}
- Story output path: {story_file}
- Component type: {component_type}
- Atomic design layer: {layer}

⚠️ ABSOLUTE REQUIREMENTS:
1. Stories that fail to render have NO VALUE - ALL checks must pass
2. Follow @procedures/typescript/tests/storybook_generation.md (all steps, no shortcuts)
3. Story count: Follow ts_test_strategist recommendations (non-negotiable)
4. ONLY modify {story_file} - any other file changes = immediate abort
5. The __stories__ directory already exists - DO NOT create it

✅ Success Criteria:
- [ ] TypeScript Compiler (tsc --noEmit): Pass
- [ ] Validation Script (validate_code.sh): Pass
- [ ] Story count matches ts_test_strategist recommendation

🔧 Tool Execution Protocol:
- **EXECUTE, DON'T DISPLAY:** Do NOT write tool calls in markdown text or code blocks
- **IGNORE DOC FORMATTING:** Code blocks in procedures are illustrations only - convert them to actual tool invocations
- **IMMEDIATE INVOCATION:** Your response must be tool use requests, not text descriptions
- **NO PREAMBLE:** No 'I will now...', 'Okay...', 'Let me...' - invoke Step 1a tool immediately
- **COMPLETE ALL STEPS:** Continue invoking tools through all steps until all checks pass""",
        "roles": [
            "roles/typescript/tests/storybook.md",
            f"roles/typescript/components/{layer}.md"
        ],
        "procedure": "procedures/typescript/tests/storybook_generation.md",
        "references_persist": [component_file]
    },
    {
        "type": "script",
        "script": "typescript/validate_code.sh",
        "args": ["--ignore-external-changes"],
        "max_retries": 2  # Total 3 attempts (initial + 2 retries)
    }
]
```

**Notes**:
- Agent task includes roles for both storybook testing and component layer
- `references_persist` ensures component source is available without re-reading
- `max_retries=2` means 3 total attempts (1 initial + 2 retries)
- Validation script uses `--ignore-external-changes` flag

#### Step 3c: Invoke Serial Children

**Actions**:
```python
invoke_serial_children(
    tasks=tasks,
    purpose=f"Generate Storybook stories for {component_name}",
    background=f"Complete ALL steps in storybook_generation.md for {component_file}. Verify TypeScript compilation, validation script, and Storybook visual rendering. DO NOT exit until all quality checks pass.",
    roles=[
        "roles/typescript/tests/storybook.md",
        f"roles/typescript/components/{layer}.md"
    ],
    procedure="procedures/typescript/tests/storybook_generation.md",
    references_persist=[component_file]
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
2. Use `edit_todos` to mark current component as completed (checked: true)
3. Move to next component

**Example**:
```python
# Receive: "✅ Child agent tasks completed successfully. To retrieve the results, use get_sessions_final_turns with the following session IDs: [...]"
# Response:
get_sessions_final_turns(session_ids=[...])
edit_todos([{
    "title": "Generate stories for Button",
    "description": "...",
    "checked": true
}])
# Continue to next component
```

##### Case 2: Normal Failure (❌)
**Message pattern**: "❌ Task execution FAILED" + "DO NOT retry or call invoke_serial_children again"

**Actions**:
1. **STOP immediately** - do NOT call `invoke_serial_children` again
2. Use `edit_todos` to mark current component as failed
3. Report error to user with details from the message
4. **Do NOT process remaining components** - stop the conductor

**Example**:
```python
# Receive: "❌ Task execution FAILED ... DO NOT retry ..."
# Response:
edit_todos([{
    "title": "Generate stories for Button",
    "description": "...",
    "checked": false,
    "note": "Failed: {error_details}"
}])
# Report to user: "Story generation failed for {component}. Error: {details}"
# STOP - do not continue to next component
```

##### Case 3: Permanent Failure (🚨)
**Message pattern**: "🚨 Task execution ABORTED (exit code 2 - permanent failure)" + "DO NOT retry"

**Actions**:
1. **STOP immediately** - do NOT call `invoke_serial_children` again
2. Use `edit_todos` to mark current component as aborted
3. Report abort reason to user (e.g., unauthorized file modifications)
4. **Do NOT process remaining components** - stop the conductor

**Example**:
```python
# Receive: "🚨 Task execution ABORTED ... DO NOT retry ..."
# Response:
edit_todos([{
    "title": "Generate stories for Button",
    "description": "...",
    "checked": false,
    "note": "Aborted: {abort_reason}"
}])
# Report to user: "Story generation aborted for {component}. Reason: {abort_reason}"
# STOP - manual investigation required
```

**Critical Rule**:
- **NEVER** call `invoke_serial_children` again if the message contains "DO NOT retry"
- **NEVER** call `invoke_serial_children` again on your own initiative to "retry"
- Failures (❌ or 🚨) require stopping the conductor and reporting to the user
- Only on success (✅) should processing continue to the next component
- **Retry logic is the responsibility of `invoke_serial_children` and its `max_retries` configuration**

---

### Step 4: Report Final Summary

**Actions**:
1. Count completed components
2. List generated story files
3. Report to user:
```
✅ Storybook story generation complete

Summary:
- Components processed: {count}
- Stories generated: {list_of_story_files}
- All quality gates passed
```

**Output**: Final report

---

## Constraints (Must Not)

### Conductor Responsibilities
- ❌ **ABSOLUTE PROHIBITION**: Never write story code directly
- ❌ **ABSOLUTE PROHIBITION**: Never run TypeScript compiler or validation commands directly
- ❌ **ABSOLUTE PROHIBITION**: Never call `invoke_serial_children` more than once per component
- ❌ **CRITICAL**: Never retry `invoke_serial_children` when receiving "DO NOT retry" message
- ❌ **CRITICAL**: Never continue to next component after receiving failure (❌) or abort (🚨) messages
- ❌ Never reuse child sessions (create new session per component via script orchestration)
- ❌ Never wait after `invoke_serial_children` (exit immediately)
- ❌ Never skip TODO updates

### Rationale
- **Retry logic is handled by `invoke_serial_children`**: The `max_retries` configuration for script tasks handles automatic retries
- **Conductor-level retries waste tokens**: Re-launching child agents duplicates work already done by the retry mechanism
- **Single responsibility**: Conductor orchestrates, child agents execute, serial manager handles retries

---

## Tool Usage

### Primary Tools
1. **edit_todos**: Create and update TODO list
2. **invoke_serial_children**: Delegate story generation + validation
3. **get_sessions_final_turns**: Retrieve results from completed child sessions

### Task Structure
```python
# Agent task: Write stories
{
    "type": "agent",
    "instruction": "<detailed instruction with procedure reference>",
    "roles": [
        "roles/typescript/tests/storybook.md",
        "roles/typescript/components/{layer}.md"
    ],
    "procedure": "procedures/typescript/tests/storybook_generation.md",
    "references_persist": [component_file]
}

# Script task: Validate quality (with retry)
{
    "type": "script",
    "script": "typescript/validate_code.sh",
    "args": ["--ignore-external-changes"],
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
  - Unauthorized file modifications detected (e.g., changes outside story file)
  - Validation failures requiring manual investigation
  - Configuration issues that cannot be auto-fixed
- The abort reason is automatically reported to the parent session for investigation

---

## Example Execution

```
Input:
  - src/web/components/atoms/Button/index.tsx
  - src/web/components/atoms/Icon/index.tsx

Step 1: Parse components, identify layer=atoms
Step 2: edit_todos (2 unchecked items)

Step 3 (Component 1):
  3a: Receive instruction from script
  3b: Construct instruction + tasks
  3c: invoke_serial_children (NEW session)
  [Conductor exits]
  [Child agent executes]
  [Script validates]
  [Conductor resumes]
  3d: get_sessions_final_turns + edit_todos (Button → completed)

Step 3 (Component 2):
  3a: Receive instruction from script
  3b: Construct instruction + tasks
  3c: invoke_serial_children (NEW session)
  [Repeat]

Step 4: Report summary (2 components, 2 story files)
```

---

## Notes

- **One session per component**: Prevents context window bloat
- **Sequential processing**: One component at a time
- **No waiting**: Conductor exits after delegation
- **Error handling**: Script task detects failures with `max_retries`
- **Resumable**: Can restart from TODO list
- **Layer-specific roles**: Each component gets appropriate layer role (atoms, molecules, organisms)
- **Pre-created directories**: The `__stories__` directory is created by the orchestration script before conductor runs
