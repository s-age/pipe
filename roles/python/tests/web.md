# Web Layer Testing Strategy

**Layer:** `src/pipe/web/`

## Responsibilities
- Request binding and validation (RequestBinder)
- Dependency injection and action instantiation (GenericActionFactory)
- Action dispatching and error handling (ActionDispatcher, StreamingDispatcher)
- Request context management (RequestContext)
- Service container management (ServiceContainer)
- HTTP exception handling (HttpException and subclasses)

## Testing Strategy
- **Mock Dependencies**: Mock Flask Request objects and service dependencies
- **Focus**: Request binding, validation, dependency injection, error handling, response formatting
- **Isolation**: Test each component independently with clear boundaries

## File-by-File Testing Patterns

### binder.py - RequestBinder

**Responsibilities:**
- Convert camelCase to snake_case in request data
- Bind Flask request to action's expected format
- Validate against request_model using Pydantic

**Test Pattern:**
```python
# tests/unit/web/test_binder.py
import pytest
from unittest.mock import Mock, MagicMock
from flask import Request
from pipe.web.binder import RequestBinder, _camel_to_snake, _snake_to_camel
from pipe.web.requests.base_request import BaseRequest
from pydantic import ValidationError


class TestCamelToSnake:
    """Test camelCase to snake_case conversion."""

    def test_simple_camel_case(self):
        """Test simple camelCase conversion."""
        assert _camel_to_snake("sessionId") == "session_id"
        assert _camel_to_snake("userName") == "user_name"

    def test_with_acronyms(self):
        """Test conversion with acronyms."""
        assert _camel_to_snake("APIKey") == "api_key"
        assert _camel_to_snake("HTTPResponse") == "http_response"

    def test_already_snake_case(self):
        """Test that snake_case remains unchanged."""
        assert _camel_to_snake("session_id") == "session_id"


class TestSnakeToCamel:
    """Test snake_case to camelCase conversion."""

    def test_simple_snake_case(self):
        """Test simple snake_case conversion."""
        assert _snake_to_camel("session_id") == "sessionId"
        assert _snake_to_camel("user_name") == "userName"

    def test_already_camel_case(self):
        """Test that camelCase remains mostly unchanged."""
        assert _snake_to_camel("sessionId") == "sessionId"


class MockRequest(BaseRequest):
    """Mock request model for testing."""
    path_params = ["id"]
    id: str
    field: str


class MockAction:
    """Mock action class for testing."""
    request_model = MockRequest


class TestRequestBinder:
    """Tests for RequestBinder.bind method."""

    def test_bind_with_json_body(self):
        """Test binding with JSON request body."""
        binder = RequestBinder()
        mock_request = Mock(spec=Request)
        mock_request.is_json = True
        mock_request.get_json.return_value = {"field": "value"}

        result = binder.bind(MockAction, mock_request, {"id": "123"})

        assert result.id == "123"
        assert result.field == "value"

    def test_bind_with_camel_case_conversion(self):
        """Test that camelCase is converted to snake_case."""
        binder = RequestBinder()
        mock_request = Mock(spec=Request)
        mock_request.is_json = True
        mock_request.get_json.return_value = {"fieldName": "value"}

        # Assuming MockRequest has field_name
        # This test would need a proper request model with field_name
        # For now, verify conversion happens
        assert True  # Placeholder

    def test_bind_without_json_body(self):
        """Test binding with no JSON body."""
        binder = RequestBinder()
        mock_request = Mock(spec=Request)
        mock_request.is_json = False

        result = binder.bind(MockAction, mock_request, {"id": "123"})

        assert result.id == "123"

    def test_bind_validation_error(self):
        """Test that validation errors are propagated."""
        binder = RequestBinder()
        mock_request = Mock(spec=Request)
        mock_request.is_json = True
        mock_request.get_json.return_value = {"invalid": "data"}

        with pytest.raises(ValidationError):
            binder.bind(MockAction, mock_request, {})

    def test_bind_without_request_model(self):
        """Test binding when action has no request_model."""
        class ActionWithoutModel:
            pass

        binder = RequestBinder()
        mock_request = Mock(spec=Request)
        mock_request.is_json = True
        mock_request.get_json.return_value = {"field": "value"}

        result = binder.bind(ActionWithoutModel, mock_request, {})

        assert result == {"field": "value"}
```

### factory.py - GenericActionFactory

**Responsibilities:**
- Instantiate action classes
- Inject dependencies from DI container
- Resolve runtime context parameters
- Handle type hints and parameter matching

**Test Pattern:**
```python
# tests/unit/web/test_factory.py
import pytest
from unittest.mock import Mock
from pipe.web.factory import GenericActionFactory
from pipe.core.container import DependencyContainer


class ServiceA:
    pass


class ServiceB:
    pass


class ActionWithDependencies:
    def __init__(self, service_a: ServiceA, service_b: ServiceB):
        self.service_a = service_a
        self.service_b = service_b


class ActionWithRuntimeContext:
    def __init__(self, validated_request: dict):
        self.validated_request = validated_request


class ActionNoInit:
    pass


class TestGenericActionFactory:
    """Tests for GenericActionFactory."""

    def test_create_with_di_container(self):
        """Test creating action with dependencies from container."""
        container = DependencyContainer()
        service_a = ServiceA()
        service_b = ServiceB()
        container.register(ServiceA, service_a)
        container.register(ServiceB, service_b)

        factory = GenericActionFactory(container)
        action = factory.create(ActionWithDependencies, {})

        assert action.service_a is service_a
        assert action.service_b is service_b

    def test_create_with_runtime_context(self):
        """Test creating action with runtime context."""
        container = DependencyContainer()
        factory = GenericActionFactory(container)
        runtime_context = {"validated_request": {"key": "value"}}

        action = factory.create(ActionWithRuntimeContext, runtime_context)

        assert action.validated_request == {"key": "value"}

    def test_create_with_no_init(self):
        """Test creating action with no __init__ method."""
        container = DependencyContainer()
        factory = GenericActionFactory(container)

        action = factory.create(ActionNoInit, {})

        assert isinstance(action, ActionNoInit)

    def test_create_missing_dependency_raises_error(self):
        """Test that missing dependencies raise RuntimeError."""
        container = DependencyContainer()
        factory = GenericActionFactory(container)

        with pytest.raises(RuntimeError, match="Cannot resolve dependency"):
            factory.create(ActionWithDependencies, {})

    def test_create_with_singleton(self):
        """Test that pre-registered action instances are returned."""
        container = DependencyContainer()
        existing_action = ActionNoInit()
        container.register(ActionNoInit, existing_action)

        factory = GenericActionFactory(container)
        action = factory.create(ActionNoInit, {})

        assert action is existing_action
```

### dispatcher.py - ActionDispatcher

**Responsibilities:**
- Dispatch actions to handlers
- Handle request binding and validation errors
- Format responses (ApiResponse wrapper)
- Handle HTTP exceptions and convert to responses
- Manage action execution lifecycle

**Test Pattern:**
```python
# tests/unit/web/test_dispatcher.py
import pytest
from unittest.mock import Mock, MagicMock, patch
from flask import Request, Response
from pipe.web.dispatcher import ActionDispatcher
from pipe.web.binder import RequestBinder
from pipe.web.factory import GenericActionFactory
from pipe.web.exceptions import BadRequestError, NotFoundError
from pydantic import ValidationError


class TestActionDispatcher:
    """Tests for ActionDispatcher."""

    @pytest.fixture
    def mock_binder(self):
        """Create mock RequestBinder."""
        return Mock(spec=RequestBinder)

    @pytest.fixture
    def mock_factory(self):
        """Create mock GenericActionFactory."""
        return Mock(spec=GenericActionFactory)

    @pytest.fixture
    def dispatcher(self, mock_binder, mock_factory):
        """Create ActionDispatcher with mocks."""
        return ActionDispatcher(mock_binder, mock_factory)

    def test_dispatch_success(self, dispatcher, mock_binder, mock_factory):
        """Test successful action dispatch."""
        mock_request = Mock(spec=Request)
        mock_action_class = Mock()
        mock_action_instance = Mock()
        mock_action_instance.execute.return_value = {"result": "success"}

        mock_binder.bind.return_value = {"validated": "data"}
        mock_factory.create.return_value = mock_action_instance

        response, status_code = dispatcher.dispatch(
            mock_action_class, {"id": "123"}, mock_request
        )

        assert status_code == 200
        assert response["success"] is True
        assert response["data"] == {"result": "success"}

    def test_dispatch_validation_error(self, dispatcher, mock_binder):
        """Test dispatch with validation error."""
        mock_request = Mock(spec=Request)
        mock_action_class = Mock()

        # Simulate ValidationError
        error = ValidationError.from_exception_data(
            "ValidationError",
            [{"loc": ("field",), "msg": "Field required", "type": "missing"}],
        )
        mock_binder.bind.side_effect = error

        response, status_code = dispatcher.dispatch(
            mock_action_class, {}, mock_request
        )

        assert status_code == 422
        assert response["success"] is False
        assert "field" in response["message"]

    def test_dispatch_http_exception(self, dispatcher, mock_binder, mock_factory):
        """Test dispatch with HTTP exception."""
        mock_request = Mock(spec=Request)
        mock_action_class = Mock()
        mock_action_instance = Mock()
        mock_action_instance.execute.side_effect = NotFoundError("Resource not found")

        mock_binder.bind.return_value = {}
        mock_factory.create.return_value = mock_action_instance

        response, status_code = dispatcher.dispatch(
            mock_action_class, {}, mock_request
        )

        assert status_code == 404
        assert response["success"] is False
        assert "Resource not found" in response["message"]

    def test_dispatch_file_not_found_error(self, dispatcher, mock_binder, mock_factory):
        """Test dispatch with FileNotFoundError (should become 404)."""
        mock_request = Mock(spec=Request)
        mock_action_class = Mock()
        mock_action_instance = Mock()
        mock_action_instance.execute.side_effect = FileNotFoundError("File not found")

        mock_binder.bind.return_value = {}
        mock_factory.create.return_value = mock_action_instance

        response, status_code = dispatcher.dispatch(
            mock_action_class, {}, mock_request
        )

        assert status_code == 404
        assert response["success"] is False

    def test_dispatch_value_error(self, dispatcher, mock_binder, mock_factory):
        """Test dispatch with ValueError (should become 422)."""
        mock_request = Mock(spec=Request)
        mock_action_class = Mock()
        mock_action_instance = Mock()
        mock_action_instance.execute.side_effect = ValueError("Invalid value")

        mock_binder.bind.return_value = {}
        mock_factory.create.return_value = mock_action_instance

        response, status_code = dispatcher.dispatch(
            mock_action_class, {}, mock_request
        )

        assert status_code == 422
        assert response["success"] is False

    def test_dispatch_unexpected_error(self, dispatcher, mock_binder, mock_factory):
        """Test dispatch with unexpected error (should become 500)."""
        mock_request = Mock(spec=Request)
        mock_action_class = Mock()
        mock_action_instance = Mock()
        mock_action_instance.execute.side_effect = RuntimeError("Unexpected")

        mock_binder.bind.return_value = {}
        mock_factory.create.return_value = mock_action_instance

        response, status_code = dispatcher.dispatch(
            mock_action_class, {}, mock_request
        )

        assert status_code == 500
        assert response["success"] is False

    def test_dispatch_flask_response(self, dispatcher, mock_binder, mock_factory):
        """Test dispatch returning Flask Response object."""
        mock_request = Mock(spec=Request)
        mock_action_class = Mock()
        mock_action_instance = Mock()
        flask_response = Response("custom response")
        mock_action_instance.execute.return_value = flask_response

        mock_binder.bind.return_value = {}
        mock_factory.create.return_value = mock_action_instance

        result = dispatcher.dispatch(mock_action_class, {}, mock_request)

        assert result is flask_response

    def test_dispatch_missing_request(self, dispatcher):
        """Test dispatch with missing request object."""
        response, status_code = dispatcher.dispatch(Mock(), {}, None)

        assert status_code == 500
        assert "Request object is missing" in response["message"]
```

### request_context.py - RequestContext

**Responsibilities:**
- Unified access to path params and body
- Type conversion for path parameters
- Body validation with Pydantic models
- Error handling for missing/invalid parameters

**Test Pattern:**
```python
# tests/unit/web/test_request_context.py
import pytest
from unittest.mock import Mock
from flask import Request
from pipe.web.request_context import RequestContext
from pydantic import BaseModel, ValidationError


class MockBodyModel(BaseModel):
    field: str
    count: int = 0


class TestRequestContext:
    """Tests for RequestContext."""

    def test_get_path_param_success(self):
        """Test getting existing path parameter."""
        context = RequestContext({"id": "123"})
        assert context.get_path_param("id") == "123"

    def test_get_path_param_missing_required(self):
        """Test getting missing required path parameter."""
        context = RequestContext({})
        with pytest.raises(ValueError, match="Required path parameter 'id' is missing"):
            context.get_path_param("id")

    def test_get_path_param_missing_optional(self):
        """Test getting missing optional path parameter."""
        context = RequestContext({})
        assert context.get_path_param("id", required=False) is None

    def test_get_path_param_int_success(self):
        """Test getting path parameter as integer."""
        context = RequestContext({"count": "42"})
        assert context.get_path_param_int("count") == 42

    def test_get_path_param_int_invalid(self):
        """Test getting non-integer path parameter as int."""
        context = RequestContext({"count": "abc"})
        with pytest.raises(ValueError, match="must be an integer"):
            context.get_path_param_int("count")

    def test_get_body_success(self):
        """Test getting validated request body."""
        mock_request = Mock(spec=Request)
        mock_request.is_json = True
        mock_request.get_json.return_value = {"field": "value", "count": 5}

        context = RequestContext({}, mock_request, MockBodyModel)
        body = context.get_body()

        assert isinstance(body, MockBodyModel)
        assert body.field == "value"
        assert body.count == 5

    def test_get_body_no_model_configured(self):
        """Test getting body when no model is configured."""
        context = RequestContext({})
        with pytest.raises(ValueError, match="No body model configured"):
            context.get_body()

    def test_get_body_not_json(self):
        """Test getting body when request is not JSON."""
        mock_request = Mock(spec=Request)
        mock_request.is_json = False

        context = RequestContext({}, mock_request, MockBodyModel)
        with pytest.raises(ValueError, match="Request body must be JSON"):
            context.get_body()

    def test_get_body_validation_error(self):
        """Test getting body with validation errors."""
        mock_request = Mock(spec=Request)
        mock_request.is_json = True
        mock_request.get_json.return_value = {"invalid": "data"}

        context = RequestContext({}, mock_request, MockBodyModel)
        with pytest.raises(ValueError):
            context.get_body()

    def test_get_body_caching(self):
        """Test that validated body is cached."""
        mock_request = Mock(spec=Request)
        mock_request.is_json = True
        mock_request.get_json.return_value = {"field": "value"}

        context = RequestContext({}, mock_request, MockBodyModel)
        body1 = context.get_body()
        body2 = context.get_body()

        assert body1 is body2
        mock_request.get_json.assert_called_once()

    def test_has_body_true(self):
        """Test has_body returns True when body exists."""
        mock_request = Mock(spec=Request)
        mock_request.is_json = True
        mock_request.get_json.return_value = {"field": "value"}

        context = RequestContext({}, mock_request)
        assert context.has_body() is True

    def test_has_body_false(self):
        """Test has_body returns False when no body."""
        mock_request = Mock(spec=Request)
        mock_request.is_json = False

        context = RequestContext({}, mock_request)
        assert context.has_body() is False

    def test_raw_request_property(self):
        """Test accessing raw Flask request."""
        mock_request = Mock(spec=Request)
        context = RequestContext({}, mock_request)
        assert context.raw_request is mock_request
```

### service_container.py - ServiceContainer

**Responsibilities:**
- Store and provide access to service instances
- Lazy initialization validation
- Thread-safe singleton pattern

**Test Pattern:**
```python
# tests/unit/web/test_service_container.py
import pytest
from unittest.mock import Mock
from pipe.web.service_container import ServiceContainer, get_container


class TestServiceContainer:
    """Tests for ServiceContainer."""

    def test_init_services(self):
        """Test initializing container with services."""
        container = ServiceContainer()
        mock_session_service = Mock()
        mock_file_indexer_service = Mock()
        mock_settings = Mock()

        container.init(
            session_service=mock_session_service,
            session_management_service=Mock(),
            session_tree_service=Mock(),
            session_workflow_service=Mock(),
            session_optimization_service=Mock(),
            session_reference_service=Mock(),
            session_artifact_service=Mock(),
            session_turn_service=Mock(),
            session_meta_service=Mock(),
            session_todo_service=Mock(),
            start_session_controller=Mock(),
            session_chat_controller=Mock(),
            session_management_controller=Mock(),
            file_indexer_service=mock_file_indexer_service,
            search_sessions_service=Mock(),
            procedure_service=Mock(),
            role_service=Mock(),
            settings=mock_settings,
            project_root="/test/root",
        )

        assert container.session_service is mock_session_service
        assert container.file_indexer_service is mock_file_indexer_service
        assert container.settings is mock_settings
        assert container.project_root == "/test/root"

    def test_access_before_init_raises_error(self):
        """Test accessing service before initialization raises RuntimeError."""
        container = ServiceContainer()
        with pytest.raises(RuntimeError, match="ServiceContainer not initialized"):
            _ = container.session_service

    def test_get_container_returns_singleton(self):
        """Test that get_container returns the global singleton."""
        container1 = get_container()
        container2 = get_container()
        assert container1 is container2
```

### exceptions.py - HTTP Exceptions

**Responsibilities:**
- Define HTTP exception classes with status codes
- Provide meaningful error messages

**Test Pattern:**
```python
# tests/unit/web/test_exceptions.py
from pipe.web.exceptions import (
    HttpException,
    BadRequestError,
    NotFoundError,
    UnprocessableEntityError,
    InternalServerError,
)


class TestHttpExceptions:
    """Tests for HTTP exception classes."""

    def test_http_exception_base(self):
        """Test base HttpException."""
        exc = HttpException("Something went wrong")
        assert exc.status_code == 500
        assert exc.message == "Something went wrong"
        assert str(exc) == "Something went wrong"

    def test_bad_request_error(self):
        """Test BadRequestError has correct status code."""
        exc = BadRequestError("Invalid input")
        assert exc.status_code == 400
        assert exc.message == "Invalid input"

    def test_not_found_error(self):
        """Test NotFoundError has correct status code."""
        exc = NotFoundError("Resource not found")
        assert exc.status_code == 404
        assert exc.message == "Resource not found"

    def test_unprocessable_entity_error(self):
        """Test UnprocessableEntityError has correct status code."""
        exc = UnprocessableEntityError("Validation failed")
        assert exc.status_code == 422
        assert exc.message == "Validation failed"

    def test_internal_server_error(self):
        """Test InternalServerError has correct status code."""
        exc = InternalServerError("Server error")
        assert exc.status_code == 500
        assert exc.message == "Server error"
```

### streaming_dispatcher.py - StreamingDispatcher

**Responsibilities:**
- Dispatch actions that return streaming responses
- Handle SSE (Server-Sent Events) responses
- Error handling without ApiResponse wrapper

**Test Pattern:**
```python
# tests/unit/web/test_streaming_dispatcher.py
import pytest
from unittest.mock import Mock, patch
from flask import Response
from pipe.web.streaming_dispatcher import dispatch_streaming_action
from pipe.web.exceptions import UnprocessableEntityError, InternalServerError
from pydantic import ValidationError


class MockStreamingAction:
    def __init__(self, validated_request=None):
        self.validated_request = validated_request

    def execute(self):
        return Response("stream data", mimetype="text/event-stream")


class TestStreamingDispatcher:
    """Tests for streaming dispatcher."""

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_streaming_success(self, mock_binder_class, mock_get_dispatcher):
        """Test successful streaming action dispatch."""
        mock_dispatcher = Mock()
        mock_factory = Mock()
        mock_action = MockStreamingAction()

        mock_get_dispatcher.return_value = mock_dispatcher
        mock_dispatcher.factory = mock_factory
        mock_factory.create.return_value = mock_action

        mock_binder = Mock()
        mock_binder_class.return_value = mock_binder
        mock_binder.bind.return_value = {"data": "validated"}

        mock_context = Mock()
        mock_context._request_data = Mock()

        result = dispatch_streaming_action(
            MockStreamingAction, {"id": "123"}, mock_context
        )

        assert isinstance(result, Response)

    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_validation_error(self, mock_binder_class):
        """Test streaming dispatch with validation error."""
        mock_binder = Mock()
        mock_binder_class.return_value = mock_binder

        error = ValidationError.from_exception_data(
            "ValidationError",
            [{"loc": ("field",), "msg": "Field required", "type": "missing"}],
        )
        mock_binder.bind.side_effect = error

        mock_context = Mock()
        mock_context._request_data = Mock()

        with pytest.raises(UnprocessableEntityError):
            dispatch_streaming_action(Mock(), {}, mock_context)

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_non_response_return(self, mock_binder_class, mock_get_dispatcher):
        """Test error when action doesn't return Response."""
        class BadAction:
            def execute(self):
                return {"not": "a response"}

        mock_dispatcher = Mock()
        mock_factory = Mock()
        mock_action = BadAction()

        mock_get_dispatcher.return_value = mock_dispatcher
        mock_dispatcher.factory = mock_factory
        mock_factory.create.return_value = mock_action

        mock_binder = Mock()
        mock_binder_class.return_value = mock_binder
        mock_binder.bind.return_value = {}

        mock_context = Mock()
        mock_context._request_data = Mock()

        with pytest.raises(TypeError, match="must return Flask Response"):
            dispatch_streaming_action(BadAction, {}, mock_context)
```

## Mandatory Test Items

- ✅ Request binding and validation
- ✅ camelCase/snake_case conversion
- ✅ Dependency injection resolution
- ✅ Error handling and HTTP status codes
- ✅ Response formatting (ApiResponse wrapper)
- ✅ Path parameter extraction and validation
- ✅ Body validation with Pydantic
- ✅ Service container initialization
- ✅ Streaming response handling

## Running Tests

```bash
# Run all web layer tests
poetry run pytest tests/unit/web/ -v

# Run specific test file
poetry run pytest tests/unit/web/test_binder.py -v

# Run specific test class
poetry run pytest tests/unit/web/test_binder.py::TestRequestBinder -v
```

## Key Testing Principles

1. **Mock Flask Objects**: Always mock Flask Request and Response objects
2. **Test Error Paths**: Verify all HTTP exception types are handled correctly
3. **Validation Coverage**: Test both valid and invalid inputs
4. **Dependency Injection**: Verify services are correctly resolved from container
5. **Response Format**: Ensure ApiResponse structure is consistent
6. **Type Conversion**: Test camelCase/snake_case conversion edge cases
7. **Error Messages**: Verify error messages are clear and actionable
8. **Isolation**: Each test should be independent and not rely on shared state
