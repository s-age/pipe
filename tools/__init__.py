import os
import importlib
from pathlib import Path

# This dictionary will store the loaded tool functions
loaded_tools = {}

def load_tools():
    """
    Dynamically loads all Python files in the 'tools' directory as tool functions.
    Each file is expected to define a single function with the same name as the file (without .py extension).
    """
    tools_dir = Path(__file__).parent
    for tool_file in tools_dir.glob("*.py"):
        if tool_file.name == "__init__.py":
            continue

        tool_name = tool_file.stem  # Get filename without extension
        try:
            # Import the module dynamically
            module = importlib.import_module(f"tools.{tool_name}")
            # Get the function from the module
            tool_function = getattr(module, tool_name)
            loaded_tools[tool_name] = tool_function
            print(f"Loaded tool: {tool_name}")
        except Exception as e:
            print(f"Error loading tool {tool_name}: {e}")

# Load tools when the package is imported
load_tools()
