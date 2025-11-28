# Extending Pipe

This guide explains how to extend the `pipe` framework by adding new agents and integrations.

## Adding New Agents

To add support for a new AI agent (e.g., Claude API, Claude Code, or other LLM providers), follow these steps:

### 1. Create Agent Implementation

Create a new Python file in `src/pipe/core/agents/` for your agent. Use existing agents like `gemini_api.py` or `gemini_cli.py` as references.

Example structure for `claude_api.py`:

```python
import requests
from typing import Dict, Any
from src.pipe.core.models import AgentResponse

class ClaudeApiAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def execute(self, prompt: str, **kwargs) -> AgentResponse:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return AgentResponse(
            content=result["content"][0]["text"],
            metadata={"model": "claude-3-sonnet", "usage": result.get("usage", {})}
        )
```

### 2. Update Dispatcher

Add your new agent to `src/pipe/core/dispatcher.py`. Import your agent class and add it to the agent mapping.

Example:

```python
from src.pipe.core.agents.claude_api import ClaudeApiAgent

# In the dispatcher class
def get_agent(self, agent_type: str):
    agents = {
        "gemini_api": GeminiApiAgent,
        "gemini_cli": GeminiCliAgent,
        "claude_api": ClaudeApiAgent,  # Add your new agent
    }
    return agents[agent_type](**self.config)
```

### 3. Create Prompt Template

Create a new Jinja2 template in `templates/prompt/` based on `gemini_api_prompt.j2`. Adapt it for your agent's specific requirements.

Example `claude_api_prompt.j2`:

```jinja2
You are Claude, an AI assistant built by Anthropic.

{% include 'roles.j2' %}
{% include 'description.j2' %}
{% include 'constraints.j2' %}
{% include 'conversation_history.j2' %}
{% include 'current_task.j2' %}

Please respond as Claude would, following the guidelines above.
```

### 4. Update Configuration

Add support for your new agent in the configuration system (`setting.yml` or environment variables). Ensure API keys and other settings are properly handled.

### 5. Add Tests

Create unit tests for your new agent in the `tests/` directory, following the existing test patterns.

## Best Practices

- Follow the existing code style and patterns
- Handle errors gracefully and provide meaningful error messages
- Include proper logging for debugging
- Document your agent implementation
- Test with various prompt sizes and edge cases

## Example: Adding Claude Code Integration

For integrating with Claude Code (similar to Gemini CLI):

1. Create `src/pipe/core/agents/claude_code.py`
2. Implement CLI interaction logic
3. Add to dispatcher as "claude_code"
4. Create appropriate prompt template
5. Update configuration options

For more information on the codebase structure, see [docs/development.md](development.md).
