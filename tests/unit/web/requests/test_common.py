"""Unit tests for common request utilities."""

from pipe.web.requests.common import camel_to_snake, normalize_camel_case_keys


class TestCamelToSnake:
    """Tests for camel_to_snake function."""

    def test_basic_camel_to_snake(self):
        """Test basic camelCase to snake_case conversion."""
        assert camel_to_snake("camelCase") == "camel_case"
        assert camel_to_snake("testParameterName") == "test_parameter_name"

    def test_pascal_to_snake(self):
        """Test PascalCase to snake_case conversion."""
        assert camel_to_snake("PascalCase") == "pascal_case"

    def test_acronyms(self):
        """Test handling of acronyms."""
        # Trace: "myHTTPRequest"
        # 1. re.sub("(.)([A-Z][a-z]+)", r"\1_\2", "myHTTPRequest") -> "myHTTP_Request"
        # 2. re.sub("([a-z0-9])([A-Z])", r"\1_\2", "myHTTP_Request") -> "my_HTTP_Request"
        # 3. .lower() -> "my_http_request"
        assert camel_to_snake("myHTTPRequest") == "my_http_request"

    def test_already_snake_case(self):
        """Test that snake_case remains unchanged."""
        assert camel_to_snake("already_snake_case") == "already_snake_case"

    def test_single_word(self):
        """Test single word conversion."""
        assert camel_to_snake("word") == "word"
        assert camel_to_snake("Word") == "word"

    def test_with_numbers(self):
        """Test conversion with numbers."""
        assert camel_to_snake("item123") == "item123"
        assert camel_to_snake("item123Key") == "item123_key"


class TestNormalizeCamelCaseKeys:
    """Tests for normalize_camel_case_keys function."""

    def test_simple_dict(self):
        """Test normalization of a simple dictionary."""
        data = {"sessionId": "123", "userName": "test"}
        expected = {"session_id": "123", "user_name": "test"}
        assert normalize_camel_case_keys(data) == expected

    def test_nested_dict(self):
        """Test normalization of a nested dictionary."""
        data = {
            "sessionInfo": {"sessionId": "123", "creationDate": "2025-01-01"},
            "status": "active",
        }
        expected = {
            "session_info": {"session_id": "123", "creation_date": "2025-01-01"},
            "status": "active",
        }
        assert normalize_camel_case_keys(data) == expected

    def test_key_collision(self):
        """Test behavior when snake_case key already exists."""
        # If snake_key already exists, it keeps the original camelCase key.
        data = {"sessionId": "new", "session_id": "old"}
        expected = {"sessionId": "new", "session_id": "old"}
        assert normalize_camel_case_keys(data) == expected

    def test_non_dict_input(self):
        """Test that non-dictionary input is returned as is."""
        data = ["itemOne", "itemTwo"]
        assert normalize_camel_case_keys(data) == data
        assert normalize_camel_case_keys("string") == "string"
        assert normalize_camel_case_keys(123) == 123

    def test_empty_dict(self):
        """Test normalization of an empty dictionary."""
        assert normalize_camel_case_keys({}) == {}

    def test_no_camel_case_keys(self):
        """Test dictionary with no camelCase keys."""
        data = {"session_id": "123", "status": "active"}
        assert normalize_camel_case_keys(data) == data

    def test_mixed_keys(self):
        """Test dictionary with mixed camelCase and snake_case keys."""
        data = {"sessionId": "123", "status": "active", "user_name": "test"}
        expected = {"session_id": "123", "status": "active", "user_name": "test"}
        assert normalize_camel_case_keys(data) == expected

    def test_list_in_dict(self):
        """Test that lists inside dictionaries are NOT recursively processed (current behavior)."""
        data = {"itemsList": [{"itemId": 1}]}
        # itemsList -> items_list
        # [{"itemId": 1}] is a list, so it's returned as is.
        expected = {"items_list": [{"itemId": 1}]}
        assert normalize_camel_case_keys(data) == expected
