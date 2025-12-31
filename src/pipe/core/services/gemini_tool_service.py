"""Service for tool discovery and schema generation for Gemini API."""

import importlib.util
import inspect
import logging
import os
from typing import Any, NotRequired, TypedDict, Union, get_args, get_type_hints

from google.genai import types

logger = logging.getLogger(__name__)


class ToolParameterSchema(TypedDict):
    """Schema for a single tool parameter."""

    type: str
    items: NotRequired[dict[str, str]]  # For array types
    properties: NotRequired[dict[str, dict]]  # For object types


class ToolParameters(TypedDict):
    """Tool parameters schema definition."""

    type: str  # Always "object"
    properties: dict[str, ToolParameterSchema]
    required: list[str]


class GeminiToolDefinition(TypedDict):
    """Complete tool definition for Gemini API."""

    name: str
    description: str
    parameters: ToolParameters


class GeminiToolService:
    """
    Manages tool discovery and schema generation for Gemini API.

    Responsibilities:
    - Scan tools directory for available tool modules
    - Dynamically load tool functions
    - Generate JSON schemas compatible with google-genai
    - Extract type hints and parameter information
    """

    # System parameters that should be filtered out from tool definitions
    SYSTEM_PARAMETERS = {"session_service", "session_id", "settings", "project_root"}

    # Type mapping for basic Python types to JSON Schema types
    TYPE_MAPPING = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
    }

    def load_tools(self, project_root: str) -> list[GeminiToolDefinition]:
        """
        Scan the tools directory and generate JSON schemas for google-genai.

        Args:
            project_root: Root directory of the project

        Returns:
            List of typed tool definitions compatible with Gemini API.
            Each definition contains: name, description, parameters schema.

        Note:
            - Automatically filters out system parameters (session_service, etc.)
            - Handles Optional types, lists, dicts, and basic types
            - Uses function docstrings for tool descriptions
            - Returns TypedDict for static type safety
        """
        tools_dir = os.path.join(project_root, "src", "pipe", "core", "tools")
        tool_defs: list[GeminiToolDefinition] = []

        try:
            filenames = os.listdir(tools_dir)
        except Exception:
            return []

        for filename in filenames:
            if not (filename.endswith(".py") and not filename.startswith("__")):
                continue

            tool_name = os.path.splitext(filename)[0]
            tool_file_path = os.path.join(tools_dir, filename)

            tool_def = self._generate_tool_definition(tool_name, tool_file_path)
            if tool_def is not None:
                tool_defs.append(tool_def)

        return tool_defs

    def convert_to_genai_tools(
        self, tool_definitions: list[GeminiToolDefinition]
    ) -> list[types.Tool]:
        """
        Convert tool definitions to Gemini API types.Tool objects.

        Args:
            tool_definitions: List of tool definitions from load_tools()

        Returns:
            List of types.Tool objects suitable for Gemini API calls
        """
        converted_tools = []
        for tool_def in tool_definitions:
            # Get parameters dict and convert to Schema
            parameters_dict = tool_def.get("parameters", {})
            parameters_schema = types.Schema(**parameters_dict)  # type: ignore[arg-type]

            converted_tools.append(
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=tool_def["name"],
                            description=tool_def.get("description", ""),
                            parameters=parameters_schema,
                        )
                    ]
                )
            )
        return converted_tools

    def _generate_tool_definition(
        self, tool_name: str, tool_file_path: str
    ) -> GeminiToolDefinition | None:
        """
        Generate a tool definition from a tool file.

        Args:
            tool_name: Tool name (filename without extension)
            tool_file_path: Absolute path to the tool file

        Returns:
            Tool definition if successful, None if the file cannot be loaded
            or does not match expected structure.

        Raises:
            ValueError: If module loading or function extraction fails unexpectedly.
        """
        try:
            # Load module
            spec = importlib.util.spec_from_file_location(
                f"pipe.core.tools.{tool_name}", tool_file_path
            )
            if not spec or not spec.loader:
                return None
            tool_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tool_module)

            # Check if the tool function exists
            if not hasattr(tool_module, tool_name):
                return None

            tool_function = getattr(tool_module, tool_name)
            sig = inspect.signature(tool_function)
            type_hints = get_type_hints(tool_function)

            description = (
                inspect.getdoc(tool_function) or f"Executes the {tool_name} tool."
            )

            properties: dict[str, ToolParameterSchema] = {}
            required: list[str] = []

            for name, param in sig.parameters.items():
                # Skip system parameters injected by the framework
                if name in self.SYSTEM_PARAMETERS:
                    continue

                param_type = type_hints.get(name, str)
                schema, is_required = self._map_parameter_to_schema(
                    name, param_type, param.default
                )
                properties[name] = schema
                if is_required:
                    required.append(name)

            tool_def: GeminiToolDefinition = {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            return tool_def

        except Exception as e:
            logger.debug(f"Failed to load tool {tool_name} from {tool_file_path}: {e}")
            return None

    def _map_parameter_to_schema(
        self, name: str, param_type: Any, default_value: Any
    ) -> tuple[ToolParameterSchema, bool]:
        """
        Map a parameter type to JSON Schema format and determine if it's required.

        Args:
            name: Parameter name
            param_type: Type hint from get_type_hints
            default_value: Default value from inspect.Parameter.default

        Returns:
            Tuple of (ToolParameterSchema, is_required)
            - ToolParameterSchema: JSON Schema representation of the parameter
            - is_required: True if the parameter has no default and is not optional
        """
        is_optional = False
        origin_type = getattr(param_type, "__origin__", None)

        # Handle Optional[T] (which is Union[T, None])
        if origin_type is Union:
            union_args = get_args(param_type)
            if len(union_args) == 2 and type(None) in union_args:
                is_optional = True
                param_type = next(t for t in union_args if t is not type(None))
                origin_type = getattr(param_type, "__origin__", None)

        # Handle list types
        if origin_type is list or param_type is list:
            list_item_type = get_args(param_type)[0] if get_args(param_type) else str
            item_origin_type = getattr(list_item_type, "__origin__", None)
            if item_origin_type is dict or list_item_type is dict:
                schema: ToolParameterSchema = {
                    "type": "array",
                    "items": {"type": "object"},
                }
            else:
                mapped_item_type = self.TYPE_MAPPING.get(list_item_type, "string")
                schema = {
                    "type": "array",
                    "items": {"type": mapped_item_type},
                }
        # Handle dict types
        elif origin_type is dict or param_type is dict:
            schema = {"type": "object", "properties": {}}
        # Handle basic types
        else:
            mapped_type = self.TYPE_MAPPING.get(param_type, "string")
            schema = {"type": mapped_type}

        # Mark as required if no default value and not optional
        is_required = default_value is inspect.Parameter.empty and not is_optional

        return schema, is_required
