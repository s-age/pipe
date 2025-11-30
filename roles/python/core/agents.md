# Agents Layer

## Purpose

Agents are the **sole interface** to external AI services. They wrap API calls to services like Google Gemini, translating our structured, deterministic world into the probabilistic realm of LLMs and back again.

## Responsibilities

1. **API Wrapper** - Encapsulate all direct API calls to external AI services
2. **Request Translation** - Convert internal structured data (prompts, tools) to API format
3. **Response Parsing** - Transform API responses back to internal models
4. **Error Handling** - Handle API-specific errors and retries
5. **Tool Schema Generation** - Generate function call schemas from tool definitions

## Characteristics

- ✅ Direct API calls (google.genai, CLI tools, etc.)
- ✅ Convert between internal models and API formats
- ✅ Handle API authentication and configuration
- ✅ Implement retry logic and error handling
- ✅ Parse streaming responses when needed
- ❌ **NO business logic** - only translation and communication
- ❌ **NO state management** - agents are stateless
- ❌ **NO prompt construction** - that's PromptService's job
- ❌ **NO session management** - that's SessionService's job

## File Structure

```
agents/
├── __init__.py
├── gemini_api.py        # Google Gemini API wrapper
├── gemini_cli.py        # CLI-based Gemini interaction
└── search_agent.py      # Web search capabilities
```

## Dependencies

**Allowed:**

- ✅ `models/` - For type definitions (Session, Turn, etc.)
- ✅ `services/prompt_service` - For prompt construction
- ✅ `services/token_service` - For token counting
- ✅ `utils/` - For datetime, file utilities
- ✅ External libraries (google.genai, requests, etc.)

**Forbidden:**

- ❌ `domains/` - Business logic doesn't belong here
- ❌ `repositories/` - No direct persistence
- ❌ `services/session_service` - Avoid circular dependencies

## Template

```python
"""
Agent for interacting with [External Service Name].
"""

import logging
from typing import Any

from pipe.core.models.turn import Turn, ModelResponseTurn, FunctionCallingTurn
from pipe.core.utils.datetime import get_current_timestamp

logger = logging.getLogger(__name__)


def call_external_service(
    prompt: str,
    tools: list[dict[str, Any]],
    hyperparameters: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    """
    Calls external AI service and returns response.

    Args:
        prompt: Formatted prompt text
        tools: List of tool definitions in API format
        hyperparameters: Model configuration (temperature, etc.)

    Returns:
        Tuple of (response_text, tool_calls)

    Raises:
        RuntimeError: If API call fails
    """
    logger.debug(f"Calling external service with prompt length: {len(prompt)}")

    try:
        # 1. Configure API client
        client = ExternalAPIClient(api_key=os.getenv("API_KEY"))

        # 2. Make API call
        response = client.generate(
            prompt=prompt,
            tools=tools,
            **hyperparameters
        )

        # 3. Parse response
        response_text = response.text
        tool_calls = response.tool_calls or []

        logger.debug(f"Response received: {len(response_text)} chars, {len(tool_calls)} tool calls")

        return response_text, tool_calls

    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise RuntimeError(f"Failed to call external service: {e}") from e


def load_tools(project_root: str) -> list[dict[str, Any]]:
    """
    Scans tools directory and generates tool schemas for API.

    Args:
        project_root: Path to project root

    Returns:
        List of tool definitions in API format
    """
    tools = []
    tools_dir = os.path.join(project_root, "src", "pipe", "core", "tools")

    # Scan directory and build schemas
    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            # Generate schema from function signature
            tool_schema = _generate_tool_schema(filename)
            tools.append(tool_schema)

    return tools
```

## Real Examples

### gemini_api.py - Google Gemini API Wrapper

**Key Responsibilities:**

- Configure Google Gemini client
- Build content history from turns
- Generate tool schemas from Python functions
- Execute API calls with retry logic
- Parse streaming responses

```python
import google.genai as genai
from google.genai import types

def call_gemini_api(
    session_service: SessionService,
    prompt_service: PromptService,
    session_id: str,
    model_name: str,
    settings: Settings,
    project_root: str,
) -> None:
    """
    Main entry point for Gemini API interaction.
    """
    # 1. Get structured prompt from PromptService
    prompt_obj = prompt_service.build_prompt_for_gemini(session_id)

    # 2. Load and convert tools
    tools = load_tools(project_root)

    # 3. Configure client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # 4. Build content history
    contents = _build_contents_from_turns(prompt_obj.conversation_history)

    # 5. Execute API call
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=prompt_obj.hyperparameters.temperature,
            tools=tools,
            system_instruction=prompt_obj.system_instruction,
        ),
    )

    # 6. Parse and save response
    _process_response(response, session_service, session_id)
```

**Tool Schema Generation:**

```python
def load_tools(project_root: str) -> list:
    """
    Scans the 'tools' directory and generates JSON schemas.
    This is agent-specific logic - converting Python type hints
    to Gemini API's expected format.
    """
    tool_defs = []
    type_mapping = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
    }

    tools_dir = os.path.join(project_root, "src", "pipe", "core", "tools")

    for filename in os.listdir(tools_dir):
        if not filename.endswith(".py") or filename.startswith("_"):
            continue

        module_name = filename[:-3]
        spec = importlib.util.spec_from_file_location(
            module_name, os.path.join(tools_dir, filename)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get function and generate schema
        func = getattr(module, module_name)
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        # Build parameter schema
        params = {}
        required = []
        for param_name, param in sig.parameters.items():
            if param_name in CONTEXT_PARAMS:
                continue  # Skip injected context

            param_type = type_hints.get(param_name, str)
            params[param_name] = {
                "type": type_mapping.get(param_type, "string"),
                "description": f"Parameter {param_name}",
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        # Create tool definition
        tool_defs.append({
            "name": module_name,
            "description": func.__doc__ or f"Tool {module_name}",
            "parameters": {
                "type": "object",
                "properties": params,
                "required": required,
            },
        })

    return tool_defs
```

### gemini_cli.py - CLI-based Gemini Interaction

**Key Responsibilities:**

- Build CLI command with arguments
- Execute subprocess
- Parse YAML/JSON output
- Handle CLI-specific errors

```python
def call_gemini_cli(
    session_service: SessionService,
    prompt_service: PromptService,
    session_id: str,
    model_name: str,
    settings: Settings,
    project_root: str,
) -> None:
    """
    Calls Gemini via CLI tool instead of API.
    Useful for local development or when API is unavailable.
    """
    # 1. Build prompt
    prompt_obj = prompt_service.build_prompt_for_gemini(session_id)

    # 2. Build CLI command
    cmd = [
        "gemini",
        "--model", model_name,
        "--temperature", str(prompt_obj.hyperparameters.temperature),
    ]

    # Add system instruction
    if prompt_obj.system_instruction:
        cmd.extend(["--system", prompt_obj.system_instruction])

    # 3. Execute subprocess
    result = subprocess.run(
        cmd,
        input=prompt_obj.user_instruction,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"CLI call failed: {result.stderr}")

    # 4. Parse response
    response_text = result.stdout

    # 5. Save to session
    session = session_service.get_session(session_id)
    session.add_turn(ModelResponseTurn(
        timestamp=get_current_timestamp(),
        message=response_text,
    ))
    session_service.save_session(session)
```

## Error Handling Patterns

### Retry Logic

```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_api_call(
    func: Callable[..., T],
    max_retries: int = 3,
    backoff_factor: float = 2.0,
) -> T:
    """
    Retries API call with exponential backoff.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            wait_time = backoff_factor ** attempt
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

    raise RuntimeError("Max retries exceeded")
```

### API-Specific Error Handling

```python
def call_gemini_api(...) -> None:
    try:
        response = client.models.generate_content(...)
        _process_response(response, ...)

    except genai.errors.ResourceExhausted:
        logger.error("API quota exceeded")
        raise RuntimeError("Gemini API quota exceeded. Please try again later.")

    except genai.errors.InvalidArgument as e:
        logger.error(f"Invalid API argument: {e}")
        raise ValueError(f"Invalid API configuration: {e}") from e

    except Exception as e:
        logger.error(f"Unexpected API error: {e}")
        raise RuntimeError(f"Failed to call Gemini API: {e}") from e
```

## Testing

### Mocking External APIs

```python
# tests/core/agents/test_gemini_api.py
from unittest.mock import Mock, patch
import pytest

@patch('google.genai.Client')
def test_call_gemini_api(mock_client_class):
    # Setup mocks
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_response = Mock(text="Response text", tool_calls=[])
    mock_client.models.generate_content.return_value = mock_response

    # Call agent
    call_gemini_api(
        session_service=mock_session_service,
        prompt_service=mock_prompt_service,
        session_id="test",
        model_name="gemini-2.0-flash",
        settings=mock_settings,
        project_root="/test",
    )

    # Verify API was called
    mock_client.models.generate_content.assert_called_once()
```

## Best Practices

### 1. Keep Agents Thin

Agents should be thin wrappers. Complex logic belongs elsewhere:

```python
# ❌ BAD: Business logic in agent
def call_gemini_api(...):
    prompt = _build_complex_prompt(...)  # This should be in PromptService
    response = client.generate(prompt)
    _validate_response(response)  # This might belong in domains/
    return response

# ✅ GOOD: Agent only handles API communication
def call_gemini_api(...):
    prompt_obj = prompt_service.build_prompt(...)  # Service handles this
    response = client.generate(prompt_obj.text)
    return response
```

### 2. Log API Interactions

Always log API calls for debugging:

```python
logger.debug(f"API Request: model={model_name}, prompt_length={len(prompt)}")
logger.debug(f"API Response: status=success, length={len(response.text)}")
```

### 3. Handle Streaming Properly

For streaming responses, yield chunks:

```python
def call_gemini_streaming(...) -> Iterator[str]:
    """
    Streams response from Gemini API.
    """
    response = client.models.generate_content_stream(...)

    for chunk in response:
        if chunk.text:
            yield chunk.text
```

### 4. Environment Configuration

Use environment variables for API keys:

```python
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")
```

### 5. Agent-Specific Prompt Adjustments

Different AI models may require subtle prompt adjustments for optimal performance. Here are some tips for common models:

#### Claude (Anthropic)

- **Issue**: Claude tends to ignore `current_task` and prioritizes previous instructions in `conversation_history`.
- **Solution**: Append the current instruction to the end of `conversation_history` instead of sending it separately as `current_task`. This ensures Claude processes the most recent instruction correctly.
- **Implementation**: Modify the prompt construction to merge `current_task` into the last turn of `conversation_history` when using Claude models.

#### General Tips

- **Test Prompt Variations**: Always test your prompt structure with `--dry-run` to see how different models interpret the JSON structure.
- **Model-Specific Tuning**: Adjust hyperparameters and prompt formatting based on the target model's known behaviors.
- **Fallback Strategies**: Implement model-specific fallbacks if the primary prompt structure doesn't work well.

## Summary

Agents are the **boundary layer** between our deterministic system and external AI services:

- ✅ Sole interface to external APIs
- ✅ Stateless translation layer
- ✅ Handle API-specific errors and retries
- ✅ Generate tool schemas from code
- ❌ No business logic
- ❌ No state management
- ❌ No prompt construction

Keep agents thin, focused, and isolated from the rest of the system.
