from pipe.core.models.base import CamelCaseModel
from pipe.core.models.turn import Turn


class PromptConversationHistory(CamelCaseModel):
    description: str
    turns: list[Turn]
