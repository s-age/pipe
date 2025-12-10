# Agent Registry Pattern

## Overview

The agent system uses a **Registry Pattern** with auto-discovery to enable plugin-like extensibility. New agents can be added without modifying the dispatcher code, following the Open/Closed Principle.

## Architecture

### Components

1. **BaseAgent** (`src/pipe/core/agents/base.py`)
   - Abstract base class defining the agent interface
   - All agents must implement the `run()` method

2. **Registry** (`src/pipe/core/agents/__init__.py`)
   - `@register_agent(key)` decorator for registration
   - `get_agent_class(key)` to retrieve agents
   - Auto-discovery using `pkgutil.walk_packages()`

3. **Dispatcher** (`src/pipe/core/dispatcher.py`)
   - Uses registry to dynamically load agents
   - No hardcoded if/elif branches

## Adding a New Agent

### Example: Adding Claude API Support

1. **Create a new file** `src/pipe/core/agents/claude_api.py`:

```python
from pipe.core.agents import register_agent
from pipe.core.agents.base import BaseAgent
from pipe.core.models.args import TaktArgs
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService


@register_agent("claude-api")
class ClaudeApiAgent(BaseAgent):
    """Agent for Anthropic Claude API."""

    def run(
        self,
        args: TaktArgs,
        session_service: SessionService,
        prompt_service: PromptService,
    ) -> tuple[str, int | None, list]:
        """Execute the Claude API agent.

        Args:
            args: Command line arguments
            session_service: Service for session management
            prompt_service: Service for prompt building

        Returns:
            Tuple of (response_text, token_count, turns_to_save)
        """
        # Your implementation here
        model_response_text = "Hello from Claude!"
        token_count = 42
        turns_to_save = []

        return model_response_text, token_count, turns_to_save
```

2. **That's it!** The agent is automatically registered and available.

3. **Use it** by setting `api_mode: claude-api` in `setting.yml`:

```yaml
api_mode: claude-api
```

## Benefits

### 1. **Extensibility (Open/Closed Principle)**

- Add new agents without modifying existing code
- Dispatcher doesn't need to know about specific agents

### 2. **Decoupling**

- Agents are self-contained modules
- No circular dependencies in dispatch logic

### 3. **Maintainability**

- Each agent file focuses on a single responsibility
- Easy to locate and modify agent-specific code

### 4. **Discoverability**

- Auto-discovery eliminates manual registration
- LSP-friendly (autocomplete, go-to-definition work)

## Current Registered Agents

You can see all registered agents at runtime:

```python
from pipe.core.agents import AGENT_REGISTRY
print(sorted(AGENT_REGISTRY.keys()))
# Output: ['gemini-api', 'gemini-cli']
```

## Error Handling

If an invalid `api_mode` is specified, the system provides a helpful error:

```python
from pipe.core.agents import get_agent_class

try:
    get_agent_class('unknown-mode')
except ValueError as e:
    print(e)
    # Unknown api_mode: 'unknown-mode'.
    # Available agents: [gemini-api, gemini-cli]
```

## Implementation Details

### Auto-Discovery Mechanism

The `__init__.py` uses `pkgutil.walk_packages()` to automatically import all Python modules in the `agents/` directory:

```python
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    if module_name in ("base",):  # Skip base module
        continue
    try:
        importlib.import_module(f".{module_name}", __package__)
    except Exception:
        # Silently skip modules with missing dependencies
        pass
```

This triggers the `@register_agent` decorators, populating the `AGENT_REGISTRY`.

### Dispatcher Integration

The dispatcher uses the registry polymorphically:

```python
from pipe.core.agents import get_agent_class

# Get agent class from registry
AgentClass = get_agent_class(api_mode)

# Instantiate and execute (no branching needed)
agent_instance = AgentClass()
model_response_text, token_count, turns_to_save = agent_instance.run(
    args, session_service, prompt_service
)
```

## Testing

When writing tests for agents, you can mock the agent directly:

```python
@patch("pipe.core.agents.gemini_api.GeminiApiAgent.run",
       return_value=("response", 100, []))
def test_my_feature(self, mock_agent_run):
    # Your test code
    pass
```

## Migration Notes

### Old Implementation (Before Registry Pattern)

```python
if api_mode == "gemini-api":
    from .delegates import gemini_api_delegate
    result = gemini_api_delegate.run(...)
elif api_mode == "gemini-cli":
    from .delegates import gemini_cli_delegate
    result = gemini_cli_delegate.run(...)
else:
    raise ValueError(f"Unknown api_mode: {api_mode}")
```

### New Implementation (Registry Pattern)

```python
from pipe.core.agents import get_agent_class

AgentClass = get_agent_class(api_mode)
agent_instance = AgentClass()
result = agent_instance.run(args, session_service, prompt_service)
```

## Best Practices

1. **Naming Convention**: Use descriptive names like `{provider}_{interface}.py`
   - Examples: `gemini_api.py`, `claude_api.py`, `openai_api.py`

2. **Error Handling**: Agents should raise meaningful exceptions
   - Use `RuntimeError` for API failures
   - Use `ValueError` for invalid configuration

3. **Documentation**: Include docstrings for the agent class and `run()` method

4. **Dependencies**: Handle optional dependencies gracefully
   - The auto-discovery silently skips modules that fail to import
   - Add dependency checks in the agent's `run()` method if needed

5. **Testing**: Write unit tests for each agent
   - Test the `run()` method with various scenarios
   - Mock external API calls

## Future Enhancements

Potential improvements to the registry pattern:

1. **Agent Metadata**: Store additional info (description, version, dependencies)
2. **Dynamic Loading**: Load agents on-demand rather than at import time
3. **Agent Configuration**: Per-agent settings validation
4. **Plugin System**: Load agents from external packages
