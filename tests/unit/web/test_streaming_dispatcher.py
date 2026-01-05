"""Unit tests for streaming_dispatcher.py."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Response
from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import (
    HttpException,
    InternalServerError,
    UnprocessableEntityError,
)
from pipe.web.request_context import RequestContext
from pipe.web.streaming_dispatcher import dispatch_streaming_action
from pydantic import ValidationError


class TestDispatchStreamingAction:
    """Tests for dispatch_streaming_action function."""

    @pytest.fixture
    def mock_request_context(self) -> MagicMock:
        """Create a mock RequestContext."""
        mock = MagicMock(spec=RequestContext)
        mock._request_data = MagicMock()
        return mock

    @pytest.fixture
    def mock_action_class(self) -> MagicMock:
        """Create a mock action class."""
        return MagicMock(spec=type(BaseAction))

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_success(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test successful dispatch of a streaming action."""
        # Setup
        params = {"id": "123"}
        mock_dispatcher = mock_get_dispatcher.return_value
        mock_binder = MockBinder.return_value

        mock_validated_data = MagicMock()
        mock_binder.bind.return_value = mock_validated_data

        mock_action_instance = MagicMock()
        mock_dispatcher.factory.create.return_value = mock_action_instance

        mock_response = MagicMock(spec=Response)
        mock_action_instance.execute.return_value = mock_response

        # Execute
        result = dispatch_streaming_action(
            mock_action_class, params, mock_request_context
        )

        # Verify
        assert result == mock_response
        mock_binder.bind.assert_called_once_with(
            mock_action_class, mock_request_context._request_data, params
        )
        mock_dispatcher.factory.create.assert_called_once()
        mock_action_instance.execute.assert_called_once()

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_validation_error(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test dispatch when binding raises ValidationError."""
        # Setup
        mock_binder = MockBinder.return_value

        # Create a real ValidationError for mocking
        mock_binder.bind.side_effect = ValidationError.from_exception_data(
            "title", [{"type": "missing", "loc": ("field",), "input": None}]
        )

        # Execute & Verify
        with pytest.raises(UnprocessableEntityError) as excinfo:
            dispatch_streaming_action(mock_action_class, {}, mock_request_context)

        assert "field: Field required" in str(excinfo.value)

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_http_exception_during_bind(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test dispatch when binding raises HttpException."""
        # Setup
        mock_binder = MockBinder.return_value
        mock_binder.bind.side_effect = HttpException("Custom error")

        # Execute & Verify
        with pytest.raises(HttpException) as excinfo:
            dispatch_streaming_action(mock_action_class, {}, mock_request_context)

        assert excinfo.value.message == "Custom error"

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_unexpected_exception_during_bind(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test dispatch when binding raises an unexpected Exception."""
        # Setup
        mock_binder = MockBinder.return_value
        mock_binder.bind.side_effect = Exception("Unexpected")

        # Execute & Verify
        with pytest.raises(InternalServerError) as excinfo:
            dispatch_streaming_action(mock_action_class, {}, mock_request_context)

        assert "Unexpected" in str(excinfo.value)

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_factory_create_error(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test dispatch when action creation fails."""
        # Setup
        mock_dispatcher = mock_get_dispatcher.return_value
        mock_dispatcher.factory.create.side_effect = Exception("Factory error")

        # Execute & Verify
        with pytest.raises(InternalServerError) as excinfo:
            dispatch_streaming_action(mock_action_class, {}, mock_request_context)

        assert "Failed to create action: Factory error" in str(excinfo.value)

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_invalid_return_type(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test dispatch when action returns a non-Response object."""
        # Setup
        mock_dispatcher = mock_get_dispatcher.return_value
        mock_action_instance = MagicMock()
        mock_dispatcher.factory.create.return_value = mock_action_instance
        mock_action_instance.execute.return_value = "not a response"

        # Execute & Verify
        with pytest.raises(InternalServerError) as excinfo:
            dispatch_streaming_action(mock_action_class, {}, mock_request_context)

        assert "must return Flask Response" in str(excinfo.value)

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_http_exception_during_execute(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test dispatch when action execution raises HttpException."""
        # Setup
        mock_dispatcher = mock_get_dispatcher.return_value
        mock_action_instance = MagicMock()
        mock_dispatcher.factory.create.return_value = mock_action_instance
        mock_action_instance.execute.side_effect = HttpException("Execute error")

        # Execute & Verify
        with pytest.raises(HttpException) as excinfo:
            dispatch_streaming_action(mock_action_class, {}, mock_request_context)

        assert excinfo.value.message == "Execute error"

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_unexpected_exception_during_execute(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test dispatch when action execution raises an unexpected Exception."""
        # Setup
        mock_dispatcher = mock_get_dispatcher.return_value
        mock_action_instance = MagicMock()
        mock_dispatcher.factory.create.return_value = mock_action_instance
        mock_action_instance.execute.side_effect = Exception("Unexpected execute error")

        # Execute & Verify
        with pytest.raises(InternalServerError) as excinfo:
            dispatch_streaming_action(mock_action_class, {}, mock_request_context)

        assert "Unexpected execute error" in str(excinfo.value)

    @patch("pipe.web.streaming_dispatcher.get_dispatcher")
    @patch("pipe.web.streaming_dispatcher.RequestBinder")
    def test_dispatch_manual_injection_fallback(
        self,
        MockBinder: MagicMock,
        mock_get_dispatcher: MagicMock,
        mock_request_context: MagicMock,
        mock_action_class: MagicMock,
    ) -> None:
        """Test manual injection fallback for request_context."""
        # Setup
        mock_dispatcher = mock_get_dispatcher.return_value

        # Create an action instance that has request_context attribute but it's None
        class MockAction:
            def __init__(self) -> None:
                self.request_context = None

            def execute(self) -> MagicMock:
                return MagicMock(spec=Response)

        mock_action_instance = MockAction()
        mock_dispatcher.factory.create.return_value = mock_action_instance

        # Execute
        dispatch_streaming_action(mock_action_class, {}, mock_request_context)

        # Verify
        assert mock_action_instance.request_context == mock_request_context
