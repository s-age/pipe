from pipe.core.models.turn import Turn


class PromptTurnCollection:
    """
    Manages a collection of conversation turns for the prompt and handles logic
    for constraining the history size to fit within context limits.
    """

    def __init__(self, turns: list[Turn], token_limit: int = 120000):
        self._turns = turns
        self.token_limit = token_limit

    def get_turns(self) -> list[Turn]:
        """
        Returns the turns for the prompt, constrained by the token limit.

        TODO: Implement token counting and turn filtering logic.
              For now, it returns all turns converted to dictionaries.
        """
        # Placeholder: In the future, this method will intelligently select turns
        # (e.g., omitting older ones) based on token count to not exceed
        # self.token_limit.
        return self._turns
