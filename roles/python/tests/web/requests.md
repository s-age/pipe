# Web Requests Layer Testing Strategy

**Layer:** `src/pipe/web/requests/`

## Responsibilities
- API request data validation
- Request body parsing and normalization
- Path parameter integration
- camelCase to snake_case conversion

## Testing Strategy
- **No Mocks Needed**: Testing pure data validation and transformation
- **Focus**: Field validation, error handling, serialization/deserialization, path parameter merging

## Test Patterns

### Basic Request Validation

```python
# tests/unit/web/requests/test_therapist_requests.py
import pytest
from pipe.core.models.session_optimization import (
    SessionModifications,
    TurnCompression,
    TurnEdit,
)
from pipe.web.requests.therapist_requests import (
    ApplyDoctorRequest,
    CreateTherapistRequest,
)
from pydantic import ValidationError


class TestCreateTherapistRequest:
    """Tests for the CreateTherapistRequest model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        request = CreateTherapistRequest(session_id="test-session-123")
        assert request.session_id == "test-session-123"

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        request = CreateTherapistRequest(session_id="test-session-789")
        dumped = request.model_dump()
        assert "session_id" in dumped
        assert dumped["session_id"] == "test-session-789"

    def test_deserialization_from_snake_case(self):
        """Test that the request can be validated from a dictionary with snake_case keys."""
        data = {"session_id": "test-session-abc"}
        request = CreateTherapistRequest.model_validate(data)
        assert request.session_id == "test-session-abc"

    def test_missing_session_id_raises_validation_error(self):
        """Test that missing session_id raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CreateTherapistRequest()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("session_id",)
        assert errors[0]["type"] == "missing"

    def test_empty_string_session_id(self):
        """Test that empty string is accepted for session_id."""
        request = CreateTherapistRequest(session_id="")
        assert request.session_id == ""

    def test_create_with_path_params(self):
        """Test creating request with path parameters."""
        request = CreateTherapistRequest.create_with_path_params(
            path_params={}, body_data={"session_id": "body-session-123"}
        )
        assert request.session_id == "body-session-123"
```

### Complex Request with Nested Models

```python
class TestApplyDoctorRequest:
    """Tests for the ApplyDoctorRequest model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        modifications = SessionModifications(
            deletions=[1, 2],
            edits=[TurnEdit(turn=3, new_content="Updated content")],
            compressions=[TurnCompression(start=5, end=10, reason="Compress test")],
        )
        request = ApplyDoctorRequest(
            session_id="test-session-123", modifications=modifications
        )
        assert request.session_id == "test-session-123"
        assert request.modifications == modifications

    def test_initialization_with_dict_modifications(self):
        """Test that the request can be initialized with dict modifications."""
        request = ApplyDoctorRequest(
            session_id="test-session-456",
            modifications={
                "deletions": [1, 2],
                "edits": [{"turn": 3, "new_content": "Updated"}],
                "compressions": [{"start": 5, "end": 10, "reason": "Test"}],
            },
        )
        assert request.session_id == "test-session-456"
        assert len(request.modifications.deletions) == 2
        assert len(request.modifications.edits) == 1
        assert len(request.modifications.compressions) == 1

    def test_complex_modifications(self):
        """Test with complex modifications containing multiple items."""
        data = {
            "session_id": "test-session-complex",
            "modifications": {
                "deletions": [1, 3, 5, 7],
                "edits": [
                    {"turn": 2, "new_content": "First edit"},
                    {"turn": 4, "new_content": "Second edit"},
                    {"turn": 6, "new_content": "Third edit"},
                ],
                "compressions": [
                    {"start": 10, "end": 15, "reason": "First compression"},
                    {"start": 20, "end": 25, "reason": "Second compression"},
                ],
            },
        }
        request = ApplyDoctorRequest.model_validate(data)
        assert request.session_id == "test-session-complex"
        assert len(request.modifications.deletions) == 4
        assert len(request.modifications.edits) == 3
        assert len(request.modifications.compressions) == 2
        assert request.modifications.edits[1].new_content == "Second edit"
        assert request.modifications.compressions[0].start == 10

    def test_forbid_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            ApplyDoctorRequest(
                session_id="test-session",
                modifications={"deletions": [], "edits": [], "compressions": []},
                extra_field="not_allowed",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
```

### Request with Custom Validation

```python
# tests/unit/web/requests/test_search_sessions.py
from pipe.web.requests.search_sessions import SearchSessionsRequest


class TestSearchSessionsRequest:
    """Tests for the SearchSessionsRequest model."""

    def test_initialization_with_valid_query(self):
        """Test that the request can be initialized with a valid query."""
        request = SearchSessionsRequest(query="test query")
        assert request.query == "test query"

    def test_empty_string_query_raises_validation_error(self):
        """Test that empty string query raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchSessionsRequest(query="")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query",)
        assert errors[0]["type"] == "value_error"
        assert "query is required and must not be empty" in str(errors[0]["ctx"]["error"])

    def test_whitespace_only_query_raises_validation_error(self):
        """Test that whitespace-only query raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchSessionsRequest(query="   ")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query",)
        assert errors[0]["type"] == "value_error"
        assert "query is required and must not be empty" in str(errors[0]["ctx"]["error"])

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

    def test_none_query_raises_validation_error(self):
        """Test that None query raises a ValidationError."""
        with pytest.raises(ValidationError):
            SearchSessionsRequest(query=None)
```

## Key Testing Principles

1. **Required Field Validation**: Always test that required fields raise ValidationError when missing
2. **Empty Value Validation**: Test empty strings, whitespace-only strings, and None values
3. **Data Type Validation**: Ensure proper type checking and conversion
4. **Nested Model Validation**: Test both direct model initialization and dict-based initialization
5. **Extra Fields**: Verify that extra fields are rejected (extra="forbid")
6. **Custom Validators**: Test all custom validation rules (e.g., non-empty strings)
7. **Edge Cases**: Test special characters, unicode, very long inputs, etc.
8. **Serialization**: Verify model_dump() produces correct structure
9. **Deserialization**: Verify model_validate() handles various input formats
10. **Path Parameters**: Test create_with_path_params() method when applicable

## Common Test Patterns

### Testing Required Fields
```python
def test_missing_required_field_raises_validation_error(self):
    """Test that missing required field raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        RequestModel()  # Missing required field

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("field_name",) for error in errors)
    assert any(error["type"] == "missing" for error in errors)
```

### Testing Custom Validators
```python
def test_custom_validator_error_message(self):
    """Test that custom validator provides clear error message."""
    with pytest.raises(ValidationError) as exc_info:
        RequestModel(field="invalid_value")

    errors = exc_info.value.errors()
    assert errors[0]["type"] == "value_error"
    assert "expected error message" in str(errors[0]["ctx"]["error"])
```

### Testing Edge Cases
```python
def test_field_with_edge_cases(self):
    """Test field accepts various edge case values."""
    edge_cases = ["", "   ", "special@#$", "unicode™", "very" * 1000]
    for value in edge_cases:
        # Either should pass or raise expected ValidationError
        try:
            request = RequestModel(field=value)
            assert request.field == value
        except ValidationError:
            # Expected for certain edge cases
            pass
```

## Running Tests

```bash
# Run all web request tests
poetry run pytest tests/unit/web/requests/ -v

# Run specific test file
poetry run pytest tests/unit/web/requests/test_therapist_requests.py -v

# Run specific test class
poetry run pytest tests/unit/web/requests/test_therapist_requests.py::TestCreateTherapistRequest -v

# Run specific test method
poetry run pytest tests/unit/web/requests/test_therapist_requests.py::TestCreateTherapistRequest::test_initialization_with_snake_case -v
```
