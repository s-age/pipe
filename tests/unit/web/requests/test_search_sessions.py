"""Tests for search sessions request model."""

import pytest
from pipe.web.requests.search_sessions import SearchSessionsRequest
from pydantic import ValidationError


class TestSearchSessionsRequest:
    """Tests for the SearchSessionsRequest model."""

    def test_initialization_with_valid_query(self):
        """Test that the request can be initialized with a valid query."""
        request = SearchSessionsRequest(query="test query")
        assert request.query == "test query"

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        request = SearchSessionsRequest(query="search term")
        assert request.query == "search term"

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        request = SearchSessionsRequest(query="test query")
        dumped = request.model_dump()
        assert "query" in dumped
        assert dumped["query"] == "test query"

    def test_deserialization_from_snake_case(self):
        """Test that the request can be validated from a dictionary."""
        data = {"query": "search term"}
        request = SearchSessionsRequest.model_validate(data)
        assert request.query == "search term"

    def test_missing_query_raises_validation_error(self):
        """Test that missing query raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchSessionsRequest()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query",)
        assert errors[0]["type"] == "missing"

    def test_empty_string_query_raises_validation_error(self):
        """Test that empty string query raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchSessionsRequest(query="")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query",)
        assert errors[0]["type"] == "value_error"
        assert "query is required and must not be empty" in str(
            errors[0]["ctx"]["error"]
        )

    def test_whitespace_only_query_raises_validation_error(self):
        """Test that whitespace-only query raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchSessionsRequest(query="   ")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query",)
        assert errors[0]["type"] == "value_error"
        assert "query is required and must not be empty" in str(
            errors[0]["ctx"]["error"]
        )

    def test_query_with_leading_trailing_whitespace(self):
        """Test that query with leading/trailing whitespace is preserved."""
        request = SearchSessionsRequest(query="  test query  ")
        assert request.query == "  test query  "

    def test_query_with_special_characters(self):
        """Test that query with special characters is accepted."""
        special_queries = [
            "query with @#$%",
            "query-with-dashes",
            "query_with_underscores",
            "query with 123 numbers",
            "クエリ with unicode",
            "query\nwith\nnewlines",
        ]
        for query in special_queries:
            request = SearchSessionsRequest(query=query)
            assert request.query == query

    def test_long_query(self):
        """Test that long queries are accepted."""
        long_query = "a" * 10000
        request = SearchSessionsRequest(query=long_query)
        assert request.query == long_query

    def test_create_with_path_params(self):
        """Test creating request with path parameters and body data."""
        request = SearchSessionsRequest.create_with_path_params(
            path_params={}, body_data={"query": "test search"}
        )
        assert request.query == "test search"

    def test_create_with_body_data_only(self):
        """Test creating request with body data only."""
        request = SearchSessionsRequest.create_with_path_params(
            path_params={}, body_data={"query": "another search"}
        )
        assert request.query == "another search"

    def test_forbid_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            SearchSessionsRequest(query="test", extra_field="not_allowed")

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)

    def test_none_query_raises_validation_error(self):
        """Test that None query raises a ValidationError."""
        with pytest.raises(ValidationError):
            SearchSessionsRequest(query=None)
