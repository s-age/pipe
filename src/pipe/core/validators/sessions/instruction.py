"""
Validator for the instruction argument.
"""


def validate(instruction: str | None):
    """
    Validates that the instruction is provided and not an empty string.

    Args:
        instruction: The instruction for the current task.

    Raises:
        ValueError: If the instruction is None or empty.
    """
    if not instruction:
        raise ValueError("Instruction is required.")
