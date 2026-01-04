"""Unit tests for BaseAction."""

from typing import ClassVar
from unittest.mock import MagicMock, patch

import pytest
from flask import Request
from pipe.core.models.base import CamelCaseModel
from pipe.web.actions.base_action import BaseAction
from pipe.web.request_context import RequestContext
from pipe.web.requests.base_request import BaseRequest
from pydantic import BaseModel


class MockBody(BaseModel):
    """Mock body model for testing."""

    field: str


class MockRequest(BaseRequest):
    """Mock request model for testing."""

    path_params: ClassVar[list[str]] = ["id"]
    id: int
    field: str | None = None


class MockResponseModel(CamelCaseModel):
    """Mock response model for testing."""

    status: str


class ConcreteAction(BaseAction[MockBody, MockRequest]):
    """Concrete implementation of BaseAction for testing."""

    body_model = MockBody
    request_model = MockRequest

    def execute(self) -> MockResponseModel:
        """Execute the action."""
        return MockResponseModel(status="ok")


class ActionCallingSuper(BaseAction[MockBody, MockRequest]):
    """Action that calls super().execute() to cover the base implementation."""

    def execute(self) -> MockResponseModel:
        """Execute and call super."""
        super().execute()
        return MockResponseModel(status="super")


class TestBaseAction:
    """Tests for BaseAction class."""

    def test_init_legacy(self) -> None:
        """Test initialization using legacy pattern (params and request_data)."""
        params = {"id": 123}
        mock_request_data = MagicMock(spec=Request)

        # Use patch_path from py_test_strategist
        with patch("pipe.web.actions.base_action.RequestContext") as mock_context_class:
            action = ConcreteAction(params=params, request_data=mock_request_data)

            mock_context_class.assert_called_once_with(
                path_params=params,
                request_data=mock_request_data,
                body_model=ConcreteAction.body_model,
            )
            assert action.request == mock_context_class.return_value
            assert action.params == params
            assert action.request_data == mock_request_data
            assert action.validated_request is None

    def test_init_with_context(self) -> None:
        """Test initialization with provided RequestContext."""
        mock_context = MagicMock(spec=RequestContext)

        action = ConcreteAction(request_context=mock_context)

        assert action.request == mock_context
        assert action.params == {}
        assert action.request_data is None
        assert action.validated_request is None

    def test_init_with_validated_request(self) -> None:
        """Test initialization with validated_request."""
        mock_validated_request = MagicMock(spec=MockRequest)
        mock_context = MagicMock(spec=RequestContext)

        action = ConcreteAction(
            request_context=mock_context, validated_request=mock_validated_request
        )

        assert action.request == mock_context
        assert action.validated_request == mock_validated_request

    def test_execute_implementation(self) -> None:
        """Test that a concrete implementation of execute works."""
        action = ConcreteAction()
        result = action.execute()

        assert isinstance(result, MockResponseModel)
        assert result.status == "ok"

    def test_base_execute_call(self) -> None:
        """Test calling super().execute() to cover the base pass statement."""
        action = ActionCallingSuper()
        result = action.execute()
        assert result.status == "super"

    def test_abstract_class_instantiation(self) -> None:
        """Test that BaseAction cannot be instantiated directly."""
        with pytest.raises(
            TypeError, match="Can't instantiate abstract class BaseAction"
        ):
            BaseAction()  # type: ignore[abstract]
