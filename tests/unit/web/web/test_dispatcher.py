"""Unit tests for ActionDispatcher in src/pipe/web/dispatcher.py."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Request, Response
from pipe.web.dispatcher import (
    ActionDispatcher,
    dispatch_action,
    get_dispatcher,
    init_dispatcher,
)
from pipe.web.exceptions import (
    BadRequestError,
    HttpException,
    NotFoundError,
    UnprocessableEntityError,
)
from pydantic import BaseModel, ValidationError


class TestActionDispatcherDispatch:
    """Tests for ActionDispatcher.dispatch method."""

    @pytest.fixture
    def mock_binder(self):
        return MagicMock()

    @pytest.fixture
    def mock_factory(self):
        return MagicMock()

    @pytest.fixture
    def dispatcher(self, mock_binder, mock_factory):
        return ActionDispatcher(binder=mock_binder, factory=mock_factory)

    @pytest.fixture
    def mock_request(self):
        return MagicMock(spec=Request)

    def test_dispatch_missing_request_data(self, dispatcher):
        """Test dispatch when request_data is None."""
        result, status_code = dispatcher.dispatch(MagicMock, {}, request_data=None)
        assert result == {"message": "Request object is missing"}
        assert status_code == 500

    def test_dispatch_validation_error(self, dispatcher, mock_binder, mock_request):
        """Test dispatch when binder raises ValidationError."""

        class DummyModel(BaseModel):
            field: str

        validation_error = None
        try:
            DummyModel(field=None)  # type: ignore[arg-type]
        except ValidationError as e:
            validation_error = e

        mock_binder.bind.side_effect = validation_error

        result, status_code = dispatcher.dispatch(
            MagicMock, {}, request_data=mock_request
        )

        assert status_code == 422
        assert result["success"] is False
        assert "field" in result["message"]

    def test_dispatch_http_exception_during_bind(
        self, dispatcher, mock_binder, mock_request
    ):
        """Test dispatch when binder raises HttpException."""
        mock_binder.bind.side_effect = HttpException("Custom error")

        result, status_code = dispatcher.dispatch(
            MagicMock, {}, request_data=mock_request
        )

        assert status_code == 500
        assert result["success"] is False
        assert result["message"] == "Custom error"

    def test_dispatch_generic_exception_during_bind(
        self, dispatcher, mock_binder, mock_request
    ):
        """Test dispatch when binder raises a generic Exception."""
        mock_binder.bind.side_effect = Exception("Generic error")

        result, status_code = dispatcher.dispatch(
            MagicMock, {}, request_data=mock_request
        )

        assert status_code == 500
        assert result == {"success": False, "message": "Generic error"}

    def test_dispatch_success_with_response_object(
        self, dispatcher, mock_binder, mock_factory, mock_request
    ):
        """Test dispatch when action returns a Response object."""
        mock_binder.bind.return_value = {"data": "valid"}
        mock_action = MagicMock()
        mock_response = MagicMock(spec=Response)
        mock_action.execute.return_value = mock_response
        mock_factory.create.return_value = mock_action

        result = dispatcher.dispatch(MagicMock, {}, request_data=mock_request)

        assert result == mock_response

    def test_dispatch_success_with_tuple(
        self, dispatcher, mock_binder, mock_factory, mock_request
    ):
        """Test dispatch when action returns a tuple (data, status)."""
        mock_binder.bind.return_value = {"data": "valid"}
        mock_action = MagicMock()

        # Mock response data that has model_dump
        mock_data = MagicMock()
        mock_data.model_dump.return_value = {"key": "value"}

        mock_action.execute.return_value = (mock_data, 201)
        mock_factory.create.return_value = mock_action

        result, status_code = dispatcher.dispatch(
            MagicMock, {}, request_data=mock_request
        )

        assert status_code == 201
        assert result == {"key": "value"}
        mock_data.model_dump.assert_called_once_with(mode="json", by_alias=True)

    def test_dispatch_success_with_generic_result(
        self, dispatcher, mock_binder, mock_factory, mock_request
    ):
        """Test dispatch when action returns a generic result."""
        mock_binder.bind.return_value = {"data": "valid"}
        mock_action = MagicMock()
        mock_action.execute.return_value = {"foo": "bar"}
        mock_factory.create.return_value = mock_action

        result, status_code = dispatcher.dispatch(
            MagicMock, {}, request_data=mock_request
        )

        assert status_code == 200
        assert result["success"] is True
        assert result["data"] == {"foo": "bar"}

    @pytest.mark.parametrize(
        "exception_instance, expected_status",
        [
            (BadRequestError("Bad Request"), 400),
            (NotFoundError("Not Found"), 404),
            (UnprocessableEntityError("Unprocessable"), 422),
            (HttpException("HTTP Error"), 500),
            (ValueError("Value Error"), 422),
            (IndexError("Index Error"), 400),
            (FileNotFoundError("File Not Found"), 404),
            (TypeError("Type Error"), 400),
            (Exception("Generic Error"), 500),
        ],
    )
    def test_dispatch_action_execution_errors(
        self,
        dispatcher,
        mock_binder,
        mock_factory,
        mock_request,
        exception_instance,
        expected_status,
    ):
        """Test dispatch when action execution raises various errors."""
        mock_binder.bind.return_value = {"data": "valid"}
        mock_action = MagicMock()
        mock_action.execute.side_effect = exception_instance
        mock_factory.create.return_value = mock_action

        result, status_code = dispatcher.dispatch(
            MagicMock, {}, request_data=mock_request
        )

        assert status_code == expected_status
        assert result["success"] is False
        assert str(exception_instance) in result["message"]

    def test_dispatch_manual_injection_fallback(
        self, dispatcher, mock_binder, mock_factory, mock_request
    ):
        """Test manual injection of request_data and params if not already set."""
        mock_binder.bind.return_value = {"data": "valid"}

        class MockAction:
            def __init__(self):
                self.request_data = None
                self.params = None

            def execute(self):
                return "ok"

        mock_action = MockAction()
        mock_factory.create.return_value = mock_action

        params = {"id": "123"}
        dispatcher.dispatch(MockAction, params, request_data=mock_request)

        assert mock_action.request_data == mock_request
        assert mock_action.params == params

    def test_dispatch_action_execution_import_error(
        self, dispatcher, mock_binder, mock_factory, mock_request
    ):
        """Test dispatch when action execution raises error and exceptions cannot be imported."""
        mock_binder.bind.return_value = {"data": "valid"}
        mock_action = MagicMock()
        mock_action.execute.side_effect = Exception("Generic Error")
        mock_factory.create.return_value = mock_action

        # Mock sys.modules to raise ImportError for pipe.web.exceptions
        with patch.dict("sys.modules", {"pipe.web.exceptions": None}):
            result, status_code = dispatcher.dispatch(
                MagicMock, {}, request_data=mock_request
            )

            assert status_code == 500
            assert result["success"] is False
            assert result["message"] == "Generic Error"


class TestDispatcherGlobals:
    """Tests for global dispatcher functions."""

    def test_get_dispatcher_not_initialized(self):
        """Test get_dispatcher raises RuntimeError when not initialized."""
        with patch("pipe.web.dispatcher._dispatcher", None):
            with pytest.raises(RuntimeError, match="Dispatcher not initialized"):
                get_dispatcher()

    def test_init_dispatcher(self):
        """Test init_dispatcher initializes global instances."""
        mock_services = [MagicMock() for _ in range(8)]

        # Reset globals before test
        with (
            patch("pipe.web.dispatcher._dispatcher", None),
            patch("pipe.web.dispatcher._container", None),
        ):
            dispatcher = init_dispatcher(*mock_services)

            assert dispatcher is not None
            assert get_dispatcher() == dispatcher

    def test_dispatch_action_success(self):
        """Test dispatch_action calls global dispatcher's dispatch."""
        mock_dispatcher = MagicMock()
        with patch("pipe.web.dispatcher.get_dispatcher", return_value=mock_dispatcher):
            dispatch_action(MagicMock, {"p": 1}, request_data=MagicMock())
            mock_dispatcher.dispatch.assert_called_once()

    def test_dispatch_action_string_path_error(self):
        """Test dispatch_action raises ValueError for string action path."""
        with pytest.raises(ValueError, match="no longer supported"):
            dispatch_action("some.path", {})
