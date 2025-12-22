"""Factory for creating PromptTodo test fixtures."""

from pipe.core.models.prompts.todo import PromptTodo


class PromptTodoFactory:
    """Helper class for creating PromptTodo objects in tests."""

    @staticmethod
    def create(
        title: str = "Test Todo",
        description: str = "Test description",
        checked: bool = False,
        **kwargs,
    ) -> PromptTodo:
        """Create a PromptTodo object with default test values.

        Args:
            title: Todo title (default: "Test Todo")
            description: Todo description (default: "Test description")
            checked: Checked status (default: False)
            **kwargs: Additional fields to override

        Returns:
            PromptTodo object
        """
        return PromptTodo(
            title=title, description=description, checked=checked, **kwargs
        )

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[PromptTodo]:
        """Create multiple PromptTodo objects.

        Args:
            count: Number of todos to create
            **kwargs: Arguments passed to create()

        Returns:
            List of PromptTodo objects
        """
        return [
            PromptTodoFactory.create(title=f"Test Todo {i}", **kwargs)
            for i in range(count)
        ]
