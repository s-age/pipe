"""
Common utilities for Pydantic request models.

Provides automatic camelCase to snake_case conversion for all request models.
"""

import re
from typing import Any


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def normalize_camel_case_keys(data: Any) -> Any:
    """
    Recursively convert camelCase keys to snake_case in dictionaries.
    
    This allows frontend to send camelCase while backend uses snake_case.
    Only converts keys that match camelCase pattern (contain uppercase letters).
    """
    if not isinstance(data, dict):
        return data
    
    normalized = {}
    for key, value in data.items():
        # Convert key to snake_case if it contains uppercase
        if any(c.isupper() for c in key):
            snake_key = camel_to_snake(key)
            # Only use snake_case version if it doesn't already exist
            if snake_key not in data:
                normalized[snake_key] = normalize_camel_case_keys(value) if isinstance(value, dict) else value
            else:
                normalized[key] = normalize_camel_case_keys(value) if isinstance(value, dict) else value
        else:
            normalized[key] = normalize_camel_case_keys(value) if isinstance(value, dict) else value
    
    return normalized
