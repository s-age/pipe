#!/bin/bash
set -e

# Install dependencies if not present (for development with volume mounts)
if [ ! -d "/usr/local/lib/python3.12/site-packages/psutil" ]; then
    echo "Installing Python dependencies..."
    poetry install --without dev --no-interaction --no-ansi
fi

# Execute the main command
exec "$@"
