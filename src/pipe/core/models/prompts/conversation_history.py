from typing import TYPE_CHECKING

from pipe.core.models.turn import Turn
from pydantic import BaseModel

if TYPE_CHECKING:
    from pipe.core.collections.turns import TurnCollection


class PromptConversationHistory(BaseModel):
    description: str
    turns: list[Turn]

    @classmethod
    def build(
        cls, turns: "TurnCollection", tool_response_limit: int = 3
    ) -> "PromptConversationHistory":  # noqa: F821
        """Builds the PromptConversationHistory component."""
        from pipe.core.domains.turns import get_turns_for_prompt

        # get_turns_for_prompt yields turns in reverse order (newest first).
        # We need to reverse them back to chronological order (oldest first).
        history_turns = list(get_turns_for_prompt(turns, tool_response_limit))
        history_turns.reverse()

        return cls(
            description=(
                "Historical record of past interactions in this session, in "
                "chronological order."
            ),
            turns=history_turns,
        )
