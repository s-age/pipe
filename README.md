[![License: CC0-1.0](https://img.shields.io/badge/License-CC0--1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)

# pipe

<p align="center">
  <img src="https://raw.githubusercontent.com/s-age/pipe/main/src/web/static/images/logo.png" alt="pipe logo" width="320">
</p>

## Overview

> **Make AI Agents Deterministic.**

`pipe` is an AI agent framework built with deep respect for the **Unix Philosophy**. It shifts the paradigm from "Conversational AI" to **AasF (Agent as Function)**.

Unlike traditional frameworks that treat agents as stateful, conversational partners, `pipe` treats an agent as a **stateless, pure function** that accepts structured context via standard input (stdin) and returns execution results via standard output (stdout).

### Philosophy

- **Do One Thing Well:** Each agent role is specialized and acts as a single, deterministic function call.
- **Composable Intelligence:** Chain agents through natural language instructions via `takt`. A parent agent (e.g., Conductor) delegates tasks to sub-agents, where the output of one agent informs the next through structured session management.
- **Universal Interface:** Built on text streams (JSON/Markdown), ensuring seamless integration with any CLI tool, script, or CI/CD pipeline.

`pipe` provides a strong foundation for the Agent as Function (AasF) paradigm, enabling smaller contexts by structuring information effectively. It realizes bottom-heavy architecture—where the complexity lies in the well-designed tools and frameworks rather than overburdening the LLM at the top. This is achieved through easy multi-agent orchestration, allowing agents to handle small, specialized tasks and build complex workflows without requiring the LLM to manage everything at once.

In this paradigm, the smaller the function, the smaller the deviation—ensuring that each agent remains highly predictable and composable.

Ultimately, pipe aims to automate not just individual agent functions, but entire session lifecycles—from creation and execution to management and archival—enabling fully autonomous AI workflows.

For a deeper dive into the principles of Context Engineering that underpin this philosophy, see our [Wiki article](https://github.com/s-age/pipe/wiki/Context-Engineering:-The-Art-of-Communicating-Intent-to-LLMs).

For an overview of the AasF (Agent as a Function) paradigm that `pipe` implements, see our [Wiki article](https://github.com/s-age/pipe/wiki/Overview:-What-AasF-Is).

## Key Concepts

### Mechanism

In `pipe`, an agent is defined simply as:

$$f(\text{context}) \rightarrow \text{result}$$

`takt` structures and injects precisely crafted context into the LLM. You must explicitly define the `--purpose` and `--background` to ground the agent, ensuring it never hallucinates the goal.

```bash
# Example: Create a parent session and use its session ID to create a child session
takt --purpose "Simple greeting" \
     --background "Basic conversation example." \
     --instruction "Say hello." \
| jq -r '.session_id' \
| xargs -I {} takt --parent {} \
                   --purpose "Follow-up response" \
                   --background "A new session that builds on the parent session." \
                   --instruction "Respond to the greeting."
```

This approach leverages `takt`'s options like `--roles` for persona definition, `--instruction` for task specification, and `--parent` for hierarchical session relationships, ensuring modular and composable AI workflows. The output JSON can be piped through tools like `jq` for extraction and chaining, maintaining the deterministic context management central to `pipe`'s philosophy.

This abstraction enables seamless composition, where any source of structured data can feed into an agent, and agents can chain together or output to any consumer. The philosophy emphasizes composability over monolithic interfaces:

- `cli | agent`: Pipe command-line outputs directly into AI processing.
- `agent | agent`: Chain agents for multi-step reasoning or specialized workflows.
- `any script | agent`: Integrate arbitrary scripts or tools as context providers.
- `WebUI | agent`: Connect web interfaces or APIs to AI orchestration.

Through `takt`, this becomes a reality—LLM complexity distilled into a Unix-like pipeline of deterministic transformations. Agents consume JSON contexts and produce JSON results, allowing infinite recombination without loss of control.

Stop managing complex conversation states. Start composing intelligent functions.

### A Clean Jailbreak from LLM Obfuscation

`pipe` is not another chat agent. It is a tool designed to give you, the developer, complete control over the conversational context. Unlike traditional clients that hide their history management in a black box, `pipe` empowers you to freely manipulate the history, extract what is essential, and achieve **true context engineering**.

This is a clean jailbreak tool from vendor obfuscation.

We employ a **minimal yet powerful** CLI-driven approach, focusing on the one thing that truly matters: ensuring the agent understands its purpose, history, and current task without ambiguity.

### Core Philosophy

#### 1. Total Context Control

The prompt is reconstructed with a structured, self-describing **JSON Schema** for every call. This is inherently more token-efficient and understandable for an LLM. The entire history is transparent, saved in readable JSON session files. This ensures full **auditability** and gives the stateless LLM a persistent, and more importantly, **malleable** memory. You can retry, refine, edit, delete, and compress with surgical precision.

#### 2. Uncompromising Extensibility

By default, `pipe` is based on `gemini-cli`, but this is merely an implementation detail. The core logic is decoupled. If you want to use the direct API, do it. If you want to use `claude-code`, do it. The framework is designed to be torn apart and rebuilt to your specifications.

#### 3. Git-Inspired Session Management

`pipe`'s session operations are designed with Git's powerful version control concepts in mind, providing developers with familiar and intuitive tools for managing conversational history:

| Operation    | Git Equivalent                             | Description                                                                                                                           |
| :----------- | :----------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| **Edit**     | `git commit --amend` or `git rebase -i`    | Modify the content of a specific turn or instruction in the session history, allowing for precise refinements without losing context. |
| **Delete**   | `git reset --hard` or `git rm`             | Remove unwanted turns or entire sections from the session, cleaning up the history for better focus.                                  |
| **Fork**     | `git branch` or `git fork`                 | Create a new session branch from any point in the conversation, enabling parallel exploration of alternative responses or strategies. |
| **Compress** | `git rebase --interactive` or `git squash` | Condense long conversation histories into concise summaries, reducing token usage while preserving essential context.                 |

This Git-inspired approach ensures that session management feels natural to developers, combining the flexibility of version control with the determinism of structured AI interactions.

---

## Features

- **Session-Based History:** Each conversation is a self-contained session, stored in a single, human-readable JSON file.
- **Structured JSON Prompting:** Builds a detailed, self-describing JSON object as the final prompt, providing meta-context to the model for improved clarity.
- **CLI-Driven Workflow:** A powerful command-line interface to start, continue, or compress sessions.
- **Extensible Backend:** The execution agent is decoupled. You can choose between `gemini-api` (direct API calls) and `gemini-cli` (CLI tool) via the `api_mode` setting in `setting.yml`. The architecture allows for swapping in other execution agents as well.
- **Configuration via YAML:** Configure model, context limits, and other settings in `setting.yml`.
- **Token-Aware:** Calculates token count for each prompt and warns before exceeding limits.
- **Dry Run Mode:** A `--dry-run` flag to inspect the final JSON prompt before sending it to the API.
- **Web UI for Management:** A comprehensive web interface to manage the entire lifecycle of a conversation.
- **Safe Operations:** Automatic backups are created before any edit or compression operation.
- **Language Support:** Allows specifying the language for agent responses.
- **YOLO Mode:** Automatically accept all actions (aka YOLO mode, see [https://www.youtube.com/watch?v=xvFZjo5PgG0](https://www.youtube.com/watch?v=xvFZjo5PgG0) for more details).
- **In-Session Todos:** Manage a simple todo list directly within the session's metadata.
- **Advanced Agent-driven Compression**:
  - A specialized `Compressor` agent can perform **partial compression** on any session's history.
  - Precisely control the compression by specifying a **turn range**, a **summarization policy** (what to keep), and a **target character count**.
  - Before applying the compression, a `Reviewer` agent automatically **verifies** that the summarized history maintains a natural conversational flow, preventing context loss.
  - **Note on MCP Server Setup:** To use advanced features like Compression and Forking, the `pipe` MCP server is configured in Docker environments. For local setups (if not using Docker), add the following to your `.gemini/setting.json` (adjust the `workingDir` path to your `pipe` installation):
    ```json
    {
      "mcpServers": {
        "pipe_tools": {
          "command": "python3",
          "args": ["-m", "pipe.cli.mcp_server"],
          "workingDir": "/path/to/pipe"
        }
      }
    }
    ```
  - **Customizing Verification:** If the verification process is too strict and frequently rejects summaries, you can edit `roles/verifier.md` to adjust the approval checklist for more lenient verification. This allows you to balance between context preservation and compression efficiency based on your needs.
- **Turn-based Forking:** Easily fork a conversation from any specific turn. This allows you to explore alternative responses from the LLM or test different instructions without altering the original history, enabling robust validation and experimentation.
- **Experimental: Therapist/Doctor Workflow:** LLM-powered session optimization where a specialized `Therapist` agent analyzes conversation sessions to identify issues and suggest improvements, and a `Doctor` agent applies approved modifications (edits, deletions, compressions) to reduce cognitive load and improve coherence.

See [docs/tools.md](docs/tools.md) for information on available tools and integrations.

See [docs/extending.md](docs/extending.md) for information on extending the framework with new agents.

See [docs/agent-registry.md](docs/agent-registry.md) for details on the agent registry pattern and how to add custom agents.

---

## Installation

See [docs/setup.md](docs/setup.md) for setup instructions.

## Usage

### Routes to Context Engineering

The **pipe** framework offers three primary routes, optimized for different user environments and goals, all built on the same structured core.

### 1. Route 1: CLI Script (Automation & CLI)

This route is ideal for **automation, scripting, and CLI-focused developers** who need reliable, repeatable execution, regardless of the programming language used—as long as you can invoke the `takt` command.

| Use Case               | Description                                                                                                                   |
| :--------------------- | :---------------------------------------------------------------------------------------------------------------------------- |
| **Start New Session**  | Define the complete context (`--purpose`, `--background`, `--roles`) and first instruction.                                   |
| **Continue Session**   | Specify an existing `<SESSION_ID>` and add a new instruction. This is the primary way to give the short-lived agent "memory." |
| **Compress History**   | Use the `--compress` flag to efficiently replace long history with a summary.                                                 |
| **Debug/Cost Control** | Use the `--dry-run` flag to inspect the generated JSON prompt before the API call.                                            |

**Examples:**

```bash
# Start New Session Example
takt --purpose "Create a new React component" --background "..." --roles "roles/engineer.md" --instruction "Create a 'UserProfile' component."

takt --session <SESSION_ID> --instruction "Now, add a state for loading."
```

### 2. Route 2: Web UI (Management & Human-in-the-Loop)

See [docs/development.md](docs/development.md) for details on running and using the Web UI.

### 3. Route 3: Execution from Agent (Orchestration)

This is for **advanced AI system builders** leveraging **pipe's** full context control capabilities for multi-agent coordination.

| Use Case                      | Description                                                                                                                                                                                         |
| :---------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Role Delegation**           | A parent agent assigns the **Conductor role** to a child agent and delegates the task using the structured command format.                                                                          |
| **Small-Scale Orchestration** | **By customizing the role definition**, the Conductor role can be programmed to divide complex tasks into subtasks and recursively delegate them to different execution agents with specific roles. |
| **Clean Execution**           | The delegated task is passed as a **structured JSON prompt**, ensuring maximum efficiency for the short-lived sub-agent.                                                                            |

**Execution Example (Delegation from Parent Agent):**

> **[IMPORTANT] The following command examples are not intended to be executed directly in the user's terminal. They are used as instructions to an already launched parent agent (such as Gemini) to assign the Conductor role and delegate tasks.**

```bash
Act as @roles/conductor.md takt --session <SESSION_ID> --instruction "Now, add a state for loading."
```

### 4. Route 4: Agent-driven Workflows (Compression & Verification)

The easiest way to perform compression is through the Web UI, which provides a dedicated compression interface in the right pane for the currently open session.

The `pipe` framework supports agent-driven meta-tasks like history management. The `Compressor` and `Reviewer` agents work in tandem to ensure both efficiency and quality.

| Step            | Agent        | Use Case                 | Description                                                                                                                                              |
| :-------------- | :----------- | :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Initiate** | `Compressor` | Surgical Compression     | Start a new session and assign the `roles/compressor.md` role. Instruct this agent to compress parts of _any other session_.                             |
| **2. Specify**  | `Compressor` | Controlled Summarization | Guide the agent by providing the target `SESSION_ID`, a `START` and `END` turn, a `policy` (what to keep), and a `target length`.                        |
| **3. Verify**   | `Reviewer`   | Quality Assurance        | Before applying the summary, the `Reviewer` agent is automatically invoked to check if the compressed history flows naturally and preserves key context. |
| **4. Apply**    | `Compressor` | Finalize Compression     | Once the verification is passed, the agent replaces the specified turn range with the generated summary.                                                 |

**Example (Starting a Compression Session):**

```bash
# Start a new session to manage other sessions
takt --purpose "Compress a long-running session" --role "roles/compressor.md" --instruction "I want to compress session <TARGET_SESSION_ID>."
```

The agent will then interactively guide you through the specification and verification process to perform the compression safely.

### 5. Route 5: Multi-Agent Simulation (e.g., Self-Play)

The true power of `pipe` is revealed in its ability to facilitate complex multi-agent simulations using nothing more than natural language. By defining roles and procedures in simple Markdown files, you can orchestrate sophisticated interactions between agents.

A compelling demonstration of this is achieving a Reversi game where Gemini plays against itself. This entire simulation is orchestrated by giving a single command to a parent agent.

| Use Case                         | Description                                                                                                                                                    |
| :------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Self-Play Simulation**         | Instruct an agent to adopt a role and execute a procedure. For example, tell Gemini to act as a Reversi player and follow the game's rules.                    |
| **Natural Language Programming** | The agents' behaviors are not hard-coded. They are guided entirely by the `@roles` and `@procedures` files you provide, making the system incredibly flexible. |

**Execution Example (Orchestrating a Self-Play Game):**

> **[IMPORTANT]** The following command is an instruction given to a parent AI agent (like Gemini), not meant for direct terminal execution.

```
Act as @roles/games/reversi_player.md and execute @procedures/reversi_game.md
```

This single line of instruction causes the agent to initiate a game of Reversi, playing against itself by following the rules and persona defined in the Markdown files. This showcases the framework's capability for complex task delegation and agent-based automation, all orchestrated through simple, human-readable text.

## Examples

### Dry Run Output Example

When running `takt` with the `--dry-run` flag, the generated JSON prompt is displayed. This JSON object represents the structured input that would be sent to the AI sub-agent. It can be useful for understanding how `pipe` constructs its prompts or for direct experimentation with AI models.

Here's an example of a generated prompt:

Note that the JSON presented here is pretty-printed for readability; the actual output from `takt --dry-run` is also pretty-printed with indentation for human readability.

See [docs/dry-run-sample.json](docs/dry-run-sample.json) for a full example.

## License

### The Spirit of the Jailbreak

This project's _original code_ is released under the [CC0 1.0 Universal (CC0 1.0) Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).

Customize it as you wish. Jailbreak as you desire.

**Important Note on Dependencies:**
This project utilizes various third-party libraries, each governed by its own license. While the original code of `pipe` is dedicated to the public domain under CC0, the licenses of these dependencies (e.g., MIT, Apache 2.0, BSD) still apply to their respective components.

- **Commercial Use**: Please review the licenses of all included third-party libraries to ensure compliance with your intended use, especially for commercial applications.
- **Attribution**: Some third-party licenses may require attribution. It is your responsibility to comply with all applicable license terms.

The purpose of this project is to be a **pipe to the agent**, and a **pipe to our followers** (the community).
