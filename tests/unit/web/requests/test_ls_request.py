"""Unit tests for LsRequest model."""

import pytest
from pipe.web.requests.fs.ls_request import LsRequest
from pydantic import ValidationError


class TestLsRequest:
    """Tests for the LsRequest model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        path_list = ["src", "pipe", "web"]
        request = LsRequest(final_path_list=path_list)
        assert request.final_path_list == path_list

    def test_initialization_with_camel_case(self):
        """Test that the request can be initialized using camelCase field names."""
        data = {"finalPathList": ["src", "pipe", "web"]}
        request = LsRequest.model_validate(data)
        assert request.final_path_list == ["src", "pipe", "web"]

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        path_list = ["tests", "unit"]
        request = LsRequest(final_path_list=path_list)
        dumped = request.model_dump()
        assert dumped == {"final_path_list": path_list}

    def test_deserialization_from_snake_case(self):
        """Test that the request can be validated from a dictionary with snake_case keys."""
        data = {"final_path_list": ["root", "subdir"]}
        request = LsRequest.model_validate(data)
        assert request.final_path_list == ["root", "subdir"]

    def test_missing_final_path_list_raises_validation_error(self):
        """Test that missing final_path_list raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LsRequest.model_validate({})

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("final_path_list",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)

    def test_wrong_type_for_final_path_list_raises_validation_error(self):
        """Test that wrong type for final_path_list raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LsRequest.model_validate({"final_path_list": "not-a-list"})

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("final_path_list",) for error in errors)
        assert any(error["type"] == "list_type" for error in errors)

    def test_empty_list_is_accepted(self):
        """Test that an empty list is accepted for final_path_list."""
        request = LsRequest(final_path_list=[])
        assert request.final_path_list == []

    def test_forbid_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            LsRequest.model_validate(
                {"final_path_list": ["src"], "extra_field": "not_allowed"}
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)

    def test_create_with_path_params(self):
        """Test creating request with path parameters (inherited from BaseRequest)."""
        # LsRequest doesn't define path_params, so it should just merge body_data
        request = LsRequest.create_with_path_params(
            path_params={"ignored": "value"}, body_data={"final_path_list": ["src"]}
        )
        assert request.final_path_list == ["src"]
