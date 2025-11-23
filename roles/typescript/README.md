# TypeScript Role Definitions for src/web

This directory contains clear role definitions for each layer in `src/web`. These define TypeScript-specific architecture patterns and conventions for the frontend application.

## 📚 Documentation Structure

### Overall Guidelines

- **[typescript.md](./typescript.md)** - Project-wide TypeScript conventions, forbidden patterns, core principles

### Layer-Specific Role Definitions

#### Web Layer (web/)

Frontend layer role definitions:

- **[api.md](./api.md)** - API integration and data fetching layer
- **[components/](./components/)** - Reusable UI component layer
- **[hooks/hooks.md](./hooks/hooks.md)** - Custom React hooks layer (detailed rules and patterns)
- **[rhf.md](./rhf.md)** - React Hook Form integration layer
- **[stores.md](./stores.md)** - State management layer

## 🏗️ Architecture Overview

This project adopts **Hook-Centric Advanced Atomic Design (HCAAD)**, an extension of Atomic Design that emphasizes custom hooks as the core of component logic. HCAAD organizes components into hierarchical layers while enforcing strict separation of concerns through hooks patterns.

```
┌─────────────────────────────────────────────┐
│ Web Layer (Frontend)                        │
│  ├─ Components (UI)                         │  ← Reusable UI components
│  ├─ Hooks (Logic)                           │  ← Custom React hooks
│  ├─ API (Integration)                       │  ← External API calls
│  ├─ Stores (State)                          │  ← Global state management
│  └─ Forms (Validation)                      │  ← Form handling & validation
└─────────────────────────────────────────────┘
```

### HCAAD Layer Responsibilities

Components are organized into four atomic layers with specific hook-based responsibilities. When deciding which layer a component belongs to, focus on the custom hooks it uses: no hooks for Atoms, local logic hooks for Molecules, integration hooks for Organisms, and store-level hooks for Pages. This hook-centric approach ensures clear separation of concerns and easy directory placement.

- **Atoms**: Basic UI primitives without custom hooks. These are pure, stateless components focused solely on presentation.
  - Examples: `Button`, `InputText`, `IconCopy`
  - Hooks: None (pure UI only)
  - Directory: `components/atoms/`

- **Molecules**: Composite components with pure logic hooks. These combine atoms and handle local state/UI logic without external dependencies.
  - Examples: `InputField`, `Select`, `Modal`
  - Hooks: `useHandlers` (local state), `useLifecycle` (computed values)
  - Directory: `components/molecules/`

- **Organisms**: Complex components that integrate with external systems. These orchestrate molecules and handle API calls or store interactions.
  - Examples: `ChatHistory`, `Form`, `SessionTree`
  - Hooks: `useActions` (API calls), `useHandlers`, `useLifecycle`
  - Directory: `components/organisms/`

- **Pages**: Top-level components responsible for global state management. These compose organisms and primarily manage store-level state.
  - Examples: `ChatHistoryPage`, `StartSessionPage`
  - Hooks: Store access (primary), `useActions`, `useLifecycle`
  - Directory: `pages/` or `components/pages/`

## MCP Server and Tools

### Starting the MCP Server

The MCP (Model Context Protocol) server allows AI assistants to interact with the pipe tools via standardized JSON-RPC communication.

To start the MCP server:

```bash
# If mcp_server is in your PATH
mcp_server

# Or using Python module
python -m pipe.cli.mcp_server
```

The server listens on stdin/stdout and can be connected to MCP-compatible clients like Claude Desktop.

### Available Tools

The following TypeScript-specific tools are available in the `tools/` directory:

- **ts_checker**: Checks TypeScript code for errors and provides diagnostics.
  - Usage: `ts_checker(file_path: str) -> dict`

- **ts_find_similar_code**: Finds similar code patterns in the TypeScript codebase.
  - Usage: `ts_find_similar_code(query: str) -> list`

- **ts_get_code_snippet**: Extracts code snippets for specific symbols (classes, functions) from a TypeScript file.
  - Usage: `ts_get_code_snippet(file_path: str, symbol_name: str) -> dict`

- **ts_get_references**: Finds all references to a specific symbol in the TypeScript codebase.
  - Usage: `ts_get_references(symbol_name: str) -> list`

- **ts_get_type_definitions**: Extracts type definitions for symbols in TypeScript files.
  - Usage: `ts_get_type_definitions(file_path: str, symbol_name: str) -> dict`

These tools enable AI assistants to perform code analysis, type checking, and reference finding tasks within the pipe project.

## 🎯 Key Principles

### 1. Component Architecture

- Use functional components with hooks
- Prefer composition over inheritance
- Keep components small and focused

### 2. State Management

- Use Zustand for global state
- Keep local state in components when possible
- Avoid prop drilling with context

### 3. Type Safety

- Strict TypeScript configuration
- Use interfaces for complex types
- Avoid `any` type

## 🎯 Quick Task Guide

**For LLMs: Start here to quickly find the right documentation.**

### Common Development Tasks

| Task                 | Read These (in order)            |
| -------------------- | -------------------------------- |
| **Add UI component** | 1. `components/` <br>2. `hooks/` |
| **Add API call**     | 1. `api.md`                      |
| **Add form**         | 1. `rhf.md`                      |
| **Add global state** | 1. `stores.md`                   |

## 📖 Usage Guide

### When Adding New Components

1. Check the appropriate layer documentation
2. Follow TypeScript and React best practices
3. Use the provided templates and examples

### During Code Review

1. Verify TypeScript types are correct
2. Check component composition
3. Ensure proper state management

## 🔍 Document Contents

### Quick Reference by Layer

| Layer           | Purpose          | Read When                         |
| --------------- | ---------------- | --------------------------------- |
| **api.md**      | API integration  | Adding external API calls         |
| **components/** | UI components    | Building reusable UI elements     |
| **hooks/**      | Custom hooks     | Sharing component logic           |
| **rhf.md**      | Form handling    | Adding forms with validation      |
| **stores.md**   | State management | Managing global application state |

## 🤝 Contributing

These role definitions are living documents. Improvement suggestions and new pattern additions are welcome.
