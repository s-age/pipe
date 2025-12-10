"""Agent registry and auto-discovery system.

This module provides a plugin-like architecture for agents. New agents can be
added by simply creating a new file in this directory and decorating the class
with @register_agent("mode-name").
"""

import importlib
import pkgutil

from .base import BaseAgent

# Registry mapping api_mode strings to Agent classes
AGENT_REGISTRY: dict[str, type[BaseAgent]] = {}


def register_agent(key: str):
    """Decorator to register an agent class in the registry.

    Usage:
        @register_agent("gemini-api")
        class GeminiApiAgent(BaseAgent):
            ...

    Args:
        key: The api_mode string that this agent handles

    Returns:
        The decorator function
    """

    def decorator(cls: type[BaseAgent]):
        AGENT_REGISTRY[key] = cls
        return cls

    return decorator


# Auto-discover and import all modules in this package
# This triggers the @register_agent decorators in each module
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    if module_name in ("base",):  # Skip base module
        continue
    try:
        importlib.import_module(f".{module_name}", __package__)
    except Exception as e:
        # Print import errors to help debug registration issues
        import sys

        print(
            f"Warning: Failed to import agent module '{module_name}': {e}",
            file=sys.stderr,
        )
        # Silently skip modules that fail to import
        # (e.g., missing dependencies for optional agents)
        pass


def get_agent_class(key: str) -> type[BaseAgent]:
    """Get an agent class from the registry.

    Args:
        key: The api_mode string (e.g., "gemini-api", "gemini-cli")

    Returns:
        The agent class

    Raises:
        ValueError: If the key is not found in the registry
    """
    agent_cls = AGENT_REGISTRY.get(key)
    if not agent_cls:
        available = ", ".join(sorted(AGENT_REGISTRY.keys()))
        raise ValueError(f"Unknown api_mode: '{key}'. Available agents: [{available}]")
    return agent_cls


__all__ = ["BaseAgent", "register_agent", "get_agent_class", "AGENT_REGISTRY"]
