"""Helper factory for creating test Settings objects."""

from pipe.core.models.settings import Settings


def create_test_settings(**overrides) -> Settings:
    """
    Create a Settings object for testing with sensible defaults.

    Args:
        **overrides: Any field values to override in the settings.
                    Special keys:
                    - model_name: Name of the model (default: "gemini-test")
                    - context_limit: Context window limit (default: 10000)
                    - cache_update_threshold: Cache threshold (default: 20000)

    Returns:
        A fully configured Settings object suitable for testing
    """
    # Extract model-specific overrides
    model_name = overrides.pop("model_name", "gemini-test")
    context_limit = overrides.pop("context_limit", 10000)
    cache_update_threshold = overrides.pop("cache_update_threshold", 20000)

    # Handle both old-style (model as string) and new-style (model_configs) input
    if "model_configs" not in overrides:
        default_model_config = {
            "name": model_name,
            "context_limit": context_limit,
            "cache_update_threshold": cache_update_threshold,
        }
        overrides["model_configs"] = [default_model_config]

    # Set model and search_model if not provided
    if "model" not in overrides:
        overrides["model"] = model_name
    if "search_model" not in overrides:
        overrides["search_model"] = overrides.get("model", model_name)

    settings_data = {
        "api_mode": "gemini-api",
        "language": "en",
        "yolo": False,
        "expert_mode": False,
        "timezone": "UTC",
        "parameters": {
            "temperature": {"value": 0.1, "description": "t"},
            "top_p": {"value": 0.2, "description": "p"},
            "top_k": {"value": 10, "description": "k"},
        },
    }

    # Apply any additional overrides
    settings_data.update(overrides)

    return Settings(**settings_data)
