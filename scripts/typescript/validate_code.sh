#!/usr/bin/env bash
#
# Validate code quality gates for TypeScript project
#
# Usage: validate_code.sh [--ignore-external-changes]
#
# Options:
#   --ignore-external-changes  Skip git status check (for pre-commit hooks)
#
# This script:
# 1. Checks git status for changes outside src/web/ (FIRST - abort early if violated)
# 2. Runs TypeScript compiler check (tsc --noEmit)
# 3. Runs formatter (npm run format)
# 4. Runs linter with auto-fix (npm run lint --fix)
#
# Exit codes:
#   0 - All checks passed, changes only in src/web/
#   1 - Quality checks failed (type checking, formatting, linting)
#   2 - ABORT: Changes detected outside src/web/ (permanent failure, no retry)
#

set -euo pipefail

# Parse arguments
IGNORE_EXTERNAL_CHANGES=false
POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --ignore-external-changes)
            IGNORE_EXTERNAL_CHANGES=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Usage: validate_code.sh [--ignore-external-changes]"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

echo "=================================================="
echo "Quality Gate Validation (TypeScript)"
echo "Checking src/web/ directory"
echo "=================================================="
echo ""

# CRITICAL: Check git status FIRST to abort early before running expensive checks
if [ "$IGNORE_EXTERNAL_CHANGES" = false ]; then
    echo "[1/4] Checking git status..."
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

        # Check if any changes are outside src/web/
        NON_WEB_CHANGES=$(echo "$CHANGED_FILES" | grep -v '^src/web/' || true)

        if [ -n "$NON_WEB_CHANGES" ]; then
            echo "🚨 FATAL ERROR: Unauthorized file modifications detected"
            echo ""
            echo "Changes detected outside src/web/ directory:"
            echo "$NON_WEB_CHANGES"
            echo ""
            echo "ABORT: Tests must ONLY modify files in src/web/ directory."
            echo "Unrelated file changes indicate:"
            echo "  - Accidental code modification"
            echo "  - Tool side effects"
            echo "  - Configuration file corruption"
            echo ""
            echo "DO NOT COMMIT. DO NOT PROCEED. ABORT IMMEDIATELY."
            echo "Skipping quality checks (no point running them)."
            exit 2
        fi

        echo "✅ All changes are within src/web/ directory"
    fi
    echo ""
else
    echo "ℹ️  Git status check skipped (--ignore-external-changes)"
    echo ""
fi

# Change to src/web directory for all subsequent commands
cd src/web

# Quality gate 2: TypeScript compiler check
echo "[2/4] Running TypeScript compiler check..."
if npx tsc --noEmit; then
    echo "✅ TypeScript compilation check passed"
else
    echo "❌ TypeScript compilation check failed"
    exit 1
fi
echo ""

# Quality gate 3: Formatter
echo "[3/4] Running formatter..."
if npm run format; then
    echo "✅ Formatting completed"
else
    echo "❌ Formatting failed"
    exit 1
fi
echo ""

# Quality gate 4: Linter
echo "[4/4] Running linter with auto-fix..."
if npm run lint -- --fix; then
    echo "✅ Linting passed"
else
    echo "❌ Linting failed"
    exit 1
fi
echo ""

echo "=================================================="
echo "✅ All quality gates passed"
echo "Safe to auto-commit"
echo "=================================================="
exit 0
