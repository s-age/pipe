# Development Guide

This guide covers development workflows, including running individual services, building, and contributing to the project.

## Running Services Individually

### Web UI (Flask Backend)

The Flask web application provides the backend API and serves the built React frontend.

#### Docker

```bash
docker-compose up web
```

#### Manual

```bash
cd src
poetry run python -m pipe.cli.app
```

Access at http://localhost:5000

#### Using the Web UI

The Web UI provides intuitive visual management and direct manipulation of session history.

| Use Case              | Description                                                                                                                                                    |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **View/Edit History** | Browse detailed session histories; surgically edit specific turns or session metadata (purpose/background).                                                    |
| **Fork from Turn**    | Easily **fork** a conversation from any specific turn to test alternative instructions or validate different LLM responses without altering the original flow. |
| **Enable Editing**    | Activate `expert_mode` in `setting.yml` to enable editing and deleting session turns directly from the Web UI.                                                 |
| **Continue Sessions** | Use form inputs to send new instructions to existing sessions.                                                                                                 |
| **Management**        | Intuitively start new sessions, compress history, or delete unnecessary sessions via a graphical interface.                                                    |

### React Frontend

The React application is built with Vite for fast development.

#### Docker

```bash
docker-compose up react
```

#### Manual

```bash
cd src/web
npm run dev
```

Access at http://localhost:3000

### Storybook

Storybook for UI component development and testing.

#### Docker

```bash
docker-compose up storybook
```

#### Manual

```bash
cd src/web
npm run storybook
```

Access at http://localhost:6006

### MCP Server

Model Context Protocol server for AI agent integration.

#### Docker

```bash
docker-compose up mcp
```

#### Manual

```bash
cd src
poetry run python -m pipe.cli.mcp_server
```

### LSP Server

Language Server Protocol server for Python code intelligence.

#### Docker

```bash
docker-compose up lsp
```

#### Manual

```bash
cd src
poetry run python -m pipe.cli.pygls_server
```

## Building and Deployment

### Building the React Frontend

For production builds:

```bash
cd src/web
npm run build
```

The built files are served by the Flask backend.

### Docker Build

To build all Docker images:

```bash
docker-compose build
```

## Development Workflow

1. **Setup:** Follow the [setup guide](setup.md)
2. **Development:** Run services individually or all together with `docker-compose up`
3. **Testing:** Run tests with `npm test` (frontend) or `poetry run pytest` (backend)
4. **Building:** Build frontend and commit changes
5. **Deployment:** Use Docker Compose for production deployment

## Contributing

This project is released under CC0 1.0 Universal Public Domain Dedication. We don't seek traditional contributors or pull requests. Instead, we encourage forking and creating your own versions. Feel free to copy, modify, and distribute as you wish. No need to be bound by a single vision—explore your own ideas!

For more information, see the main [README.md](../README.md).
