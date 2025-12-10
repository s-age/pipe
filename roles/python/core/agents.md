# Agents Layer

## Purpose

Agents handle **external AI model integrations**. They wrap LLM APIs, manage tool calling, and handle streaming responses.

## Responsibilities

1. **LLM Integration** - Call external AI APIs
2. **Tool Management** - Register and execute tools
3. **Streaming** - Handle streaming responses
4. **Error Handling** - Retry logic and error recovery
5. **Context Management** - Manage conversation context

## Rules

### ✅ DO

- Wrap external API calls
- Handle streaming and non-streaming modes
- Implement retry logic
- Convert API responses to internal models
- Register tools dynamically

### ❌ DON'T

- **NO business logic** - Only API integration
- **NO persistence** - Use services/repositories
- **NO domain logic** - Use domains
- **NO complex orchestration** - Agents are called BY services

## File Structure

```
agents/
├── base_agent.py         # Abstract base
├── anthropic_agent.py    # Claude integration
├── openai_agent.py       # OpenAI integration
└── ...
```

## Dependencies

**Allowed:**
- ✅ External SDKs (anthropic, openai)
- ✅ Core Models (for types)
- ✅ Tools (for registration)
- ✅ Standard library

**Forbidden:**
- ❌ Services
- ❌ Repositories
- ❌ Domains directly

## Example

```python
"""Anthropic Claude agent."""

from anthropic import Anthropic
from pipe.core.agents.base_agent import BaseAgent
from pipe.core.models.turn import Turn

class AnthropicAgent(BaseAgent):
    """
    Claude API integration.
    
    Handles:
    - Message API calls
    - Tool calling
    - Streaming responses
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.tools = []
    
    def register_tool(self, tool: Tool) -> None:
        """Register tool for agent use."""
        self.tools.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.parameters
        })
    
    def run(self, messages: list[dict], stream: bool = False) -> Turn:
        """
        Call Claude API.
        
        Args:
            messages: Conversation history
            stream: Enable streaming
            
        Returns:
            Turn with model response
        """
        try:
            if stream:
                return self._run_streaming(messages)
            else:
                return self._run_sync(messages)
        except Exception as e:
            return Turn(
                type="error",
                content=f"API error: {str(e)}"
            )
    
    def _run_sync(self, messages: list[dict]) -> Turn:
        """Synchronous API call."""
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            max_tokens=4096
        )
        
        return Turn(
            type="model_response",
            content=response.content[0].text,
            metadata={
                "model": self.model,
                "usage": response.usage.model_dump()
            }
        )
    
    def _run_streaming(self, messages: list[dict]) -> Turn:
        """Streaming API call."""
        content = []
        
        with self.client.messages.stream(
            model=self.model,
            messages=messages,
            tools=self.tools,
            max_tokens=4096
        ) as stream:
            for text in stream.text_stream:
                content.append(text)
                yield text  # Stream to caller
        
        return Turn(
            type="model_response",
            content="".join(content)
        )
```

## Common Patterns

### Pattern 1: Retry Logic

```python
def run(self, messages: list[dict]) -> Turn:
    """Run with retry."""
    for attempt in range(3):
        try:
            return self._call_api(messages)
        except RateLimitError:
            time.sleep(2 ** attempt)
    raise Exception("Max retries exceeded")
```

### Pattern 2: Tool Execution

```python
def execute_tool(self, tool_name: str, params: dict) -> dict:
    """Execute tool by name."""
    tool = self._get_tool(tool_name)
    return tool.execute(**params)
```

## Testing

```python
# tests/core/agents/test_anthropic_agent.py

def test_agent_calls_api(mock_client):
    """Test agent calls Anthropic API."""
    agent = AnthropicAgent(api_key="test")
    agent.client = mock_client
    
    turn = agent.run([{"role": "user", "content": "Hello"}])
    
    assert turn.type == "model_response"
    mock_client.messages.create.assert_called_once()

def test_agent_registers_tools():
    """Test agent registers tools correctly."""
    agent = AnthropicAgent(api_key="test")
    tool = MockTool(name="test_tool")
    
    agent.register_tool(tool)
    
    assert len(agent.tools) == 1
    assert agent.tools[0]["name"] == "test_tool"
```

## Summary

**Agents:**
- ✅ External API integration
- ✅ Tool management
- ✅ Streaming support
- ✅ Error handling with retry
- ❌ No business logic or persistence

**Agents wrap external APIs, services orchestrate them**
