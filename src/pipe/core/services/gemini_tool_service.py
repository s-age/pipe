"""Service for tool discovery and schema generation for Gemini API."""

import importlib.util
import inspect
import os
from typing import NotRequired, TypedDict, Union, get_args, get_type_hints


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
        type_mapping = {
            str: "string",
            int: "number",
            float: "number",
            bool: "boolean",
        }

        try:
            filenames = os.listdir(tools_dir)
        except Exception:
            return []

        for filename in filenames:
            if not (filename.endswith(".py") and not filename.startswith("__")):
                continue

            tool_name = os.path.splitext(filename)[0]
            tool_file_path = os.path.join(tools_dir, filename)

            try:
                spec = importlib.util.spec_from_file_location(
                    f"pipe.core.tools.{tool_name}", tool_file_path
                )
                if not spec or not spec.loader:
                    continue
                tool_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(tool_module)

                if not hasattr(tool_module, tool_name):
                    continue

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
                    if name in [
                        "session_service",
                        "session_id",
                        "settings",
                        "project_root",
                    ]:
                        continue

                    param_type = type_hints.get(name, str)
                    is_optional = False
                    origin_type = getattr(param_type, "__origin__", None)

                    # Handle Optional[T] (which is Union[T, None])
                    if origin_type is Union:
                        union_args = get_args(param_type)
                        if len(union_args) == 2 and type(None) in union_args:
                            is_optional = True
                            param_type = next(
                                t for t in union_args if t is not type(None)
                            )
                            origin_type = getattr(param_type, "__origin__", None)

                    # Handle list types
                    if origin_type in (list, list):
                        list_item_type = (
                            get_args(param_type)[0] if get_args(param_type) else str
                        )
                        item_origin_type = getattr(list_item_type, "__origin__", None)
                        if item_origin_type in (dict, dict):
                            properties[name] = {
                                "type": "array",
                                "items": {"type": "object"},
                            }
                        else:
                            mapped_item_type = type_mapping.get(
                                list_item_type, "string"
                            )
                            properties[name] = {
                                "type": "array",
                                "items": {"type": mapped_item_type},
                            }
                    # Handle dict types
                    elif origin_type in (dict, dict):
                        properties[name] = {"type": "object", "properties": {}}
                    # Handle basic types
                    else:
                        mapped_type = type_mapping.get(param_type, "string")
                        properties[name] = {"type": mapped_type}

                    # Mark as required if no default value and not optional
                    if param.default is inspect.Parameter.empty and not is_optional:
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
                tool_defs.append(tool_def)

            except Exception:
                # Skip tools that fail to load
                pass

        return tool_defs
