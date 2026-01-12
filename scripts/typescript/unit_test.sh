#!/usr/bin/env bash
#
# Run unit tests with quality validation for TypeScript custom hooks
#
# Usage: unit_test.sh [--ignore-external-changes] [--files <file1> <file2> ...]
#
# Options:
#   --ignore-external-changes  Skip git status check (for pre-commit hooks)
#   --files <paths>           Only test and validate specified files (relative to src/web/)
#
# This script:
# 1. Runs validate_code.sh (git status, TypeScript, formatter, linter)
# 2. Runs unit tests for specified test files (npm run test:unit)
#
# Exit codes:
#   0 - All checks passed, tests passed
#   1 - Quality checks or tests failed
#   2 - ABORT: Changes detected outside src/web/ (permanent failure, no retry)
#

set -euo pipefail

# Parse arguments
IGNORE_EXTERNAL_CHANGES=false
TARGET_FILES=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --ignore-external-changes)
            IGNORE_EXTERNAL_CHANGES=true
            shift
            ;;
        --files)
            shift
            # Collect all subsequent arguments until next flag or end
            while [[ $# -gt 0 ]] && [[ ! "$1" =~ ^-- ]]; do
                TARGET_FILES+=("$1")
                shift
            done
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Usage: unit_test.sh [--ignore-external-changes] [--files <file1> <file2> ...]"
            exit 1
            ;;
        *)
            # Default behavior: treat positional args as target files
            TARGET_FILES+=("$1")
            shift
            ;;
    esac
done

echo "=================================================="
echo "Unit Test Execution with Quality Validation"
if [ ${#TARGET_FILES[@]} -eq 0 ]; then
    echo "Testing src/web/ directory (all test files)"
else
    echo "Testing specific files:"
    for file in "${TARGET_FILES[@]}"; do
        echo "  - $file"
    done
fi
echo "=================================================="
echo ""

# Step 1: Run quality validation
echo "[Step 1/2] Running quality validation..."
echo "=================================================="
echo ""

# Build validate_code.sh command
VALIDATE_CMD="bash scripts/typescript/validate_code.sh"
if [ "$IGNORE_EXTERNAL_CHANGES" = true ]; then
    VALIDATE_CMD="$VALIDATE_CMD --ignore-external-changes"
fi
if [ ${#TARGET_FILES[@]} -gt 0 ]; then
    VALIDATE_CMD="$VALIDATE_CMD --files ${TARGET_FILES[*]}"
fi

# Execute validation
if $VALIDATE_CMD; then
    echo "✅ Quality validation passed"
else
    VALIDATE_EXIT_CODE=$?
    if [ $VALIDATE_EXIT_CODE -eq 2 ]; then
        echo "🚨 ABORT: Permanent failure detected (exit code 2)"
        echo "Changes outside src/web/ directory detected"
        exit 2
    else
        echo "❌ Quality validation failed (exit code $VALIDATE_EXIT_CODE)"
        exit 1
    fi
fi
echo ""

# Step 2: Run unit tests
echo "[Step 2/2] Running unit tests..."
echo "=================================================="
echo ""

# Change to src/web directory for npm commands
cd src/web

# Build test command
if [ ${#TARGET_FILES[@]} -eq 0 ]; then
    # Run all tests
    echo "ℹ️  Running all unit tests in src/web/"
    if npm run test:unit; then
        echo "✅ All unit tests passed"
    else
        echo "❌ Unit tests failed"
        exit 1
    fi
else
    # Run tests for specific files
    # Extract test file names (handle both full paths and relative paths)
    TEST_PATTERNS=()
    for file in "${TARGET_FILES[@]}"; do
        # Remove 'src/web/' prefix if present
        file="${file#src/web/}"

        # Extract just the filename without path and extension
        # e.g., "components/organisms/Turn/hooks/__tests__/useTurnActions.test.ts" -> "useTurnActions"
        if [[ "$file" == *"__tests__"* ]]; then
            # Extract test file name
            filename=$(basename "$file" .test.ts)
            TEST_PATTERNS+=("$filename")
        else
            # Not a test file - skip
            echo "ℹ️  Skipping non-test file: $file"
        fi
    done

    if [ ${#TEST_PATTERNS[@]} -eq 0 ]; then
        echo "⚠️  No test files found in specified files"
        echo "✅ Skipping test execution (no tests to run)"
    else
        echo "ℹ️  Running tests matching patterns:"
        for pattern in "${TEST_PATTERNS[@]}"; do
            echo "    - $pattern"
        done
        echo ""

        # Run tests with pattern matching (test:unit already includes --run flag)
        if npm run test:unit -- "${TEST_PATTERNS[@]}"; then
            echo "✅ Unit tests passed"
        else
            echo "❌ Unit tests failed"
            exit 1
        fi
    fi
fi
echo ""

echo "=================================================="
echo "✅ All quality gates and unit tests passed"
echo "Safe to auto-commit"
echo "=================================================="
exit 0
