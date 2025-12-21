# Setup Guide

This guide provides setup instructions for the `pipe` project, with options for Docker Compose (recommended) and manual installation.

## Docker Setup (Recommended)

Use Docker Compose for a quick and isolated setup.

### Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/s-age/pipe.git
   cd pipe
   ```

2. **Set up environment variables:**
   - Copy the default environment file:
     ```bash
     cp .env.default .env
     ```
   - Edit `.env` and add your API keys:
     - For Gemini API: `GOOGLE_API_KEY='YOUR_API_KEY_HERE'`
     - For other services, add as needed.

3. **Run the application:**

   ```bash
   docker-compose up --build
   ```

4. **Access the services:**
   - **Web UI (Flask):** http://localhost:5000
   - **React Dev Server:** http://localhost:3000
   - **Storybook:** http://localhost:6006

For detailed development workflows and running individual services, see [docs/development.md](development.md).

### Services Overview

The Docker Compose setup includes the following services:

- **web**: Flask web application with backend API
- **react**: React development server with Vite
- **mcp**: Model Context Protocol server
- **lsp**: Language Server Protocol server for Python
- **storybook**: Storybook for UI component development

### Development

To run in development mode with hot reloading:

```bash
docker-compose up
```

To rebuild after changes:

```bash
docker-compose up --build
```

## Manual Setup

For development or when Docker is not available, set up manually using Poetry.

### Prerequisites

- Python 3.12 or higher
- Poetry installed (`pip install poetry` or use the official installer)
- Node.js 24 (for frontend development)
- `gemini-cli` is optional; the system can use Gemini API directly for most features.

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/s-age/pipe.git
   cd pipe
   ```

2. **Install Python dependencies:**

   ```bash
   poetry install
   ```

3. **Install Node.js dependencies (for frontend):**

   ```bash
   cd src/web
   npm install
   cd ../..
   ```

4. **Set up API Key:** Create a `.env` file (you can copy `.env.default`).
   - For Gemini API mode: Add `GOOGLE_API_KEY='YOUR_API_KEY_HERE'` in your `.env` file.
   - For `gemini-cli` mode: Set `GOOGLE_API_KEY` in your environment (e.g., `export GOOGLE_API_KEY='YOUR_API_KEY_HERE'`).
   - The system supports extensible backends; configure other agents (e.g., Claude, OpenAI) via `setting.yml` and their respective API keys.

5. **Run the application:**
   See [docs/development.md](development.md) for detailed commands to run individual services.

## Configuration

- Environment variables are defined in `.env`
- Application settings can be modified in `setting.yml`
- Docker-specific configs are in `docker-compose.yml`

## Troubleshooting

- Ensure Docker and Docker Compose are installed and running (for Docker setup)
- Check that ports 5000, 3000, 6006 are available
- Verify API keys are correctly set in `.env`
- For manual setup, ensure Python and Node.js versions match requirements

For more detailed information, see the main [README.md](../README.md).
