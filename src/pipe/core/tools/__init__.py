import fnmatch
import importlib
import os
import sys
from collections.abc import Callable
from typing import Any

# This dictionary will store the loaded tool functions
loaded_tools: dict[str, Callable[..., Any]] = {}


def load_tools():
    """
    Dynamically loads all Python files in the 'tools' directory as tool functions.
    Each file is expected to define a single function with the same name as the
    file (without .py extension).
    """
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(tools_dir):
        if fnmatch.fnmatch(filename, "*.py"):
            tool_name = os.path.splitext(filename)[0]
            if tool_name == "__init__":
                continue
        try:
            # Import the module dynamically
            module = importlib.import_module(f".{tool_name}", __package__)
            # Get the function from the module
            tool_function = getattr(module, tool_name)
            loaded_tools[tool_name] = tool_function
        except Exception as e:
            print(f"Error loading tool {tool_name}: {e}", file=sys.stderr)


# Load tools when the package is imported
load_tools()
