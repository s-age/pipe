from __future__ import annotations

from pipe.core.models.todo import TodoItem


class TodoCollection:
    """
    Manages a list of TodoItem objects and provides utility methods for them.
    This class is used as a transient logic container and does not handle its own
    persistence.
    It is instantiated on-the-fly with a list of todos to perform operations like
    sorting, filtering, and preparing them for prompts.
    """

    def __init__(self, todos: list[TodoItem]):
        self._todos = todos if todos is not None else []

    def get_for_prompt(self) -> list[dict]:
        """
        Returns a list of todos suitable for inclusion in a prompt.
        Currently, this converts each TodoItem object to its dictionary representation.
        """
        return [todo.model_dump() for todo in self._todos]

    # Future methods for sorting and filtering can be added here.
    # For example:
    #
    # def get_sorted_by_priority(self) -> List[TodoItem]:
    #     # Sorting logic here
    #     pass
    #
    # def filter_by_status(self, status: str) -> List[TodoItem]:
    #     # Filtering logic here
    #     pass
