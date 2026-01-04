# Web Controllers Layer Testing Strategy

**Layer:** `src/pipe/web/controllers/`

## Responsibilities
- Orchestrate multiple actions to fulfill complex business logic
- Aggregate data from multiple sources (actions, services)
- Handle cross-cutting concerns like error handling and response formatting
- Coordinate between different parts of the application

## Testing Strategy
- **Use Mocks**: Controllers orchestrate actions and services, so we mock dependencies
- **Focus**: Integration of multiple actions, error handling, response structure, business logic coordination
- **Monkeypatch**: Use monkeypatch to inject mock actions and dependencies

## Test Patterns

### Basic Controller Test Structure

```python
# tests/unit/web/controllers/test_session_chat_controller.py
from unittest.mock import Mock, MagicMock
import pytest
from pipe.web.controllers.session_chat_controller import SessionChatController
from pipe.web.action_responses import (
    SessionTreeResponse,
    SessionOverview,
    SessionTreeNode,
    SettingsResponse,
    SettingsInfo,
)
from pipe.web.responses import ApiResponse
from pipe.web.responses.session_chat_responses import ChatContextResponse
from pipe.web.exceptions import HttpException, NotFoundError
from pipe.core.models.session import Session
from pipe.core.models.hyperparameters import Hyperparameters


class TestSessionChatController:
    """Tests for the SessionChatController class."""

    @pytest.fixture
    def mock_session_service(self):
        """Create a mock session service."""
        return Mock()

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return Mock()

    @pytest.fixture
    def controller(self, mock_session_service, mock_settings):
        """Create a SessionChatController instance with mocked dependencies."""
        return SessionChatController(
            session_service=mock_session_service, settings=mock_settings
        )

    def test_initialization(self, mock_session_service, mock_settings):
        """Test that the controller can be initialized."""
        controller = SessionChatController(
            session_service=mock_session_service, settings=mock_settings
        )
        assert controller.session_service == mock_session_service
        assert controller.settings == mock_settings
```

### Testing Happy Path with Multiple Actions

```python
def test_get_chat_context_without_session_id(
    self,
    controller,
    sample_session_tree_response,
    sample_settings_response,
    monkeypatch,
):
    """Test getting chat context without a specific session ID."""
    # Mock SessionTreeAction
    mock_tree_action = Mock()
    mock_tree_action.execute.return_value = sample_session_tree_response
    mock_tree_action_class = Mock(return_value=mock_tree_action)

    # Mock SettingsGetAction
    mock_settings_action = Mock()
    mock_settings_action.execute.return_value = sample_settings_response
    mock_settings_action_class = Mock(return_value=mock_settings_action)

    # Patch the action classes
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SessionTreeAction",
        mock_tree_action_class,
    )
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SettingsGetAction",
        mock_settings_action_class,
    )

    response, status_code = controller.get_chat_context(session_id=None)

    assert status_code == 200
    assert isinstance(response, ApiResponse)
    assert response.success is True
    assert isinstance(response.data, ChatContextResponse)
    assert response.data.sessions == sample_session_tree_response.sessions
    assert response.data.session_tree == sample_session_tree_response.session_tree
    assert response.data.settings == sample_settings_response.settings
    assert response.data.current_session is None
```

### Testing with dispatch_action

```python
def test_get_chat_context_with_valid_session_id(
    self,
    controller,
    sample_session_tree_response,
    sample_settings_response,
    sample_session,
    monkeypatch,
):
    """Test getting chat context with a valid session ID."""
    # Mock SessionTreeAction
    mock_tree_action = Mock()
    mock_tree_action.execute.return_value = sample_session_tree_response
    mock_tree_action_class = Mock(return_value=mock_tree_action)

    # Mock SettingsGetAction
    mock_settings_action = Mock()
    mock_settings_action.execute.return_value = sample_settings_response
    mock_settings_action_class = Mock(return_value=mock_settings_action)

    # Mock dispatch_action to return session data
    mock_dispatch = Mock(return_value=({"data": sample_session}, 200))

    # Patch the action classes and dispatch_action
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SessionTreeAction",
        mock_tree_action_class,
    )
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SettingsGetAction",
        mock_settings_action_class,
    )
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.dispatch_action",
        mock_dispatch,
    )

    response, status_code = controller.get_chat_context(session_id="session-1")

    assert status_code == 200
    assert isinstance(response, ApiResponse)
    assert response.success is True
    assert isinstance(response.data, ChatContextResponse)
    assert response.data.current_session == sample_session
    mock_dispatch.assert_called_once()
```

### Testing Error Handling - HttpException

```python
def test_get_chat_context_with_nonexistent_session_id(
    self,
    controller,
    sample_session_tree_response,
    sample_settings_response,
    monkeypatch,
):
    """Test getting chat context with a nonexistent session ID still returns tree and settings."""
    # Mock SessionTreeAction
    mock_tree_action = Mock()
    mock_tree_action.execute.return_value = sample_session_tree_response
    mock_tree_action_class = Mock(return_value=mock_tree_action)

    # Mock SettingsGetAction
    mock_settings_action = Mock()
    mock_settings_action.execute.return_value = sample_settings_response
    mock_settings_action_class = Mock(return_value=mock_settings_action)

    # Mock dispatch_action to raise NotFoundError
    def mock_dispatch_raises(*args, **kwargs):
        raise NotFoundError("Session not found")

    # Patch the action classes and dispatch_action
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SessionTreeAction",
        mock_tree_action_class,
    )
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SettingsGetAction",
        mock_settings_action_class,
    )
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.dispatch_action",
        mock_dispatch_raises,
    )

    response, status_code = controller.get_chat_context(
        session_id="nonexistent-session"
    )

    # Should still return 200 with tree and settings, but no current_session
    assert status_code == 200
    assert isinstance(response, ApiResponse)
    assert response.success is True
    assert isinstance(response.data, ChatContextResponse)
    assert response.data.sessions == sample_session_tree_response.sessions
    assert response.data.session_tree == sample_session_tree_response.session_tree
    assert response.data.settings == sample_settings_response.settings
    assert response.data.current_session is None
```

### Testing Error Handling - Actions Raising Exceptions

```python
def test_get_chat_context_tree_action_raises_http_exception(
    self, controller, monkeypatch
):
    """Test that HttpException from tree action is handled properly."""
    # Mock SessionTreeAction to raise InternalServerError
    from pipe.web.exceptions import InternalServerError

    def mock_tree_action_raises(*args, **kwargs):
        raise InternalServerError("Tree error")

    mock_tree_action_instance = Mock()
    mock_tree_action_instance.execute = mock_tree_action_raises
    mock_tree_action_class = Mock(return_value=mock_tree_action_instance)

    # Patch the action class
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SessionTreeAction",
        mock_tree_action_class,
    )

    response, status_code = controller.get_chat_context(session_id=None)

    assert status_code == 500
    assert isinstance(response, ApiResponse)
    assert response.success is False
    assert response.message == "Tree error"
```

### Testing Generic Exception Handling

```python
def test_get_chat_context_generic_exception(
    self, controller, sample_session_tree_response, monkeypatch
):
    """Test that generic exceptions are handled with 500 status."""
    # Mock SessionTreeAction
    mock_tree_action = Mock()
    mock_tree_action.execute.return_value = sample_session_tree_response
    mock_tree_action_class = Mock(return_value=mock_tree_action)

    # Mock SettingsGetAction to raise generic exception
    def mock_settings_action_raises(*args, **kwargs):
        raise ValueError("Unexpected error")

    mock_settings_action_instance = Mock()
    mock_settings_action_instance.execute = mock_settings_action_raises
    mock_settings_action_class = Mock(return_value=mock_settings_action_instance)

    # Patch the action classes
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SessionTreeAction",
        mock_tree_action_class,
    )
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SettingsGetAction",
        mock_settings_action_class,
    )

    response, status_code = controller.get_chat_context(session_id=None)

    assert status_code == 500
    assert isinstance(response, ApiResponse)
    assert response.success is False
    assert response.message == "Unexpected error"
```

### Testing Request Data Propagation

```python
def test_get_chat_context_with_request_data(
    self,
    controller,
    sample_session_tree_response,
    sample_settings_response,
    monkeypatch,
):
    """Test that request_data is passed to actions."""
    # Mock SessionTreeAction
    mock_tree_action = Mock()
    mock_tree_action.execute.return_value = sample_session_tree_response
    mock_tree_action_class = Mock(return_value=mock_tree_action)

    # Mock SettingsGetAction
    mock_settings_action = Mock()
    mock_settings_action.execute.return_value = sample_settings_response
    mock_settings_action_class = Mock(return_value=mock_settings_action)

    # Patch the action classes
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SessionTreeAction",
        mock_tree_action_class,
    )
    monkeypatch.setattr(
        "pipe.web.controllers.session_chat_controller.SettingsGetAction",
        mock_settings_action_class,
    )

    mock_request = Mock()
    response, status_code = controller.get_chat_context(
        session_id=None, request_data=mock_request
    )

    # Verify request_data was passed to actions
    mock_tree_action_class.assert_called_once_with(
        params={}, request_data=mock_request
    )
    mock_settings_action_class.assert_called_once_with(
        params={}, request_data=mock_request
    )
    assert status_code == 200
```

## Fixture Patterns

### Creating Sample Response Models

```python
@pytest.fixture
def sample_session_tree_response(self):
    """Create a sample session tree response."""
    overview = SessionOverview(
        session_id="session-1",
        purpose="Test session",
        created_at="2024-01-01T00:00:00",
        last_updated_at="2024-01-01T01:00:00",
    )
    tree_node = SessionTreeNode(session_id="session-1", overview=overview)
    return SessionTreeResponse(
        sessions={"session-1": overview}, session_tree=[tree_node]
    )

@pytest.fixture
def sample_settings_response(self):
    """Create a sample settings response."""
    settings_info = SettingsInfo(
        model="claude-3-sonnet",
        search_model="claude-3-haiku",
        context_limit=100000,
        cache_update_threshold=1000,
        api_mode="api",
        language="en",
        yolo=False,
        max_tool_calls=50,
        expert_mode=False,
        sessions_path="/path/to/sessions",
        reference_ttl=3600,
        tool_response_expiration=300,
        timezone="UTC",
        hyperparameters=Hyperparameters(temperature=1.0, top_k=0, top_p=0.999),
    )
    return SettingsResponse(settings=settings_info)

@pytest.fixture
def sample_session(self):
    """Create a sample session."""
    return Session(
        session_id="session-1",
        created_at="2024-01-01T00:00:00",
        purpose="Test Session",
        roles=["test-role"],
    )
```

### Creating Mock Services

```python
@pytest.fixture
def mock_session_service(self):
    """Create a mock session service."""
    return Mock()

@pytest.fixture
def mock_settings(self):
    """Create mock settings."""
    return Mock()
```

## Key Testing Principles

1. **Mock Dependencies**: Controllers orchestrate actions and services, so mock all dependencies
2. **Use Monkeypatch**: Use pytest's monkeypatch to inject mock action classes
3. **Test Action Orchestration**: Verify that controller calls the right actions in the right order
4. **Test Error Handling**: Ensure controller handles HttpException and generic exceptions properly
5. **Test Response Structure**: Verify that responses are formatted correctly (ApiResponse wrapper)
6. **Test Business Logic**: Focus on the controller's orchestration logic, not action internals
7. **Test Request Data Flow**: Verify request_data is passed through to actions when needed
8. **Test Edge Cases**: Test scenarios like missing sessions, non-200 status codes, etc.
9. **Verify Mock Calls**: Use `assert_called_once()` or similar to verify actions were called correctly
10. **Isolated Tests**: Each test should be independent and not rely on other tests

## Common Patterns

### Mocking Action Classes with Monkeypatch

```python
# Create a mock instance that will be returned by the action class
mock_action = Mock()
mock_action.execute.return_value = expected_response

# Create a mock class that returns the mock instance
mock_action_class = Mock(return_value=mock_action)

# Use monkeypatch to replace the real class with the mock
monkeypatch.setattr(
    "pipe.web.controllers.module_name.ActionClassName",
    mock_action_class,
)
```

### Mocking Functions (like dispatch_action)

```python
# Create a mock function
mock_dispatch = Mock(return_value=({"data": sample_data}, 200))

# Use monkeypatch to replace the function
monkeypatch.setattr(
    "pipe.web.controllers.module_name.dispatch_action",
    mock_dispatch,
)
```

### Testing HttpException with Custom Status Codes

```python
# Create a custom HttpException with specific status code
def mock_action_raises(*args, **kwargs):
    error = HttpException("Custom error message")
    error.status_code = 403
    raise error

mock_action_instance = Mock()
mock_action_instance.execute = mock_action_raises
```

### Testing with HttpException Subclasses

```python
# Use specific exception subclasses (preferred)
from pipe.web.exceptions import NotFoundError, InternalServerError

def mock_action_raises(*args, **kwargs):
    raise NotFoundError("Resource not found")
```

## Running Tests

```bash
# Run all web controller tests
poetry run pytest tests/unit/web/controllers/ -v

# Run specific test file
poetry run pytest tests/unit/web/controllers/test_session_chat_controller.py -v

# Run specific test class
poetry run pytest tests/unit/web/controllers/test_session_chat_controller.py::TestSessionChatController -v

# Run specific test method
poetry run pytest tests/unit/web/controllers/test_session_chat_controller.py::TestSessionChatController::test_initialization -v
```

## Differences from Other Layers

### vs. Requests Layer
- **Requests**: Pure data validation, no mocks needed
- **Controllers**: Orchestration logic, requires mocking actions and services

### vs. Actions Layer
- **Actions**: Business logic with service dependencies, mock services
- **Controllers**: Higher-level orchestration, mock actions themselves

### vs. Services Layer
- **Services**: Core business logic, may mock repositories
- **Controllers**: Web-specific orchestration, mock both actions and services

## Best Practices

1. **Keep Controllers Thin**: Controllers should orchestrate, not implement business logic
2. **Test Error Paths**: Always test what happens when actions fail
3. **Verify Call Arguments**: Use `assert_called_once_with()` to verify correct parameters
4. **Use Fixtures**: Create reusable fixtures for common test data
5. **Clear Test Names**: Use descriptive test names that explain the scenario
6. **Arrange-Act-Assert**: Structure tests clearly with setup, execution, and verification
7. **Test Response Format**: Verify both status codes and response structure
8. **Mock at Module Level**: Use `monkeypatch.setattr()` with full module path
9. **Isolate Tests**: Each test should set up its own mocks independently
10. **Document Complex Scenarios**: Add comments explaining complex mock setups
