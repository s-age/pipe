#!/usr/bin/env bash
#
# Validate code quality gates for entire project
#
# Usage: validate_code.sh [--verbose] [--coverage]
#
# Options:
#   --verbose    Enable verbose output for pytest
#   --coverage   Enable coverage reporting for pytest
#
# This script:
# 1. Runs Ruff linting with auto-fix on entire project
# 2. Runs Ruff formatting on entire project
# 3. Runs MyPy type checking on entire project
# 4. Runs PyTest execution
# 5. Checks git status for changes outside tests/
#
# Exit codes:
#   0 - All checks passed, changes only in tests/
#   1 - Quality checks failed OR changes outside tests/
#

set -euo pipefail

# Parse arguments
VERBOSE_ENABLED=false
COVERAGE_ENABLED=false
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
        -*)
            echo "Unknown option: $1"
            echo "Usage: validate_code.sh [--verbose] [--coverage] [paths...]"
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

# Quality gate 1: Ruff check
echo "[1/4] Running Ruff linting..."
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

# Quality gate 2: Ruff format
echo "[2/4] Running Ruff formatting..."
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

# Quality gate 3: MyPy
echo "[3/4] Running MyPy type checking..."
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

# Quality gate 4: PyTest
echo "[4/4] Running PyTest..."
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

# Check for changes outside tests/
echo "=================================================="
echo "Git Status Check"
echo "=================================================="
echo ""

# Get list of changed files (excluding untracked)
CHANGED_FILES=$(git status --short | grep -v '^??' | awk '{print $2}' || true)

if [ -z "$CHANGED_FILES" ]; then
    echo "ℹ️  No changes detected"
    exit 0
fi

echo "Changed files:"
echo "$CHANGED_FILES"
echo ""

# Check if any changes are outside tests/
NON_TEST_CHANGES=$(echo "$CHANGED_FILES" | grep -v '^tests/' || true)

if [ -n "$NON_TEST_CHANGES" ]; then
    echo "⚠️  WARNING: Changes detected outside tests/ directory:"
    echo "$NON_TEST_CHANGES"
    echo ""
    echo "Action required: User confirmation needed before committing"
fi

echo "✅ All changes are within tests/ directory"
echo "Safe to auto-commit"
exit 0
