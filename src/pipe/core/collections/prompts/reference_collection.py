from pipe.core.models.prompts.file_reference import PromptFileReference


class PromptReferenceCollection:
    """
    Manages a collection of prompt file references and handles logic for
    constraining the total size of included file content to fit within context limits.
    """

    def __init__(
        self, references: list[PromptFileReference], token_limit: int = 400000
    ):
        self._references = references
        self.token_limit = token_limit

    def get_content(self) -> list[dict]:
        """
        Returns the content of the references, constrained by the token limit.

        TODO: Implement token counting and content truncation/selection logic.
              For now, it returns all references without modification.
        """
        # Placeholder: In the future, this method will intelligently select and
        # potentially truncate file content based on token count to not exceed
        # self.token_limit.
        return [ref.model_dump() for ref in self._references]
