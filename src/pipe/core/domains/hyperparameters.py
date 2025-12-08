"""Domain logic for Hyperparameters.

Separates business logic from data structures (models).
"""

from typing import Any

from pipe.core.models.hyperparameters import Hyperparameters


def merge_hyperparameters(
    existing: Hyperparameters | None, new_params: dict[str, Any]
) -> Hyperparameters:
    """Merge new hyperparameter values with existing ones.

    Args:
        existing: Current Hyperparameters or None
        new_params: Dictionary with hyperparameter updates (partial allowed)

    Returns:
        New Hyperparameters instance with merged values
    """
    if existing:
        # Merge new values with existing hyperparameters
        merged = {
            "temperature": new_params.get("temperature", existing.temperature),
            "top_p": new_params.get("top_p", existing.top_p),
            "top_k": new_params.get("top_k", existing.top_k),
        }
    else:
        # No existing hyperparameters, use new values directly
        merged = new_params

    return Hyperparameters(**merged)
