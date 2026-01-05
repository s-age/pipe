"""Unit tests for RequestContext."""

from unittest.mock import MagicMock

import pytest
from pipe.web.request_context import RequestContext
from pydantic import BaseModel


class MockModel(BaseModel):
    """Mock model for testing body validation."""

    name: str
    age: int


class TestRequestContext:
    """Tests for RequestContext class."""

    def test_init(self) -> None:
        """Test initialization of RequestContext."""
        path_params = {"id": "123"}
        context = RequestContext(path_params=path_params)
        assert context._path_params == path_params
        assert context._request_data is None
        assert context._body_model is None

    def test_get_path_param_success(self) -> None:
        """Test successful retrieval of path parameters."""
        path_params = {"id": "123", "active": True}
        context = RequestContext(path_params=path_params)
        assert context.get_path_param("id") == "123"
        assert context.get_path_param("active") is True
        assert context.get_path_param("missing", required=False) is None

    def test_get_path_param_required_missing(self) -> None:
        """Test that missing required path parameter raises ValueError."""
        context = RequestContext(path_params={})
        with pytest.raises(ValueError, match="Required path parameter 'id' is missing"):
            context.get_path_param("id", required=True)

    def test_get_path_param_int_success(self) -> None:
        """Test successful retrieval of path parameter as integer."""
        path_params = {"id": "123"}
        context = RequestContext(path_params=path_params)
        assert context.get_path_param_int("id") == 123
        assert context.get_path_param_int("missing", required=False) is None

    def test_get_path_param_int_invalid(self) -> None:
        """Test that invalid integer path parameter raises ValueError."""
        path_params = {"id": "abc"}
        context = RequestContext(path_params=path_params)
        with pytest.raises(
            ValueError, match="Path parameter 'id' must be an integer, got: abc"
        ):
            context.get_path_param_int("id")

    def test_get_body_success(self) -> None:
        """Test successful retrieval and validation of request body."""
        mock_request = MagicMock()
        mock_request.is_json = True
        mock_request.get_json.return_value = {"name": "John", "age": 30}

        context = RequestContext(
            path_params={}, request_data=mock_request, body_model=MockModel
        )

        body = context.get_body()
        assert isinstance(body, MockModel)
        assert body.name == "John"
        assert body.age == 30
        # Test caching
        assert context.get_body() is body
        mock_request.get_json.assert_called_once()

    def test_get_body_no_model(self) -> None:
        """Test that get_body raises ValueError when no model is configured."""
        context = RequestContext(path_params={})
        with pytest.raises(
            ValueError, match="No body model configured for this request"
        ):
            context.get_body()

    def test_get_body_not_json(self) -> None:
        """Test that get_body raises ValueError when request is not JSON."""
        mock_request = MagicMock()
        mock_request.is_json = False
        context = RequestContext(
            path_params={}, request_data=mock_request, body_model=MockModel
        )
        with pytest.raises(ValueError, match="Request body must be JSON"):
            context.get_body()

    def test_get_body_no_data(self) -> None:
        """Test that get_body raises ValueError when no request body is provided."""
        mock_request = MagicMock()
        mock_request.is_json = True
        mock_request.get_json.return_value = None
        context = RequestContext(
            path_params={}, request_data=mock_request, body_model=MockModel
        )
        with pytest.raises(ValueError, match="No request body provided"):
            context.get_body()

    def test_get_body_validation_error(self) -> None:
        """Test that get_body raises ValueError on validation failure."""
        mock_request = MagicMock()
        mock_request.is_json = True
        mock_request.get_json.return_value = {"name": "John"}  # Missing 'age'
        context = RequestContext(
            path_params={}, request_data=mock_request, body_model=MockModel
        )
        with pytest.raises(ValueError):
            context.get_body()

    def test_has_body(self) -> None:
        """Test has_body method."""
        # Case 1: Has body
        mock_request_1 = MagicMock()
        mock_request_1.is_json = True
        mock_request_1.get_json.return_value = {"data": "ok"}
        context_1 = RequestContext(path_params={}, request_data=mock_request_1)
        assert context_1.has_body() is True

        # Case 2: No request data
        context_2 = RequestContext(path_params={})
        assert context_2.has_body() is False

        # Case 3: Not JSON
        mock_request_3 = MagicMock()
        mock_request_3.is_json = False
        context_3 = RequestContext(path_params={}, request_data=mock_request_3)
        assert context_3.has_body() is False

        # Case 4: JSON but None
        mock_request_4 = MagicMock()
        mock_request_4.is_json = True
        mock_request_4.get_json.return_value = None
        context_4 = RequestContext(path_params={}, request_data=mock_request_4)
        assert context_4.has_body() is False

    def test_raw_request(self) -> None:
        """Test raw_request property."""
        mock_request = MagicMock()
        context = RequestContext(path_params={}, request_data=mock_request)
        assert context.raw_request == mock_request
