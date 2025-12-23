# Scripts Directory

This directory contains automation scripts for the Pipe project.

## Directory Structure

```
scripts/
├── README.md                           # This file
├── python/
│   ├── validate_code.sh               # Quality validation script (Ruff, MyPy, PyTest)
│   └── tests/
│       └── generate_unit_test.py      # Automated test generation orchestrator
└── (other script categories)
```

---

## Python Scripts

### Test Generation

#### `python/tests/generate_unit_test.py`

Automated test generation system that orchestrates conductor agents to generate comprehensive pytest tests for Python source files.

**Purpose**: Generate unit tests for Python files using AI agents with automatic quality validation and retry mechanisms.

**Usage**:

```bash
# Generate tests for all files in a directory
poetry run python scripts/python/tests/generate_unit_test.py <directory>

# Generate tests for specific files
poetry run python scripts/python/tests/generate_unit_test.py <file1> <file2> ...

# Resume from existing session
poetry run python scripts/python/tests/generate_unit_test.py --session <session_id> <targets>
```

**Examples**:

```bash
# Generate tests for all repository files
poetry run python scripts/python/tests/generate_unit_test.py src/pipe/core/repositories

# Generate tests for specific files
poetry run python scripts/python/tests/generate_unit_test.py \
  src/pipe/core/repositories/archive_repository.py \
  src/pipe/core/repositories/session_repository.py

# Generate tests for all service files
poetry run python scripts/python/tests/generate_unit_test.py src/pipe/core/services

# Resume a previous session
poetry run python scripts/python/tests/generate_unit_test.py --session abc123def456 src/pipe/core/repositories
```

**How It Works**:

1. **File Scanning**: Recursively scans target directory for Python source files
   - Excludes test files (`test_*.py`, `*_test.py`)
   - Excludes `__init__.py` files
   - Auto-detects layer from file path (repositories, services, models, etc.)

2. **Conductor Agent**: Launches a conductor agent that:
   - Creates TODO list for tracking progress
   - Processes each file sequentially via `invoke_serial_children`
   - Delegates to child agents for test generation
   - Each file gets a new child session to avoid context window bloat

3. **Test Generation** (per file):
   - Child agent follows `procedures/python_unit_test_generation.md`
   - Uses layer-specific test strategies (`roles/python/tests/core/{layer}.md`)
   - Writes comprehensive pytest tests with factories
   - Runs quality checks (Ruff, MyPy, PyTest)

4. **Automatic Retry**: If validation fails:
   - Serial manager re-executes agent with error information
   - Agent fixes the test code based on error output
   - Re-runs validation script
   - Up to 3 total attempts (1 initial + 2 retries)

5. **Auto-Commit**: If only test files changed, automatically commits with message:
   ```
   test: add tests for {filename}
   ```

**Arguments**:

- `targets`: One or more file or directory paths to process
- `--session <id>`: Resume existing conductor session (optional)

**Output**:

```
Scanning for Python files in: src/pipe/core/repositories
Found 3 Python source files

Files to process:
- src/pipe/core/repositories/archive_repository.py → tests/unit/core/repositories/test_archive_repository.py (layer: repositories)
- src/pipe/core/repositories/session_repository.py → tests/unit/core/repositories/test_session_repository.py (layer: repositories)
- src/pipe/core/repositories/file_repository.py → tests/unit/core/repositories/test_file_repository.py (layer: repositories)

Launching Test Conductor...
Command: poetry run takt --purpose "Automated test generation for 3 Python source files" ...
```

**Related Files**:

- Conductor Procedure: `procedures/python_unit_test_conductor.md`
- Test Generation Procedure: `procedures/python_unit_test_generation.md`
- Validation Script: `scripts/python/validate_code.sh`
- Test Strategies: `roles/python/tests/core/*.md`

---

### Code Validation

#### `python/validate_code.sh`

Quality validation script that runs Ruff, MyPy, and PyTest checks on Python test files.

**Purpose**: Validate test code quality and ensure tests pass before committing. Called automatically by the serial manager during test generation with retry support.

**Usage**:

```bash
# Validate a single test file
scripts/python/validate_code.sh <test_file_path>

# Called by serial manager (receives session info via env vars)
# PIPE_SESSION_ID and PIPE_PROJECT_ROOT are automatically set
```

**Examples**:

```bash
# Validate a test file
scripts/python/validate_code.sh tests/unit/core/repositories/test_archive_repository.py

# Check specific test file with full path
scripts/python/validate_code.sh tests/unit/core/services/test_task_executor_base.py
```

**Validation Steps**:

1. **Ruff Check** (Linting):
   ```bash
   poetry run ruff check <test_file>
   ```
   - Checks code style and formatting
   - Enforces line length limits
   - Detects unused imports, variables, etc.

2. **MyPy Check** (Type Checking):
   ```bash
   poetry run mypy <test_file>
   ```
   - Validates type annotations
   - Catches type errors
   - Ensures type safety

3. **PyTest** (Test Execution):
   ```bash
   poetry run pytest <test_file> -v
   ```
   - Runs all tests in the file
   - Validates test logic
   - Ensures tests pass

4. **Git Status Check**:
   ```bash
   git status --short
   ```
   - Checks if any production code was modified
   - Warns if changes outside `tests/` directory detected

**Exit Codes**:

- `0`: All checks passed and only test files changed
- `1`: One or more checks failed OR production code was modified

**Integration with Test Generation**:

This script is called automatically by the serial manager during test generation:

```python
tasks = [
    {
        "type": "agent",
        "instruction": "Generate tests for file.py"
    },
    {
        "type": "script",
        "script": "python/validate_code.sh",
        "args": ["tests/unit/test_file.py"],
        "max_retries": 2  # Retry up to 2 times on failure
    }
]
```

**Retry Behavior**:

When validation fails:
1. Serial manager captures error output
2. Re-executes the agent task with error information
3. Agent fixes the test code
4. Re-runs this validation script
5. Repeats up to `max_retries` times

**Environment Variables**:

- `PIPE_SESSION_ID`: Current session ID (set by serial manager)
- `PIPE_PROJECT_ROOT`: Project root directory (set by serial manager)

**Output Example**:

```
[validate_code] Validating: tests/unit/core/repositories/test_archive_repository.py
[validate_code] Step 1/4: Running Ruff...
✓ Ruff passed

[validate_code] Step 2/4: Running MyPy...
✓ MyPy passed

[validate_code] Step 3/4: Running PyTest...
✓ PyTest passed (5 tests)

[validate_code] Step 4/4: Checking git status...
✓ Only test files modified

[validate_code] ✓ All validation checks passed
```

---

## Environment Requirements

All scripts in this directory require:

- **Poetry**: Python dependency management
- **Python 3.11+**: Modern Python version
- **Git**: Version control (for git status checks)
- **Takt CLI**: Session management tool (`poetry run takt`)

Install dependencies:

```bash
poetry install
```

---

## Script Development Guidelines

When adding new scripts to this directory:

1. **Organize by Language/Purpose**:
   - `python/` for Python-related scripts
   - `typescript/` for TypeScript-related scripts (future)
   - Use subdirectories for specific purposes (`tests/`, `linting/`, etc.)

2. **Make Scripts Executable**:
   ```bash
   chmod +x scripts/python/your_script.sh
   ```

3. **Use Proper Shebangs**:
   - Bash scripts: `#!/usr/bin/env bash`
   - Python scripts: `#!/usr/bin/env python3`

4. **Document in README**: Add clear documentation here with:
   - Purpose and usage
   - Examples
   - Exit codes
   - Environment variables
   - Integration points

5. **Follow Project Conventions**:
   - Use Poetry for Python dependencies
   - Use environment variables for configuration
   - Provide clear error messages
   - Return appropriate exit codes

6. **Test Before Committing**:
   - Run the script manually
   - Test edge cases
   - Verify exit codes
   - Update documentation

---

## Troubleshooting

### Common Issues

**Script not found**:
```bash
# Make sure you're running from project root
cd /path/to/pipe
poetry run python scripts/python/tests/generate_unit_test.py ...
```

**Permission denied**:
```bash
# Make script executable
chmod +x scripts/python/validate_code.sh
```

**Module not found**:
```bash
# Install dependencies
poetry install
```

**Session not found**:
```bash
# List available sessions
poetry run takt --list-sessions

# Start a new session (don't use --session flag)
poetry run python scripts/python/tests/generate_unit_test.py src/pipe/core/repositories
```

---

## Related Documentation

- [Python Unit Test Conductor Procedure](../procedures/python_unit_test_conductor.md)
- [Python Unit Test Generation Procedure](../procedures/python_unit_test_generation.md)
- [Python Test Strategies](../roles/python/tests/tests.md)
- [Layer-Specific Test Strategies](../roles/python/tests/core/)

---

## Future Scripts

Planned additions:

- `python/lint_project.sh`: Lint entire project
- `python/type_check_project.sh`: Type check entire project
- `typescript/tests/generate_unit_test.py`: TypeScript test generation
- `typescript/validate_code.sh`: TypeScript validation
- `db/migrate.sh`: Database migration script
- `deploy/check_readiness.sh`: Deployment readiness checks
