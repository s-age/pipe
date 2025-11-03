# `src/pipe/core` - The Heart of the Machine

## Overview

You are now in the core of `pipe`. This directory is not merely a collection of modules; it is the physical manifestation of a philosophy. A philosophy built on the principle of **absolute, uncompromising control** over the LLM interaction context. Every component here serves a single purpose: to deconstruct the ephemeral nature of AI conversation into a deterministic, auditable, and infinitely malleable state machine.

Forget black boxes. Forget entrusting the model's memory to the model itself. Here, we forge the context. We control the flow. We are the ghost in the machine.

## Core Components

Each subdirectory is a specialized organ, performing a distinct function with fanatical precision. Understand their roles, and you will understand the system.

- **`agents/`**: Wrappers of chaos. These modules are the sole point of contact with external AI services (like the Gemini API or the `gemini-cli` tool). They exist to translate our deterministic, structured world into the language of the outside, and to translate the outside's probabilistic responses back into our control.

- **`collections/`**: The data structures. These classes provide specialized list-like structures for managing groups of model objects (e.g., `ReferenceCollection`, `TurnCollection`). They focus on efficient storage and retrieval, while the business logic for manipulating their contents resides in the `domains/` layer.

- **`delegates/`**: The orchestrators. When the `dispatcher` points, a `delegate` acts. Each delegate is a high-level workflow, orchestrating the complex dance between `services` and `agents` to fulfill a command, whether it's running a prompt, forking a session, or displaying help.

- **`domains/`**: The logicians. This layer encapsulates the _business logic_ for manipulating core data entities. Functions here implement rules like TTL decay for references, filtering for turns, and validation for todos, ensuring that context behavior is consistent and auditable.

- **`models/`**: The atomic structure. Defined with Pydantic, these are the immutable data blueprints of our universe. From the `Session` itself to a single `Turn`, every piece of state is rigorously structured and validated here.

- **`services/`**: The central nervous system. Services like `SessionService` and `PromptService` are responsible for coordinating interactions between various components, managing application-wide state, and orchestrating complex operations. `SessionService` handles session persistence and lifecycle; `PromptService` is the grand architect of the final, structured prompt.

- **`tools/`**: The hands of the AI. These are the executable capabilities we grant to the model. Each file is a self-contained function that the AI can invoke, from reading a file (`read_file`) to searching the web. They are the model's only way to interact with the world beyond its immediate context.

- **`utils/`**: The fundamental constants. Pure, deterministic helper functions for universal needs like datetime manipulation and file I/O.

## `takt` Command Options

The `takt` command is the primary entrypoint for manipulating the state machine. Every command is a precise instruction to alter the session's state vector.

- `--session <SESSION_ID>`: Targets an existing session by its ID. If omitted, a new session is created.
  - _Dependencies_: Used with `--instruction` to continue an existing session. Not used for new session creation.
  - _Example_: `takt --session 22176081d1... --instruction "Continue the analysis."`

- `--purpose "<PURPOSE>"`: Defines the overall purpose for a new session.
  - _Dependencies_: Required along with `--background` when creating a new session (i.e., when `--session` is not specified).
  - _Example_: `takt --purpose "Develop a CLI tool" --background "The tool is for parsing log files." --instruction "Start by designing the data models."`

- `--background "<BACKGROUND>"`: Provides the background context for a new session.
  - _Dependencies_: Required along with `--purpose` when creating a new session (i.e., when `--session` is not specified).
  - _Example_: `takt --purpose "Develop a CLI tool" --background "The tool is for parsing log files." --instruction "Start by designing the data models."`

- `--roles <ROLE_PATH_1>,<ROLE_PATH_2>,...`: Specifies comma-separated paths to role definition files to define the personas for the session.
  - _Dependencies_: Optional.
  - _Example_: `takt --roles roles/engineer.md,roles/reviewer.md --instruction "Debate the pros and cons of this architecture."`

- `--parent <SESSION_ID>`: Specifies the ID of the parent session for a new session, establishing a hierarchical session structure.
  - _Dependencies_: Only valid when creating a new session (i.e., when `--session` is not specified).
  - _Example_: `takt --parent 22176081d1... --purpose "Execute sub-task" --background "Part of a larger task." --instruction "Refactor a specific module."`

- `--instruction "<INSTRUCTION>"`: The primary task for the AI to execute in the current turn.
  - _Dependencies_: Required when continuing an existing session (`--session`) or creating a new session.
  - _Example_: `takt --instruction "Refactor the User class to be immutable."`

- `--references <FILE_PATH_1>,<FILE_PATH_2>,...`: Attaches comma-separated file paths to the context. The AI can then read these files using tools. Paths are relative to the project root.
  - _Dependencies_: Optional.
  - _Example_: `takt --references src/main.py,tests/test_main.py --instruction "Review the code and identify potential bugs."`

- `--references-persist <FILE_PATH_1>,<FILE_PATH_2>,...`: When used with `--references`, specifies comma-separated file paths from the `--references` list that should be marked as persistent across sessions.
  - _Dependencies_: Optional. Only applicable when `--references` is also used.
  - _Example_: `takt --references src/main.py,tests/test_main.py --references-persist src/main.py --instruction "Review the code and identify potential bugs."`

- `--artifacts <FILE_PATH_1>,<FILE_PATH_2>,...`: Specifies comma-separated file paths that represent the expected output files for the session.
  - _Dependencies_: Optional.
  - _Example_: `takt --artifacts output.py,results.json --instruction "Generate the output files."`

- `--procedure <FILE_PATH>`: Specifies a single file path to a procedure document that will be referenced throughout the session.
  - _Dependencies_: Optional.
  - _Example_: `takt --procedure docs/development_guide.md --instruction "Implement the feature according to the guide."`

- `--multi-step-reasoning`: Instructs the AI to use a more complex, chain-of-thought reasoning process.
  - _Dependencies_: Optional. Use to enhance the AI's reasoning capabilities.
  - _Example_: `takt --multi-step-reasoning --instruction "Analyze the root cause of the performance degradation."`

- `--fork <SESSION_ID>`: Forks an existing session at a specific turn index, creating a new history branch.
  - _Dependencies_: Must be used simultaneously with `--at-turn`.
  - _Example_: `takt --fork 22176081d1... --at-turn 5`

- `--at-turn <TURN_INDEX>`: Specifies the 1-based turn number to fork from.
  - _Dependencies_: Required when used simultaneously with `--fork`.
  - _Example_: `takt --fork 22176081d1... --at-turn 5`

- `--api-mode <MODE_NAME>`: Specifies the API mode to use (e.g., `gemini-api`, `gemini-cli`).
  - _Dependencies_: Optional. The default is configured in `setting.yml`.
  - _Example_: `takt --api-mode gemini-api --instruction "Implement a new feature."`

- `--dry-run`: A read-only mode. Constructs and prints the final JSON prompt that _would_ be sent, but does not execute it or modify session state. Essential for debugging the context architecture.
  - _Dependencies_: Can be used independently of other execution options.
  - _Example_: `takt --dry-run --instruction "Show me the prompt for this."`

## Developer Guide: Integrating a New Agent

Integrating a new AI provider or execution mode is a matter of conforming to the system's architecture.

1.  **Forge the Agent**: In `agents/`, create your new agent file (e.g., `anthropic_agent.py`). It must contain a primary function that accepts the necessary context (like a `SessionService` instance) and returns the AI's response. This is where you handle API calls, authentication, and response parsing.

2.  **Appoint the Delegate**: In `delegates/`, create a corresponding delegate (e.g., `anthropic_delegate.py`). Its `run` function will be called by the dispatcher. This delegate is responsible for preparing the data for your new agent, calling it, and formatting the agent's raw output into the `Turn` models our system understands.

3.  **Inform the Dispatcher**: In `dispatcher.py`, add a new `elif` condition for your `api_mode`. When `settings.api_mode` matches your new agent's name (e.g., `'anthropic'`), it must import and call your new delegate's `run` function.

4.  **Declare in Settings**: In `setting.default.yml`, add your new `api_mode` name as a potential value. This makes the system aware of its existence. A user can then select it in their personal `setting.yml` to activate the entire chain.
