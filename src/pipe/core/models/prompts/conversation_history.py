from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from pipe.core.collections.turns import TurnCollection


class PromptConversationHistory(BaseModel):
    description: str
    turns: list[dict[str, Any]]

    @classmethod
    def build(
        cls, turns: "TurnCollection", tool_response_limit: int = 3
    ) -> "PromptConversationHistory":  # noqa: F821
        """Builds the PromptConversationHistory component."""
        from pipe.core.domains.turns import get_turns_for_prompt

        history_turns = [
            turn.model_dump()
            for turn in reversed(list(get_turns_for_prompt(turns, tool_response_limit)))
        ]
        return cls(
            description=(
                "Historical record of past interactions in this session, in "
                "chronological order."
            ),
            turns=history_turns,
        )
