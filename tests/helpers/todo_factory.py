"""Factory for creating TodoItem test fixtures."""

from pipe.core.models.todo import TodoItem


class TodoFactory:
    """Helper class for creating TodoItem objects in tests."""

    @staticmethod
    def create(
        title: str = "Test Todo",
        description: str = "Test description",
        checked: bool = False,
        **kwargs,
    ) -> TodoItem:
        """Create a TodoItem object with default test values.

        Args:
            title: Todo title (default: "Test Todo")
            description: Todo description (default: "Test description")
            checked: Checked status (default: False)
            **kwargs: Additional fields to override

        Returns:
            TodoItem object
        """
        return TodoItem(title=title, description=description, checked=checked, **kwargs)

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[TodoItem]:
        """Create multiple TodoItem objects.

        Args:
            count: Number of todos to create
            **kwargs: Arguments passed to create()

        Returns:
            List of TodoItem objects
        """
        return [
            TodoFactory.create(title=f"Test Todo {i}", **kwargs) for i in range(count)
        ]
