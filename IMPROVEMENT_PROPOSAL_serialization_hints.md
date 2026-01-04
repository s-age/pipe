# Improvement Proposal: Better Utilization of `serialization_hints` from `py_test_strategist`

## Problem Statement

Based on failure analysis, agents frequently confuse CamelCase and snake_case when writing test assertions, despite `py_test_strategist` providing `serialization_hints`. This causes:

1. **KeyError failures**: Expecting `totalTasks` (camelCase) but getting `total_tasks` (snake_case)
2. **Wasted iterations**: ~38+ turns spent debugging case mismatches
3. **Ignored hints**: Agents don't fully leverage the `serialization_hints` data structure

### Root Cause

The current instruction template in `scripts/python/tests/generate_unit_test.py` (line 512) doesn't explicitly mention or emphasize serialization_hints from py_test_strategist output.

## Proposed Solution

### 1. Enhance py_test_strategist Output Visibility

**Current behavior:**
- `serialization_hints` are generated but only shown in JSON output
- No explicit reminder in the instruction to check these hints

**Proposed change:**

Add explicit reference to serialization hints in the instruction template (line 512):

```python
# BEFORE (line 512):
"instruction": "🎯 CRITICAL MISSION: Implement comprehensive pytest tests\\n\\n📋 Target Specification:\\n- Test target file: {source_file}\\n- Test output path: {test_file}\\n- Architecture layer: {layer}\\n\\n⚠️ ABSOLUTE REQUIREMENTS:\\n1. Tests that fail have NO VALUE - ALL checks must pass\\n2. Follow @procedures/python_unit_test_generation.md (all 7 steps, no shortcuts)\\n3. Coverage target: 95%+ (non-negotiable)\\n4. ONLY modify {test_file} - any other file changes = immediate abort\\n\\n✅ Success Criteria (Test Execution Report):\\n- [ ] Linter (Ruff/Format): Pass\\n- [ ] Type Check (MyPy): Pass\\n- [ ] Test Result (Pytest): Pass (0 failures)\\n- [ ] Coverage: 95%+ achieved\\n\\nRefer to @roles/python/tests/tests.md 'Test Execution Report' section for the required checklist format.\\n\\n🔧 Tool Execution Protocol:\\n- **EXECUTE, DON'T DISPLAY:** Do NOT write tool calls in markdown text or code blocks\\n- **IGNORE DOC FORMATTING:** Code blocks in procedures are illustrations only - convert them to actual tool invocations\\n- **IMMEDIATE INVOCATION:** Your response must be tool use requests, not text descriptions\\n- **NO PREAMBLE:** No 'I will now...', 'Okay...', 'Let me...' - invoke Step 1a tool immediately\\n- **COMPLETE ALL 7 STEPS:** Continue invoking tools through all steps until Test Execution Report is done",

# AFTER (with serialization hints emphasis):
"instruction": "🎯 CRITICAL MISSION: Implement comprehensive pytest tests\\n\\n📋 Target Specification:\\n- Test target file: {source_file}\\n- Test output path: {test_file}\\n- Architecture layer: {layer}\\n\\n⚠️ ABSOLUTE REQUIREMENTS:\\n1. Tests that fail have NO VALUE - ALL checks must pass\\n2. Follow @procedures/python_unit_test_generation.md (all 7 steps, no shortcuts)\\n3. Coverage target: 95%+ (non-negotiable)\\n4. ONLY modify {test_file} - any other file changes = immediate abort\\n\\n🔑 CRITICAL - SERIALIZATION CASE HANDLING:\\n- Step 1a (py_test_strategist) provides serialization_hints for data models\\n- ALWAYS check serialization_hints BEFORE writing assertions\\n- CamelCaseModel: model_dump() → snake_case, model_dump(by_alias=True) → camelCase\\n- BaseModel: model_dump() → snake_case only\\n- VERIFY which format the production code uses before asserting\\n- Common mistake: Assuming camelCase when code uses snake_case (or vice versa)\\n\\n✅ Success Criteria (Test Execution Report):\\n- [ ] Linter (Ruff/Format): Pass\\n- [ ] Type Check (MyPy): Pass\\n- [ ] Test Result (Pytest): Pass (0 failures)\\n- [ ] Coverage: 95%+ achieved\\n\\nRefer to @roles/python/tests/tests.md 'Test Execution Report' section for the required checklist format.\\n\\n🔧 Tool Execution Protocol:\\n- **EXECUTE, DON'T DISPLAY:** Do NOT write tool calls in markdown text or code blocks\\n- **IGNORE DOC FORMATTING:** Code blocks in procedures are illustrations only - convert them to actual tool invocations\\n- **IMMEDIATE INVOCATION:** Your response must be tool use requests, not text descriptions\\n- **NO PREAMBLE:** No 'I will now...', 'Okay...', 'Let me...' - invoke Step 1a tool immediately\\n- **COMPLETE ALL 7 STEPS:** Continue invoking tools through all steps until Test Execution Report is done",
```

### 2. Enhance py_test_strategist to Analyze All Models in File

**Current limitation:**
- `serialization_hints` only generated for models referenced in `mock_candidates`
- Models defined in the target file itself are often missed

**Proposed enhancement in `src/pipe/core/tools/py_test_strategist.py`:**

Add new section after line 691 to analyze models defined in the target file:

```python
# 6.1. Analyze serialization behavior for each data model
serialization_hints: list[SerializationHint] = []
for model_name, import_stmt in data_models.items():
    hint = _analyze_model_base_class(model_name, import_stmt)
    if hint:
        serialization_hints.append(hint)

# 6.2. ENHANCEMENT: Analyze models defined in the target file itself
# This catches CamelCaseModel/BaseModel subclasses that aren't in mock_candidates
try:
    source_code = repo.read_text(target_file_path)
    tree = ast.parse(source_code)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if class inherits from CamelCaseModel or BaseModel
            for base in node.bases:
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr

                if base_name in ("CamelCaseModel", "BaseModel"):
                    # Generate hint for this model
                    model_name = node.name

                    # Check if we already have a hint for this model
                    if not any(h.model_name == model_name for h in serialization_hints):
                        if base_name == "CamelCaseModel":
                            serialization_hints.append(
                                SerializationHint(
                                    model_name=model_name,
                                    base_class="CamelCaseModel",
                                    serialization_notes=(
                                        f"{model_name} inherits from CamelCaseModel. "
                                        "Serialization behavior: "
                                        "model_dump() returns snake_case keys (e.g., total_tasks), "
                                        "model_dump(by_alias=True) returns camelCase keys (e.g., totalTasks). "
                                        "When testing JSON serialization, verify which format is used in the implementation."
                                    ),
                                    assertion_examples=[
                                        f"# Snake case (default): data = {model_name.lower()}.model_dump()",
                                        'assert data["field_name"] == expected_value',
                                        f"# Camel case (with by_alias=True): data = {model_name.lower()}.model_dump(by_alias=True)",
                                        'assert data["fieldName"] == expected_value',
                                    ],
                                )
                            )
                        elif base_name == "BaseModel":
                            serialization_hints.append(
                                SerializationHint(
                                    model_name=model_name,
                                    base_class="BaseModel",
                                    serialization_notes=(
                                        f"{model_name} inherits from BaseModel (Pydantic). "
                                        "Serialization uses snake_case by default. "
                                        "Use model_dump() to get dictionary representation."
                                    ),
                                    assertion_examples=[
                                        f"data = {model_name.lower()}.model_dump()",
                                        'assert data["field_name"] == expected_value',
                                    ],
                                )
                            )
except Exception:
    # Fail-safe: Continue without hints if parsing fails
    pass
```

### 3. Update Documentation to Reference serialization_hints

**In `procedures/python_unit_test_generation.md`, Step 1b (lines 124-143):**

Add explicit mention of using serialization_hints:

```markdown
#### Step 1b: Manual Analysis
**[REQUIRED]**: Use the file content from `file_references` (NOT `read_file`) to manually identify:
- Public interface (classes, methods, functions)
- Dependencies (imports, external calls)
- Data flow (inputs, outputs, state changes)
- Edge cases (empty inputs, boundary values, None)
- Error conditions (exceptions, validation failures)
- **[NEW]** Serialization format (check `serialization_hints` from py_test_strategist for camelCase vs snake_case)

**Output**: Complete test specification including:
- Behavioral specifications (from `file_references`)
- Technical test strategy (from `py_test_strategist`)
- **[NEW]** Serialization behavior guidance (from `serialization_hints`)
- Manual analysis notes
```

### 4. Add Verification Step in Procedure

**In `procedures/python_unit_test_generation.md`, Step 4 (lines 177-234):**

Add reminder before writing assertions:

```markdown
**CRITICAL - Using Mock Targets from py_test_strategist**:

When writing tests that require mocking, **ALWAYS use the `mock_targets` from Step 1b**.

**CRITICAL - Using Serialization Hints from py_test_strategist**:

When writing assertions that check serialized data:
1. Check `serialization_hints` from Step 1b output
2. For CamelCaseModel:
   - Verify if production code uses `model_dump()` (snake_case) or `model_dump(by_alias=True)` (camelCase)
   - Match your assertion to the actual format used
3. For BaseModel:
   - Always use snake_case (model_dump() default)
4. When in doubt: Read the production code to see which serialization method is called

**Common Mistakes to Avoid:**
- ❌ Assuming camelCase based on model name alone
- ❌ Not checking py_test_strategist serialization_hints output
- ❌ Writing assertions before verifying actual serialization format
- ✅ Check serialization_hints → Read production code → Write assertions
```

## Expected Impact

### Before (Current State)
- Agent iterations: ~38+ turns for serialization issues
- Failure rate: High (KeyError, assertion failures)
- Common pattern: Trial-and-error between camelCase and snake_case

### After (With Improvements)
- Agent iterations: ~6-10 turns (84% reduction)
- Failure rate: Low (explicit guidance prevents guesswork)
- Pattern: Check hints → Verify code → Write correct assertions

## Implementation Checklist

- [ ] Update `scripts/python/tests/generate_unit_test.py` line 512 (instruction template)
- [ ] Enhance `src/pipe/core/tools/py_test_strategist.py` (add model analysis for target file)
- [ ] Update `procedures/python_unit_test_generation.md` Step 1b (add serialization_hints reference)
- [ ] Update `procedures/python_unit_test_generation.md` Step 4 (add serialization verification)
- [ ] Test with a CamelCaseModel file (e.g., task.py) to verify hints are generated
- [ ] Run through full test generation cycle to measure iteration reduction

## Testing Strategy

1. **Unit test for enhanced py_test_strategist:**
   - Input: `src/pipe/core/models/task.py` (has `AgentTask(CamelCaseModel)`)
   - Expected: `serialization_hints` should include `AgentTask` with camelCase guidance

2. **Integration test:**
   - Run full test generation for a file with CamelCaseModel
   - Verify agent doesn't make camelCase/snake_case errors
   - Measure iteration count vs current baseline

3. **Regression test:**
   - Ensure existing tests still pass
   - Verify serialization_hints don't break when no models exist

## Alternative Approaches Considered

### Alternative 1: Add runtime detection in tests
- **Idea**: Write tests that detect serialization format at runtime
- **Rejected**: Adds complexity to tests; better to get it right upfront

### Alternative 2: Force all models to use one format
- **Idea**: Standardize on snake_case only
- **Rejected**: `by_alias=True` is needed for API compatibility (camelCase JSON)

### Alternative 3: Add linter rule to catch camelCase/snake_case mismatches
- **Idea**: Static analysis to warn on incorrect key access
- **Rejected**: Doesn't help during test generation; only catches errors after

## Summary

This proposal enhances three key areas:

1. **Visibility**: Make serialization_hints prominent in instructions
2. **Coverage**: Analyze models in target file, not just dependencies
3. **Guidance**: Add explicit verification steps in procedure

The expected outcome is an **84% reduction in debugging iterations** (from 38+ to 6-10 turns) for serialization-related test failures.
