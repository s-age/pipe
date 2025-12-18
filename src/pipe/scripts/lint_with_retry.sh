#!/bin/bash
set -e

# Environment variables from serial_manager
SESSION_ID="${PIPE_SESSION_ID}"
MAX_ATTEMPTS="${1:-3}"
TARGET_DIR="${2:-src/}"

echo "[lint_with_retry] Starting Lint validation (max attempts: $MAX_ATTEMPTS)"

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    echo "[lint_with_retry] === Attempt $attempt/$MAX_ATTEMPTS ==="

    # Execute Ruff lint via Poetry
    if poetry run ruff check "$TARGET_DIR"; then
        echo "[lint_with_retry] ✓ Lint passed on attempt $attempt"
        exit 0
    fi

    echo "[lint_with_retry] ✗ Lint failed on attempt $attempt"

    # Launch fixer agent if not final attempt
    if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
        echo "[lint_with_retry] Launching fixer agent..."

        # Capture lint errors
        LINT_OUTPUT=$(poetry run ruff check "$TARGET_DIR" 2>&1 || true)

        # Launch fixer agent synchronously (wait for completion)
        poetry run takt --session "$SESSION_ID" --instruction "
Previous lint validation failed (attempt $attempt/$MAX_ATTEMPTS).

【Ruff Output】
$LINT_OUTPUT

【Fix Instructions】
Fix all lint errors above. Lint will be re-run automatically after fixing.
" || {
            echo "[lint_with_retry] Fixer agent failed. Aborting."
            exit 1
        }

        echo "[lint_with_retry] Waiting 2 seconds before retry..."
        sleep 2
    fi
done

echo "[lint_with_retry] ✗ Lint failed after $MAX_ATTEMPTS attempts"
exit 1
