# Tool Architecture and Philosophy

This document outlines the design principles and architecture of the tools used within the `pipe` framework. A clear understanding of these concepts is crucial for extending the system and for ensuring agents use the tools as intended.

## The `pool` Mechanism: Capturing Tool Interactions

A critical and often misunderstood feature is the `pool`. When a tool is executed via the `mcp_server`, two distinct entries are **automatically added** to a temporary `pool` list within the active session file:

1.  **`function_calling` Turn:** Logs the exact tool and arguments that were called.
2.  **`tool_response` Turn:** Logs the result (success or failure) returned by the tool.

This mechanism ensures that every action taken by an agent is transparently recorded in the session history. The `takt` process then merges this `pool` into the main `turns` history after the model's response is received.

**Crucial Rule for Agents:** Agents **MUST NOT** attempt to manually create `function_calling` or `tool_response` turns. The `mcp_server` and `takt` handle this automatically. Any agent attempting to replicate this behavior is operating on a misunderstanding of the framework and will likely corrupt the session history.

## Core Principles

The entire tool ecosystem is built on a few core principles that mirror the stateless nature of Large Language Models.

### 1. Tools are Stateless

Every tool in this directory is designed to be **completely stateless**. They are simple functions that receive data, perform a single, specific action, and return a result. They do not hold any memory of past interactions.

### 2. The Session is the State

The single source of truth for any operation is the **session file (`.json`)**. Tools do not act in a vacuum; their primary purpose is to read from or modify the state of a specific session. This modification is always mediated by the `SessionService`, which is passed dynamically to any tool that needs it.

For example, a tool doesn't just "delete todos"; it tells the `SessionService` to delete the todos *for a specific session ID*.

### 3. Dynamic Prompt Construction

A key concept is the separation between *recording a reference* and *using its content*.

-   When you use `read_file` or `read_many_files`, the tools **do not return the file's content**.
-   Instead, they add a *reference* (the file path) to the session's `references` list.
-   It is only when the next prompt is being constructed by `takt` that the framework reads the content of these referenced files and injects it into the `file_references` section of the final JSON prompt sent to the LLM.

This approach keeps the tool interactions lightweight and makes the session file a clean record of *which* context is important, deferring the "heavy lifting" of reading content until it's actually needed.

## Tool Categories

The tools can be grouped into the following categories:

### Session & State Management

These tools directly manipulate the metadata and history of a session.

-   **`edit_todos` / `delete_todos`**: Modifies the `todos` list within the session object.
-   **`delete_session`**: Removes an entire session file and its backups.
-   **`replace_session_turns`**: Replaces a range of turns in the history with a summary, used for compression.
-   **`save_memory`**: (Stub) Intended to save information to a user's long-term memory profile.

### File System Interaction

These tools interact with the local file system.

-   **`read_file` / `read_many_files`**: **Do not return content.** They add file paths to the session's `references` list for inclusion in the next prompt.
-   **`write_file`**: Writes content to a specified file, with safety checks to prevent writing to sensitive areas.
-   **`replace`**: Performs a find-and-replace operation within a single file.
-   **`list_directory`**: Lists the contents of a directory.
-   **`glob`**: Finds files matching a glob pattern, respecting `.gitignore`.
-   **`search_file_content`**: Searches for a regex pattern within files in a given path.

### External Information Gathering

These tools fetch information from outside the local project environment.

-   **`google_web_search`**: Executes a grounded Google Search via a dedicated search agent and returns the results.
-   **`web_fetch`**: Fetches the raw text content from one or more URLs.

### Command Execution

-   **`run_shell_command`**: Executes a shell command within the project's root directory, with safety checks.

### Advanced Agentic Workflows

These tools are designed to orchestrate other agents or complex, multi-step processes.

-   **`create_verified_summary`**: Initiates the two-step history compression workflow. It first generates a summary and then calls `verify_summary`. This tool can only be used by an agent with the `compresser` role.
-   **`verify_summary`**: Invokes a `reviewer` sub-agent in a temporary session to validate a generated summary before it's applied to the original session's history.
