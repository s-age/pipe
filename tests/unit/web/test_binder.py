"""Unit tests for RequestBinder and utility functions in binder.py."""

from unittest.mock import MagicMock

import pytest
from flask import Request
from pipe.web.binder import (
    RequestBinder,
    _camel_to_snake,
    _convert_keys_to_camel,
    _convert_keys_to_snake,
    _snake_to_camel,
)
from pipe.web.requests.base_request import BaseRequest


class TestStringConversion:
    """Tests for camelCase and snake_case conversion utilities."""

    @pytest.mark.parametrize(
        "input_str, expected",
        [
            ("camelCase", "camel_case"),
            ("Simple", "simple"),
            ("already_snake", "already_snake"),
            ("HTTPRequest", "http_request"),
            ("myHTTPResponse", "my_http_response"),
            ("v1Alpha1", "v1_alpha1"),
            ("", ""),
        ],
    )
    def test_camel_to_snake(self, input_str: str, expected: str):
        """Test converting camelCase to snake_case."""
        assert _camel_to_snake(input_str) == expected

    @pytest.mark.parametrize(
        "input_str, expected",
        [
            ("snake_case", "snakeCase"),
            ("simple", "simple"),
            ("alreadyCamel", "alreadyCamel"),
            ("http_request", "httpRequest"),
            ("my_http_response", "myHttpResponse"),
            ("", ""),
        ],
    )
    def test_snake_to_camel(self, input_str: str, expected: str):
        """Test converting snake_case to camelCase."""
        assert _snake_to_camel(input_str) == expected


class TestKeyConversion:
    """Tests for recursive key conversion in dictionaries and lists."""

    def test_convert_keys_to_snake_dict(self):
        """Test converting dictionary keys to snake_case recursively."""
        data = {
            "userName": "testUser",
            "userProfile": {
                "firstName": "John",
                "lastName": "Doe",
                "contactInfo": [
                    {"emailAddress": "john@example.com"},
                    {"phoneNumber": "123456"},
                ],
            },
        }
        expected = {
            "user_name": "testUser",
            "user_profile": {
                "first_name": "John",
                "last_name": "Doe",
                "contact_info": [
                    {"email_address": "john@example.com"},
                    {"phone_number": "123456"},
                ],
            },
        }
        assert _convert_keys_to_snake(data) == expected

    def test_convert_keys_to_camel_dict(self):
        """Test converting dictionary keys to camelCase recursively."""
        data = {
            "user_name": "testUser",
            "user_profile": {
                "first_name": "John",
                "last_name": "Doe",
                "contact_info": [
                    {"email_address": "john@example.com"},
                    {"phone_number": "123456"},
                ],
            },
        }
        expected = {
            "userName": "testUser",
            "userProfile": {
                "firstName": "John",
                "lastName": "Doe",
                "contactInfo": [
                    {"emailAddress": "john@example.com"},
                    {"phoneNumber": "123456"},
                ],
            },
        }
        assert _convert_keys_to_camel(data) == expected

    def test_convert_keys_non_dict_list(self):
        """Test that non-dict/list data is returned as is."""
        assert _convert_keys_to_snake("string") == "string"
        assert _convert_keys_to_snake(123) == 123
        assert _convert_keys_to_camel(None) is None


class TestRequestBinder:
    """Tests for RequestBinder.bind method."""

    @pytest.fixture
    def binder(self):
        """Create a RequestBinder instance."""
        return RequestBinder()

    @pytest.fixture
    def mock_request(self):
        """Create a mock Flask Request object."""
        request = MagicMock(spec=Request)
        request.is_json = False
        return request

    def test_bind_no_json_no_model(self, binder, mock_request):
        """Test binding when there is no JSON and no request model."""

        class DummyAction:
            pass

        result = binder.bind(DummyAction, mock_request, {})
        assert result is None

    def test_bind_with_json_no_model(self, binder, mock_request):
        """Test binding when JSON is present but no request model is defined."""
        mock_request.is_json = True
        mock_request.get_json.return_value = {"userName": "test"}

        class DummyAction:
            pass

        result = binder.bind(DummyAction, mock_request, {})
        assert result == {"user_name": "test"}
        mock_request.get_json.assert_called_once_with(silent=True)

    def test_bind_with_json_and_model(self, binder, mock_request):
        """Test binding when both JSON and request model are present."""
        mock_request.is_json = True
        mock_request.get_json.return_value = {"userName": "test"}
        route_params = {"id": "123"}

        class MockRequestModel(BaseRequest):
            user_name: str
            id: str
            path_params = ["id"]

        class DummyAction:
            request_model = MockRequestModel

        result = binder.bind(DummyAction, mock_request, route_params)

        assert isinstance(result, MockRequestModel)
        assert result.user_name == "test"
        assert result.id == "123"

    def test_bind_no_json_with_model(self, binder, mock_request):
        """Test binding when JSON is absent but request model is present."""
        mock_request.is_json = False
        route_params = {"id": "123"}

        class MockRequestModel(BaseRequest):
            id: str
            path_params = ["id"]

        class DummyAction:
            request_model = MockRequestModel

        result = binder.bind(DummyAction, mock_request, route_params)

        assert isinstance(result, MockRequestModel)
        assert result.id == "123"

    def test_bind_silent_json_failure(self, binder, mock_request):
        """Test binding when get_json returns None (silent failure)."""
        mock_request.is_json = True
        mock_request.get_json.return_value = None

        class DummyAction:
            pass

        result = binder.bind(DummyAction, mock_request, {})
        assert result is None

    def test_bind_model_not_subclass_of_base_request(self, binder, mock_request):
        """Test binding when request_model is not a subclass of BaseRequest."""
        mock_request.is_json = True
        mock_request.get_json.return_value = {"userName": "test"}

        class NotBaseRequest:
            def __init__(self, **kwargs):
                self.data = kwargs

        class DummyAction:
            request_model = NotBaseRequest

        result = binder.bind(DummyAction, mock_request, {})
        # Should return converted_json because it's not a BaseRequest subclass
        assert result == {"user_name": "test"}
