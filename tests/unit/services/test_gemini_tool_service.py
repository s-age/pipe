"""Unit tests for GeminiToolService."""

import inspect
import tempfile
import unittest
from pathlib import Path

from pipe.core.services.gemini_tool_service import (
    GeminiToolService,
)


class TestGeminiToolService(unittest.TestCase):
    """Tests for GeminiToolService."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = GeminiToolService()

    def test_map_parameter_to_schema_str(self):
        """Test mapping a string parameter."""
        schema, is_required = self.service._map_parameter_to_schema(
            "query", str, inspect.Parameter.empty
        )
        self.assertEqual(schema["type"], "string")
        self.assertTrue(is_required)

    def test_map_parameter_to_schema_int(self):
        """Test mapping an integer parameter."""
        schema, is_required = self.service._map_parameter_to_schema(
            "count", int, inspect.Parameter.empty
        )
        self.assertEqual(schema["type"], "number")
        self.assertTrue(is_required)

    def test_map_parameter_to_schema_float(self):
        """Test mapping a float parameter."""
        schema, is_required = self.service._map_parameter_to_schema("score", float, 0.5)
        self.assertEqual(schema["type"], "number")
        self.assertFalse(is_required)

    def test_map_parameter_to_schema_bool(self):
        """Test mapping a boolean parameter."""
        schema, is_required = self.service._map_parameter_to_schema(
            "enabled", bool, False
        )
        self.assertEqual(schema["type"], "boolean")
        self.assertFalse(is_required)

    def test_map_parameter_to_schema_optional_str(self):
        """Test mapping an optional string parameter."""
        from typing import Optional

        param_type = Optional[str]  # noqa: UP007
        schema, is_required = self.service._map_parameter_to_schema(
            "optional_query", param_type, inspect.Parameter.empty
        )
        self.assertEqual(schema["type"], "string")
        self.assertFalse(is_required)

    def test_map_parameter_to_schema_list_int(self):
        """Test mapping a list of integers."""

        param_type = list[int]
        schema, is_required = self.service._map_parameter_to_schema(
            "numbers", param_type, inspect.Parameter.empty
        )
        self.assertEqual(schema["type"], "array")
        self.assertEqual(schema["items"]["type"], "number")
        self.assertTrue(is_required)

    def test_map_parameter_to_schema_list_str(self):
        """Test mapping a list of strings."""

        param_type = list[str]
        schema, is_required = self.service._map_parameter_to_schema(
            "tags", param_type, None
        )
        self.assertEqual(schema["type"], "array")
        self.assertEqual(schema["items"]["type"], "string")
        self.assertFalse(is_required)

    def test_map_parameter_to_schema_dict(self):
        """Test mapping a dictionary parameter."""
        schema, is_required = self.service._map_parameter_to_schema(
            "metadata", dict, inspect.Parameter.empty
        )
        self.assertEqual(schema["type"], "object")
        self.assertTrue(is_required)

    def test_map_parameter_to_schema_with_default(self):
        """Test parameter with default value is not required."""
        schema, is_required = self.service._map_parameter_to_schema(
            "message", str, "default_value"
        )
        self.assertEqual(schema["type"], "string")
        self.assertFalse(is_required)

    def test_generate_tool_definition_missing_file(self):
        """Test _generate_tool_definition with non-existent file."""
        result = self.service._generate_tool_definition(
            "nonexistent", "/path/to/nonexistent.py"
        )
        self.assertIsNone(result)

    def test_generate_tool_definition_invalid_module(self):
        """Test _generate_tool_definition with invalid Python module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = Path(tmpdir) / "bad_tool.py"
            tool_file.write_text("this is not valid python }{")

            result = self.service._generate_tool_definition("bad_tool", str(tool_file))
            self.assertIsNone(result)

    def test_generate_tool_definition_missing_function(self):
        """Test _generate_tool_definition when function name doesn't match module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = Path(tmpdir) / "tool_a.py"
            tool_file.write_text("""
def tool_b(query: str) -> str:
    \"\"\"Some tool.\"\"\"
    return query
""")

            result = self.service._generate_tool_definition("tool_a", str(tool_file))
            self.assertIsNone(result)

    def test_generate_tool_definition_valid_tool(self):
        """Test _generate_tool_definition with a valid tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = Path(tmpdir) / "search_tool.py"
            tool_file.write_text("""
def search_tool(query: str, limit: int = 10) -> str:
    \"\"\"Search for something.\"\"\"
    return f"Searching for {query}"
""")

            result = self.service._generate_tool_definition(
                "search_tool", str(tool_file)
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["name"], "search_tool")
            self.assertEqual(result["description"], "Search for something.")
            self.assertIn("query", result["parameters"]["properties"])
            self.assertIn("limit", result["parameters"]["properties"])
            self.assertIn("query", result["parameters"]["required"])
            self.assertNotIn("limit", result["parameters"]["required"])

    def test_generate_tool_definition_filters_system_parameters(self):
        """Test that system parameters are filtered out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = Path(tmpdir) / "my_tool.py"
            tool_file.write_text("""
def my_tool(query: str, session_id: str, settings) -> str:
    \"\"\"My tool.\"\"\"
    return query
""")

            result = self.service._generate_tool_definition("my_tool", str(tool_file))

            self.assertIsNotNone(result)
            self.assertIn("query", result["parameters"]["properties"])
            self.assertNotIn("session_id", result["parameters"]["properties"])
            self.assertNotIn("settings", result["parameters"]["properties"])

    def test_load_tools_empty_directory(self):
        """Test load_tools with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = tmpdir
            # Create the expected tools directory structure
            tools_dir = Path(project_root) / "src" / "pipe" / "core" / "tools"
            tools_dir.mkdir(parents=True, exist_ok=True)

            result = self.service.load_tools(project_root)

            self.assertEqual(result, [])

    def test_load_tools_multiple_tools(self):
        """Test load_tools with multiple tool files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = tmpdir
            tools_dir = Path(project_root) / "src" / "pipe" / "core" / "tools"
            tools_dir.mkdir(parents=True, exist_ok=True)

            # Create first tool
            tool1_file = tools_dir / "search.py"
            tool1_file.write_text("""
def search(query: str) -> str:
    \"\"\"Search tool.\"\"\"
    return query
""")

            # Create second tool
            tool2_file = tools_dir / "calculate.py"
            tool2_file.write_text("""
def calculate(expression: str) -> str:
    \"\"\"Calculate tool.\"\"\"
    return str(eval(expression))
""")

            # Create init file (should be ignored)
            init_file = tools_dir / "__init__.py"
            init_file.write_text("")

            result = self.service.load_tools(project_root)

            self.assertEqual(len(result), 2)
            names = {tool["name"] for tool in result}
            self.assertEqual(names, {"search", "calculate"})

    def test_load_tools_nonexistent_directory(self):
        """Test load_tools when tools directory doesn't exist."""
        result = self.service.load_tools("/nonexistent/path")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
