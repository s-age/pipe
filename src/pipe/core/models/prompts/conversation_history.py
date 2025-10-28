from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from pipe.core.collections.turns import TurnCollection


class PromptConversationHistory(BaseModel):
    description: str
    turns: list[dict[str, Any]]

    @classmethod
    def build(cls, turns: "TurnCollection") -> "PromptConversationHistory":  # noqa: F821
        """Builds the PromptConversationHistory component."""
        from pipe.core.collections.prompts.turn_collection import PromptTurnCollection

        history_turns = list(reversed(list(turns.get_for_prompt())))
        return cls(
            description=(
                "Historical record of past interactions in this session, in "
                "chronological order."
            ),
            turns=PromptTurnCollection(history_turns).get_turns(),
        )
