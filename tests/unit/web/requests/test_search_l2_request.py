"""Tests for the SearchL2Request model."""

import pytest
from pipe.web.requests.fs.search_l2_request import SearchL2Request
from pydantic import ValidationError


class TestSearchL2Request:
    """Tests for the SearchL2Request model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        request = SearchL2Request(
            current_path_list=["src", "pipe"], query="search term"
        )
        assert request.current_path_list == ["src", "pipe"]
        assert request.query == "search term"

    def test_initialization_with_camel_case(self):
        """Test that the request can be initialized using camelCase field names (via BaseRequest)."""
        # BaseRequest uses normalize_camel_case_keys validator
        data = {"currentPathList": ["src", "pipe"], "query": "search term"}
        request = SearchL2Request.model_validate(data)
        assert request.current_path_list == ["src", "pipe"]
        assert request.query == "search term"

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchL2Request()  # type: ignore

        errors = exc_info.value.errors()
        assert len(errors) == 2
        locs = [error["loc"] for error in errors]
        assert ("current_path_list",) in locs
        assert ("query",) in locs

    def test_invalid_types(self):
        """Test that invalid types raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchL2Request(
                current_path_list="not a list",  # type: ignore
                query=123,  # type: ignore
            )

        errors = exc_info.value.errors()
        assert len(errors) == 2
        assert any(error["loc"] == ("current_path_list",) for error in errors)
        assert any(error["loc"] == ("query",) for error in errors)

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        request = SearchL2Request(current_path_list=["src"], query="test")
        dumped = request.model_dump()
        assert dumped == {"current_path_list": ["src"], "query": "test"}

    def test_create_with_path_params(self):
        """Test creating request with path parameters (inherited from BaseRequest)."""
        # SearchL2Request doesn't define path_params, but let's verify it works
        request = SearchL2Request.create_with_path_params(
            path_params={}, body_data={"current_path_list": ["src"], "query": "test"}
        )
        assert isinstance(request, SearchL2Request)
        assert request.current_path_list == ["src"]
        assert request.query == "test"

    def test_forbid_extra_fields(self):
        """Test that extra fields are forbidden (inherited from BaseRequest)."""
        with pytest.raises(ValidationError) as exc_info:
            SearchL2Request(
                current_path_list=["src"],
                query="test",
                extra_field="not allowed",  # type: ignore
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
