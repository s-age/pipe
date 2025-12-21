"""Domain logic for TaktArgs.

Separates conversion logic from data structures (models).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipe.core.models.args import TaktArgs
    from pipe.core.models.turn import UserTaskTurn


def convert_args_to_turn(args: "TaktArgs", timestamp: str) -> "UserTaskTurn":
    """Converts TaktArgs to a UserTaskTurn.

    Args:
        args: The TaktArgs to convert
        timestamp: The timestamp for the turn

    Returns:
        UserTaskTurn created from the args
    """
    from pipe.core.models.turn import UserTaskTurn

    return UserTaskTurn(
        type="user_task", instruction=args.instruction, timestamp=timestamp
    )
