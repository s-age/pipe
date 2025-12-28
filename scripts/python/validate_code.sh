#!/usr/bin/env bash
#
# Validate code quality gates for entire project
#
# Usage: validate_code.sh [--verbose] [--coverage]
#
# Options:
#   --verbose                  Enable verbose output for pytest
#   --coverage                 Enable coverage reporting for pytest
#   --ignore-external-changes  Skip git status check (for pre-commit hooks)
#
# This script:
# 1. Checks git status for changes outside tests/ (FIRST - abort early if violated)
# 2. Runs Black formatter (88-character line length enforcement)
# 3. Runs Ruff linting with auto-fix on entire project
# 4. Runs Ruff formatting on entire project
# 5. Runs MyPy type checking on entire project
# 6. Runs PyTest execution
#
# Exit codes:
#   0 - All checks passed, changes only in tests/
#   1 - Quality checks failed (linting, type checking, tests)
#   2 - ABORT: Changes detected outside tests/ (permanent failure, no retry)
#

set -euo pipefail

# Parse arguments
VERBOSE_ENABLED=false
COVERAGE_ENABLED=false
IGNORE_EXTERNAL_CHANGES=false
POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE_ENABLED=true
            shift
            ;;
        --coverage)
            COVERAGE_ENABLED=true
            shift
            ;;
        --ignore-external-changes)
            IGNORE_EXTERNAL_CHANGES=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Usage: validate_code.sh [--verbose] [--coverage] [--ignore-external-changes] [paths...]"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

echo "=================================================="
echo "Quality Gate Validation"
if [ ${#POSITIONAL_ARGS[@]} -gt 0 ]; then
    echo "Checking paths: ${POSITIONAL_ARGS[*]}"
else
    echo "Checking entire project"
fi
echo "=================================================="
echo ""

# CRITICAL: Check git status FIRST to abort early before running expensive checks
if [ "$IGNORE_EXTERNAL_CHANGES" = false ]; then
    echo "[1/6] Checking git status..."
    echo "=================================================="
    echo ""

    # Get list of changed files (excluding untracked)
    CHANGED_FILES=$(git status --short | grep -v '^??' | awk '{print $2}' || true)

    if [ -z "$CHANGED_FILES" ]; then
        echo "ℹ️  No changes detected"
    else
        echo "Changed files:"
        echo "$CHANGED_FILES"
        echo ""

        # Check if any changes are outside tests/
        NON_TEST_CHANGES=$(echo "$CHANGED_FILES" | grep -v '^tests/' || true)

        if [ -n "$NON_TEST_CHANGES" ]; then
            echo "🚨 FATAL ERROR: Unauthorized file modifications detected"
            echo ""
            echo "Changes detected outside tests/ directory:"
            echo "$NON_TEST_CHANGES"
            echo ""
            echo "ABORT: Tests must ONLY modify files in tests/ directory."
            echo "Unrelated file changes indicate:"
            echo "  - Accidental code modification"
            echo "  - Tool side effects"
            echo "  - Import errors modifying __pycache__"
            echo "  - Configuration file corruption"
            echo ""
            echo "DO NOT COMMIT. DO NOT PROCEED. ABORT IMMEDIATELY."
            echo "Skipping quality checks (no point running them)."
            exit 2
        fi

        echo "✅ All changes are within tests/ directory"
    fi
    echo ""
else
    echo "ℹ️  Git status check skipped (--ignore-external-changes)"
    echo ""
fi

# Format code with Black BEFORE running quality checks
echo "[2/6] Running Black formatter..."
if poetry run black .; then
    echo "✅ Black formatting completed"
else
    echo "❌ Black formatting failed"
    exit 1
fi
echo ""

# Quality gate 3: Ruff check
echo "[3/6] Running Ruff linting..."
RUFF_CHECK_TARGETS="."
if [ ${#POSITIONAL_ARGS[@]} -gt 0 ]; then
    RUFF_CHECK_TARGETS="${POSITIONAL_ARGS[*]}"
fi

if poetry run ruff check --fix $RUFF_CHECK_TARGETS; then
    echo "✅ Ruff check passed"
else
    echo "❌ Ruff check failed"
    exit 1
fi
echo ""

# Quality gate 4: Ruff format
echo "[4/6] Running Ruff formatting..."
RUFF_FORMAT_TARGETS="."
if [ ${#POSITIONAL_ARGS[@]} -gt 0 ]; then
    RUFF_FORMAT_TARGETS="${POSITIONAL_ARGS[*]}"
fi

if poetry run ruff format $RUFF_FORMAT_TARGETS; then
    echo "✅ Ruff format passed"
else
    echo "❌ Ruff format failed"
    exit 1
fi
echo ""

# Quality gate 5: MyPy
echo "[5/6] Running MyPy type checking..."
MYPY_TARGETS="."
if [ ${#POSITIONAL_ARGS[@]} -gt 0 ]; then
    MYPY_TARGETS="${POSITIONAL_ARGS[*]}"
fi

if poetry run mypy $MYPY_TARGETS; then
    echo "✅ MyPy check passed"
else
    echo "❌ MyPy check failed"
    exit 1
fi
echo ""

# Quality gate 6: PyTest
echo "[6/6] Running PyTest..."
PYTEST_ARGS="-q"

if [ "$VERBOSE_ENABLED" = true ]; then
    echo "Verbose output enabled"
    PYTEST_ARGS="-v"
fi

if [ "$COVERAGE_ENABLED" = true ]; then
    echo "Coverage reporting enabled"
    PYTEST_ARGS="$PYTEST_ARGS --cov=src/pipe --cov-report=term-missing --cov-report=html"
fi

if [ ${#POSITIONAL_ARGS[@]} -gt 0 ]; then
    PYTEST_ARGS="$PYTEST_ARGS ${POSITIONAL_ARGS[*]}"
fi

if poetry run pytest $PYTEST_ARGS; then
    echo "✅ PyTest passed"
else
    echo "❌ PyTest failed"
    exit 1
fi
echo ""

echo "=================================================="
echo "✅ All quality gates passed"
echo "Safe to auto-commit"
echo "=================================================="
exit 0
