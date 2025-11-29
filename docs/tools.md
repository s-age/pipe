# Tools Guide

This guide covers the various tools and integrations available in the `pipe` project, including MCP and LSP servers.

## Model Context Protocol (MCP) Server

The MCP server allows integration with AI agents for advanced tool calling capabilities.

### Running the MCP Server

#### Docker

```bash
docker-compose up mcp
```

#### Manual

```bash
cd src
poetry run python -m pipe.cli.mcp_server
```

### Integration with `gemini-cli`

To use advanced features like agent-driven **Compression** and session **Forking** in `gemini-cli` mode, you must first register `pipe`'s tool server. This command tells `gemini-cli` how to communicate with this project's tools.

Execute the following command once:

```bash
gemini mcp add pipe_tools "python -m pipe.cli.mcp_server" --working-dir /path/to/pipe
```

_(Replace `/path/to/pipe` with the actual absolute path to this project's directory.)_

**Benefit:** After this integration, all tool calls made during a session (such as `create_verified_summary` or `read_file`) will become visible in the session history file (`.json`), providing complete transparency and auditability of the agent's actions.

## Language Server Protocol (LSP) Server

`pipe` also provides a Language Server Protocol (LSP) server based on `pygls`. This server integrates with IDEs (like VS Code) to enable advanced understanding and manipulation of Python code. Its purpose is to provide context for LLMs to better understand the codebase.

**Provided LSP Features:**

- **Code Analysis**: Provides definition locations and docstrings for classes, functions, and variables.
- **Code Snippets**: Extracts code snippets for specific symbols.
- **Type Hints**: Displays type hints for functions and classes.
- **Symbol References**: Searches for symbol references within files.

### How to Run

The LSP server can be started in the background using the following command. This allows IDEs to connect to the server.

```bash
python -m src.pipe.cli.pygls_server > /dev/null 2>&1 &
```

- This command starts the server in the background and redirects standard output and standard error to `/dev/null`.
- To stop the server, use the `kill` command with the Process Group ID (PGID) displayed upon startup. For example, if the PGID is `83272`:
  ```bash
  kill -s TERM -- -83272
  ```

**Note:** This server is designed to be connected to by an LSP client (e.g., an IDE like VS Code). Running it standalone will produce minimal visible output.

## Tool Registration

When creating new tools, place the tool files in the appropriate directories. Tools are automatically registered if they follow the expected structure.

For Python-related tool development, you may find `roles/python/craftsman.md` helpful as it provides guidance on tool creation and best practices.

For more information on development, see [docs/development.md](development.md).
