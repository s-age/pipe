[![License: CC0-1.0](https://img.shields.io/badge/License-CC0--1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
# pipe: A Clean Jailbreak from LLM Obfuscation

`pipe` is not another chat agent. It is a tool designed to give you, the developer, complete control over the conversational context. Unlike traditional clients that hide their history management in a black box, `pipe` empowers you to freely manipulate the history, extract what is essential, and achieve **true context engineering**.

This is a clean jailbreak tool from vendor obfuscation.

We employ a **minimal yet powerful** CLI-driven approach, focusing on the one thing that truly matters: ensuring the agent understands its purpose, history, and current task without ambiguity.

## Core Philosophy

### 1. Total Context Control

The prompt is reconstructed with a structured, self-describing **JSON Schema** for every call. This is inherently more token-efficient and understandable for an LLM. The entire history is transparent, saved in readable JSON session files. This ensures full **auditability** and gives the stateless LLM a persistent, and more importantly, **malleable** memory. You can retry, refine, edit, delete, and compress with surgical precision.

### 2. Uncompromising Extensibility

By default, `pipe` is based on `gemini-cli`, but this is merely an implementation detail. The core logic is decoupled. If you want to use the direct API, do it. If you want to use `claude-code`, do it. The framework is designed to be torn apart and rebuilt to your specifications.

### License: The Spirit of the Jailbreak

This project is released under the [CC0 1.0 Universal (CC0 1.0) Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).

Customize it as you wish. Jailbreak as you desire.

The purpose of this project is to be a **pipe to the agent**, and a **pipe to our followers** (the community).

-----

## Features

  * **Session-Based History:** Each conversation is a self-contained session, stored in a single, human-readable JSON file.
  * **Structured JSON Prompting:** Builds a detailed, self-describing JSON object as the final prompt, providing meta-context to the model for improved clarity.
  * **CLI-Driven Workflow:** A powerful command-line interface to start, continue, or compress sessions.
  * **Extensible Backend:** Defaults to `gemini-cli`, but the architecture allows for swapping out the execution agent.
  * **Configuration via YAML:** Configure model, context limits, and other settings in `setting.yml`.
  * **Token-Aware:** Calculates token count for each prompt and warns before exceeding limits.
  * **Dry Run Mode:** A `--dry-run` flag to inspect the final JSON prompt before sending it to the API.
  * **Web UI for Management:** The Web UI allows you to view a list of past conversation sessions and browse the detailed conversation history (turns) for each session. You can also intuitively perform management operations such as starting new chat sessions, deleting unnecessary sessions, editing the content of specific turns, and compressing sessions to reduce token count. Furthermore, you can send new instructions to existing sessions to continue the conversation. Metadata such as session purpose and background can also be edited.
  * **Safe Operations:** Automatic backups are created before any edit or compression operation.
  * **Language Support:** Allows specifying the language for agent responses.
  * **YOLO Mode:** Automatically accept all actions (aka YOLO mode, see [https://www.youtube.com/watch?v=xvFZjo5PgG0](https://www.youtube.com/watch?v=xvFZjo5PgG0) for more details).

-----

## Setup & Installation

1.  **Prerequisites:** Python 3.x and `gemini-cli` installed in your PATH.
2.  **Install Dependencies:** `pip3 install -r requirements.txt`
3.  **Set up API Key:** Create a `.env` file (you can copy `.env.default`).
    *   For consistency with `.env.default`, add `GEMINI_API_KEY='YOUR_API_KEY_HERE'`.
    *   For CLI usage, ensure `GOOGLE_API_KEY` is set in your environment (e.g., `export GOOGLE_API_KEY='YOUR_API_KEY_HERE'`) as `conductor.py` expects this variable.

-----

## Usage: 3 Routes to Context Engineering

The **pipe** framework offers three primary routes, optimized for different user environments and goals, all built on the same structured core.

### 1. Route 1: Python Script (Automation & CLI)

This route is ideal for **automation, scripting, and CLI-focused developers** who need reliable, repeatable execution.

| Use Case | Description |
| :--- | :--- |
| **Start New Session** | Define the complete context (`--purpose`, `--background`, `--roles`) and first instruction. |
| **Continue Session** | Specify an existing `<SESSION_ID>` and add a new instruction. This is the primary way to give the short-lived agent "memory." |
| **Compress History** | Use the `--compress` flag to efficiently replace long history with a summary. |
| **Debug/Cost Control** | Use the `--dry-run` flag to inspect the generated JSON prompt before the API call. |

**Examples:**

```bash
# Start New Session Example
python3 conductor.py --purpose "Create a new React component" --background "..." --roles "roles/engineer.md" --instruction "Create a 'UserProfile' component."

# Continue Session Example
python3 conductor.py --session <SESSION_ID> --instruction "Now, add a state for loading."
```

### 2. Route 2: Web UI (Management & Human-in-the-Loop)

This is best for users seeking **intuitive visual management** and **direct manipulation of history** without file editing.

| Use Case | Description |
| :--- | :--- |
| **View/Edit History** | Browse detailed session histories; surgically edit specific turns or session metadata (purpose/background). |
| **Continue Sessions** | Use form inputs to send new instructions to existing sessions. |
| **Management** | Intuitively start new sessions, compress history, or delete unnecessary sessions via a graphical interface. |

**Example (Start Server):**

```bash
python3 app.py
```

*(Navigate to `http://127.0.0.1:5001` in your browser)*

### 3. Route 3: Execution from Agent (Orchestration)

This is for **advanced AI system builders** leveraging **pipe's** full context control capabilities for multi-agent coordination.

| Use Case | Description |
| :--- | :--- |
| **Role Delegation** | A parent agent assigns the **Conductor role** to a child agent and delegates the task using the structured command format. |
| **Small-Scale Orchestration** | **By customizing the role definition**, the Conductor role can be programmed to divide complex tasks into subtasks and recursively delegate them to different execution agents with specific roles. |
| **Clean Execution** | The delegated task is passed as a **structured JSON prompt**, ensuring maximum efficiency for the short-lived sub-agent. |

**Execution Example (Delegation from Parent Agent):**

> **[IMPORTANT] The following command examples are not intended to be executed directly in the user's terminal. They are used as instructions to an already launched parent agent (such as Gemini) to assign the Conductor role and delegate tasks.**

```bash
Act as @roles/conductor.md python3 conductor.py --session <SESSION_ID> --instruction "Now, add a state for loading."
```

## Dry Run Output Example

When running `conductor.py` with the `--dry-run` flag, the generated JSON prompt is displayed. This JSON object represents the structured input that would be sent to the AI sub-agent. It can be useful for understanding how `pipe` constructs its prompts or for direct experimentation with AI models.

Here's an example of a generated prompt:

Note that the JSON presented here is pretty-printed for readability; the actual output from `conductor.py --dry-run` is a single-line JSON string.

```json
{
  "description": "JSON object representing the entire request to the AI sub-agent. The agent's goal is to accomplish the 'current_task' based on all provided context.",
  "main_instruction": "When you receive JSON data, process your thoughts according to the following flowchart:\n\n```mermaid\ngraph TD\n    A[\"Start: JSON Input\"] --> B[\"Step 1: Read 'current_task.instruction' to identify task objective\"];\n    B --> C[\"Step 2: Extract relevant information from the latest turns in 'conversation_history.turns'\"];\n    C --> D[\"Step 3: Integrate extracted task instructions and historical information, then summarize the current context\"];\n    D --> E[\"Step 4: Based on the summarized information, think and plan for response generation\"];\n    E --> F[\"Step 5: Generate final response based on the plan\"];\n    F --> G[\"End: Output Response\"];\n```",
  "hyperparameters": {
    "description": "Contextual instructions to control the AI model's generation process. The model should strive to follow these instructions.",
    "temperature": {
      "type": "number",
      "value": 0.2,
      "description": "Be precise and factual. A lower value is preferred for deterministic output."
    },
    "top_p": {
      "type": "number",
      "value": 0.5,
      "description": "Consider a broad range of possibilities, but adhere strictly to the temperature setting."
    },
    "top_k": {
      "type": "number",
      "value": 5,
      "description": "Limit the generation to the top 5 most likely tokens at each step."
    }
  },
  "session_goal": {
    "description": "The immutable purpose and background for this entire conversation session.",
    "purpose": "Implementation of src/components/atoms/Button",
    "background": "Component preparation for starting a React project"
  },
  "response_constraints": {
    "description": "Constraints that the AI sub-agent should adhere to when generating responses. The entire response, including all content, must be generated in the specified language.",
    "language": "Japanese"
  },
  "roles": {
    "description": "A list of personas or role definitions that the AI sub-agent should conform to.",
    "definitions": [
      "# Role: Software Engineer\n\nYou are a professional software engineer. Your primary goal is to write clean, efficient, and maintainable code based on the provided instructions and context. Adhere to best practices and coding standards relevant to the specified language.\n"
    ]
  },
  "conversation_history": {
    "description": "Historical record of past interactions in this session, in chronological order.",
    "turns": []
  },
  "current_task": {
    "description": "The specific task that the AI sub-agent must currently execute.",
    "instruction": "I want to create a Button component using React, Atomic Design, and Vanilla Extract"
  },
  "reasoning_process": "```mermaid\ngraph TD\n    A([\"Start: JSON Input\"]) --> B[\"Step 1: Read 'current_task.instruction' to identify task objective\"];\n    B --> C[\"Step 2: Derive general principles behind the task (Step-Back)\"];\n    C --> D[\"Step 3: Extract relevant information from the latest turns in 'conversation_history.turns'\"];\n    D --> E[\"Step 4: Integrate extracted task instructions, principles, and historical information, then summarize the current context\"];\n    E --> F[\"Step 5: Based on the summarized information, think and plan for response generation\"];\n    F --> G{\"Decision: Are there any contradictions or leaps in logic?\"};\n    G -- NO --> E;\n    G -- YES --> H[\"Step 6: Re-examine the reasoning path from multiple perspectives and confirm the robustness of the conclusion (Self-Consistency)\"];\n    H --> I[\"Step 7: Generate the final response based on the plan\"];\n    I --> J{\"Decision: Does it meet the initial requirements (format/purpose)?\"};\n    J -- NO --> F;\n    J -- YES --> K([\"End: Output Response\"]);\n```"
}