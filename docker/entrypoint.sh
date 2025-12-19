#!/bin/bash
set -e

# Always ensure dependencies are installed (volume mounts can override Dockerfile installs)
echo "Ensuring Python dependencies are installed..."
cd /app
poetry install --without dev --no-interaction --no-ansi

# Execute the main command
exec "$@"
