"""Unit tests for GeminiToolService."""

import inspect
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.services.gemini_tool_service import GeminiToolService


@pytest.fixture
def service():
    """Create a GeminiToolService instance."""
    return GeminiToolService()


class TestGeminiToolServiceMapParameterToSchema:
    """Tests for _map_parameter_to_schema method."""

    def test_map_parameter_to_schema_str(self, service):
        """Test mapping a string parameter."""
        schema, is_required = service._map_parameter_to_schema(
            "query", str, inspect.Parameter.empty
        )
        assert schema["type"] == "string"
        assert is_required is True

    def test_map_parameter_to_schema_int(self, service):
        """Test mapping an integer parameter."""
        schema, is_required = service._map_parameter_to_schema(
            "count", int, inspect.Parameter.empty
        )
        assert schema["type"] == "number"
        assert is_required is True

    def test_map_parameter_to_schema_float(self, service):
        """Test mapping a float parameter."""
        schema, is_required = service._map_parameter_to_schema("score", float, 0.5)
        assert schema["type"] == "number"
        assert is_required is False

    def test_map_parameter_to_schema_bool(self, service):
        """Test mapping a boolean parameter."""
        schema, is_required = service._map_parameter_to_schema("enabled", bool, False)
        assert schema["type"] == "boolean"
        assert is_required is False

    def test_map_parameter_to_schema_optional_str(self, service):
        """Test mapping an optional string parameter."""
        from typing import Union

        param_type = Union[str, None]  # noqa: UP007
        schema, is_required = service._map_parameter_to_schema(
            "optional_query", param_type, None
        )
        assert schema["type"] == "string"
        assert is_required is False

    def test_map_parameter_to_schema_typing_optional(self, service):
        """Test mapping an optional parameter using typing.Optional."""
        from typing import Union

        param_type = Union[int, None]  # noqa: UP007
        schema, is_required = service._map_parameter_to_schema(
            "count", param_type, None
        )
        assert schema["type"] == "number"
        assert is_required is False

    def test_map_parameter_to_schema_list_int(self, service):
        """Test mapping a list of integers."""
        param_type = list[int]
        schema, is_required = service._map_parameter_to_schema(
            "numbers", param_type, inspect.Parameter.empty
        )
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "number"
        assert is_required is True

    def test_map_parameter_to_schema_list_str(self, service):
        """Test mapping a list of strings."""
        param_type = list[str]
        schema, is_required = service._map_parameter_to_schema("tags", param_type, None)
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "string"
        assert is_required is False

    def test_map_parameter_to_schema_list_dict(self, service):
        """Test mapping a list of dictionaries."""
        param_type = list[dict]
        schema, is_required = service._map_parameter_to_schema(
            "items", param_type, inspect.Parameter.empty
        )
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "object"
        assert is_required is True

    def test_map_parameter_to_schema_dict(self, service):
        """Test mapping a dictionary parameter."""
        schema, is_required = service._map_parameter_to_schema(
            "metadata", dict, inspect.Parameter.empty
        )
        assert schema["type"] == "object"
        assert is_required is True

    def test_map_parameter_to_schema_with_default(self, service):
        """Test parameter with default value is not required."""
        schema, is_required = service._map_parameter_to_schema(
            "message", str, "default_value"
        )
        assert schema["type"] == "string"
        assert is_required is False


class TestGeminiToolServiceGenerateToolDefinition:
    """Tests for _generate_tool_definition method."""

    def test_generate_tool_definition_missing_file(self, service):
        """Test _generate_tool_definition with non-existent file."""
        result = service._generate_tool_definition(
            "nonexistent", "/path/to/nonexistent.py"
        )
        assert result is None

    def test_generate_tool_definition_invalid_module(self, service):
        """Test _generate_tool_definition with invalid Python module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = Path(tmpdir) / "bad_tool.py"
            tool_file.write_text("this is not valid python }{")

            result = service._generate_tool_definition("bad_tool", str(tool_file))
            assert result is None

    def test_generate_tool_definition_missing_function(self, service):
        """Test _generate_tool_definition when function name doesn't match module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = Path(tmpdir) / "tool_a.py"
            tool_file.write_text(
                """
def tool_b(query: str) -> str:
    \"\"\"Some tool.\"\"\"
    return query
"""
            )

            result = service._generate_tool_definition("tool_a", str(tool_file))
            assert result is None

    def test_generate_tool_definition_valid_tool(self, service):
        """Test _generate_tool_definition with a valid tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = Path(tmpdir) / "search_tool.py"
            tool_file.write_text(
                """
def search_tool(query: str, limit: int = 10) -> str:
    \"\"\"Search for something.\"\"\"
    return f"Searching for {query}"
"""
            )

            result = service._generate_tool_definition("search_tool", str(tool_file))

            assert result is not None
            assert result["name"] == "search_tool"
            assert result["description"] == "Search for something."
            assert "query" in result["parameters"]["properties"]
            assert "limit" in result["parameters"]["properties"]
            assert "query" in result["parameters"]["required"]
            assert "limit" not in result["parameters"]["required"]

    def test_generate_tool_definition_filters_system_parameters(self, service):
        """Test that system parameters are filtered out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = Path(tmpdir) / "my_tool.py"
            tool_file.write_text(
                """
def my_tool(query: str, session_id: str, settings) -> str:
    \"\"\"My tool.\"\"\"
    return query
"""
            )

            result = service._generate_tool_definition("my_tool", str(tool_file))

            assert result is not None
            assert "query" in result["parameters"]["properties"]
            assert "session_id" not in result["parameters"]["properties"]
            assert "settings" not in result["parameters"]["properties"]

    @patch(
        "pipe.core.services.gemini_tool_service.importlib.util.spec_from_file_location"
    )
    def test_generate_tool_definition_no_loader(self, mock_spec, service):
        """Test _generate_tool_definition when spec or loader is missing."""
        mock_spec.return_value = None
        result = service._generate_tool_definition("tool", "/path/to/tool.py")
        assert result is None

        mock_spec.return_value = MagicMock(loader=None)
        result = service._generate_tool_definition("tool", "/path/to/tool.py")
        assert result is None

    @patch(
        "pipe.core.services.gemini_tool_service.importlib.util.spec_from_file_location"
    )
    def test_generate_tool_definition_exception(self, mock_spec, service):
        """Test _generate_tool_definition when an exception occurs."""
        mock_spec.side_effect = Exception("Unexpected error")
        result = service._generate_tool_definition("tool", "/path/to/tool.py")
        assert result is None


class TestGeminiToolServiceLoadTools:
    """Tests for load_tools method."""

    def test_load_tools_empty_directory(self, service):
        """Test load_tools with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = tmpdir
            # Create the expected tools directory structure
            tools_dir = Path(project_root) / "src" / "pipe" / "core" / "tools"
            tools_dir.mkdir(parents=True, exist_ok=True)

            result = service.load_tools(project_root)

            assert result == []

    def test_load_tools_multiple_tools(self, service):
        """Test load_tools with multiple tool files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = tmpdir
            tools_dir = Path(project_root) / "src" / "pipe" / "core" / "tools"
            tools_dir.mkdir(parents=True, exist_ok=True)

            # Create first tool
            tool1_file = tools_dir / "search.py"
            tool1_file.write_text(
                """
def search(query: str) -> str:
    \"\"\"Search tool.\"\"\"
    return query
"""
            )

            # Create second tool
            tool2_file = tools_dir / "calculate.py"
            tool2_file.write_text(
                """
def calculate(expression: str) -> str:
    \"\"\"Calculate tool.\"\"\"
    return str(eval(expression))
"""
            )

            # Create init file (should be ignored)
            init_file = tools_dir / "__init__.py"
            init_file.write_text("")

            result = service.load_tools(project_root)

            assert len(result) == 2
            names = {tool["name"] for tool in result}
            assert names == {"search", "calculate"}

    def test_load_tools_nonexistent_directory(self, service):
        """Test load_tools when tools directory doesn't exist."""
        result = service.load_tools("/nonexistent/path")
        assert result == []

    @patch("pipe.core.services.gemini_tool_service.os.listdir")
    def test_load_tools_exception(self, mock_listdir, service):
        """Test load_tools when listdir raises an exception."""
        mock_listdir.side_effect = Exception("Permission denied")
        result = service.load_tools("/some/path")
        assert result == []


class TestGeminiToolServiceConvertToGenaiTools:
    """Tests for convert_to_genai_tools method."""

    def test_convert_to_genai_tools(self, service):
        """Test converting tool definitions to types.Tool objects."""
        tool_definitions = [
            {
                "name": "search",
                "description": "Search tool",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            }
        ]

        with patch(
            "pipe.core.services.gemini_tool_service.types.Schema"
        ) as mock_schema:
            with patch(
                "pipe.core.services.gemini_tool_service.types.Tool"
            ) as mock_tool:
                with patch(
                    "pipe.core.services.gemini_tool_service.types.FunctionDeclaration"
                ) as mock_func_decl:
                    mock_schema_instance = MagicMock()
                    mock_schema.return_value = mock_schema_instance

                    mock_func_decl_instance = MagicMock()
                    mock_func_decl.return_value = mock_func_decl_instance

                    mock_tool_instance = MagicMock()
                    mock_tool.return_value = mock_tool_instance

                    result = service.convert_to_genai_tools(tool_definitions)

                    assert len(result) == 1
                    assert result[0] == mock_tool_instance

                    mock_schema.assert_called_once_with(
                        type="object",
                        properties={"query": {"type": "string"}},
                        required=["query"],
                    )
                    mock_func_decl.assert_called_once_with(
                        name="search",
                        description="Search tool",
                        parameters=mock_schema_instance,
                    )
                    mock_tool.assert_called_once_with(
                        function_declarations=[mock_func_decl_instance]
                    )

    def test_convert_to_genai_tools_empty(self, service):
        """Test converting empty list of tool definitions."""
        result = service.convert_to_genai_tools([])
        assert result == []
