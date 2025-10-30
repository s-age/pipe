from collections.abc import Iterator
from typing import TYPE_CHECKING

from pipe.core.models.turn import ToolResponseTurn, Turn


class TurnCollection(list[Turn]):
    """
    A collection of Turn objects, providing utility methods for turn management.
    """

    if TYPE_CHECKING:
        from pipe.core.collections.turns import TurnCollection

    def get_turns_for_prompt(self, tool_response_limit: int = 3) -> Iterator[Turn]:
        """
        Yields turns for prompt generation, applying filtering rules.
        - The last turn (current task) is excluded.
        - Only the last N 'tool_response' turns from the history are included.
        """
        tool_response_count = 0
        history = self[:-1]  # Exclude the last turn

        # Iterate in reverse to easily count the last N tool_responses
        for turn in reversed(history):
            if isinstance(turn, ToolResponseTurn):
                tool_response_count += 1
                if tool_response_count > tool_response_limit:
                    continue
            yield turn
