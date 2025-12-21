"""Domain logic for Hyperparameters.

Separates business logic from data structures (models).
"""

from pipe.core.models.hyperparameters import Hyperparameters


def merge_hyperparameters(
    existing: Hyperparameters | None, new_params: Hyperparameters
) -> Hyperparameters:
    """Merge new hyperparameter values with existing ones.

    Args:
        existing: Current Hyperparameters or None
        new_params: Hyperparameters with updates (fields can be None for no change)

    Returns:
        New Hyperparameters instance with merged values
    """
    if existing:
        # Merge: use new value if provided, otherwise keep existing
        return Hyperparameters(
            temperature=(
                new_params.temperature
                if new_params.temperature is not None
                else existing.temperature
            ),
            top_p=new_params.top_p if new_params.top_p is not None else existing.top_p,
            top_k=new_params.top_k if new_params.top_k is not None else existing.top_k,
        )
    else:
        # No existing hyperparameters, use new values directly
        return new_params
