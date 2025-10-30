from collections.abc import Iterator
from typing import TYPE_CHECKING

from pipe.core.models.turn import ToolResponseTurn, Turn

if TYPE_CHECKING:
    from pipe.core.collections.turns import TurnCollection


def get_turns_for_prompt(
    turns_collection: "TurnCollection", tool_response_limit: int = 3
) -> Iterator[Turn]:
    """
    Yields turns for prompt generation, applying filtering rules.
    - The last turn (current task) is excluded.
    - Only the last N 'tool_response' turns from the history are included.
    """
    tool_response_count = 0
    history = turns_collection[:-1]  # Exclude the last turn

    # Iterate in reverse to easily count the last N tool_responses
    for turn in reversed(history):
        if isinstance(turn, ToolResponseTurn):
            tool_response_count += 1
            if tool_response_count > tool_response_limit:
                continue
        yield turn


def expire_old_tool_responses(
    turns_collection: "TurnCollection", expiration_threshold: int = 3
) -> bool:
    """
    Expires the message content of old tool_response turns to save tokens,
    while preserving the 'succeeded' status. This uses a safe rebuild pattern.
    Returns True if any turns were modified.
    """
    if not turns_collection:
        return False

    user_tasks = [turn for turn in turns_collection if turn.type == "user_task"]
    if len(user_tasks) <= expiration_threshold:
        return False

    expiration_threshold_timestamp = user_tasks[-expiration_threshold].timestamp

    new_turns = []
    modified = False
    for turn in turns_collection:
        if (
            turn.type == "tool_response"
            and turn.timestamp < expiration_threshold_timestamp
            and isinstance(turn.response, dict)
            and turn.response.get("status") == "succeeded"
        ):
            modified_turn = turn.model_copy(deep=True)
            modified_turn.response["message"] = (
                "This tool response has expired to save tokens."
            )
            new_turns.append(modified_turn)
            modified = True
        else:
            new_turns.append(turn)

    if modified:
        turns_collection[:] = new_turns

    return modified
