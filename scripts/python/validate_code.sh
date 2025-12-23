#!/usr/bin/env bash
#
# Validate test file quality gates
#
# Usage: validate_test.sh <test_file_path>
#
# This script:
# 1. Runs Ruff linting
# 2. Runs MyPy type checking
# 3. Runs PyTest execution
# 4. Checks git status for changes outside tests/
#
# Exit codes:
#   0 - All checks passed, changes only in tests/
#   1 - Quality checks failed OR changes outside tests/
#

set -euo pipefail

# Check arguments
if [ $# -ne 1 ]; then
    echo "Error: Missing test file path argument"
    echo "Usage: $0 <test_file_path>"
    exit 1
fi

TEST_FILE="$1"

# Verify test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "Error: Test file not found: $TEST_FILE"
    exit 1
fi

echo "=================================================="
echo "Quality Gate Validation"
echo "Test file: $TEST_FILE"
echo "=================================================="
echo ""

# Quality gate 1: Ruff
echo "[1/3] Running Ruff linting..."
if poetry run ruff check "$TEST_FILE"; then
    echo "✅ Ruff check passed"
else
    echo "❌ Ruff check failed"
    exit 1
fi
echo ""

# Quality gate 2: MyPy
echo "[2/3] Running MyPy type checking..."
if poetry run mypy "$TEST_FILE"; then
    echo "✅ MyPy check passed"
else
    echo "❌ MyPy check failed"
    exit 1
fi
echo ""

# Quality gate 3: PyTest
echo "[3/3] Running PyTest..."
if poetry run pytest -v; then
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
    exit 1
fi

echo "✅ All changes are within tests/ directory"
echo "Safe to auto-commit"
exit 0
