"""
Validators for new session creation arguments.
"""


def validate(purpose: str | None, background: str | None):
    """
    Validates that the purpose and background for a new session are provided.

    Args:
        purpose: The purpose of the new session.
        background: The background context for the new session.

    Raises:
        ValueError: If purpose or background is None or an empty string.
    """
    if not purpose:
        raise ValueError("Purpose is required for a new session.")
    if not background:
        raise ValueError("Background is required for a new session.")
