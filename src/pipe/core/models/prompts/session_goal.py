from pipe.core.models.base import CamelCaseModel


class PromptSessionGoal(CamelCaseModel):
    description: str
    purpose: str
    background: str

    @classmethod
    def build(cls, purpose: str, background: str) -> "PromptSessionGoal":
        """Builds the PromptSessionGoal component."""
        return cls(
            description="This section outlines the goal of the current session.",
            purpose=purpose,
            background=background,
        )
