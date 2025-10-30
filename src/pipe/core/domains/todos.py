from typing import TYPE_CHECKING

from pipe.core.models.todo import TodoItem

if TYPE_CHECKING:
    from pipe.core.collections.todos import TodoCollection
    from pipe.core.models.session import Session


def update_todos_in_session(session: "Session", todos_data: list[dict | TodoItem]):
    """Updates the todos list in a session object. Does not save."""
    session.todos = [TodoItem(**t) if isinstance(t, dict) else t for t in todos_data]


def delete_todos_in_session(session: "Session"):
    """Deletes all todos from a session object. Does not save."""
    session.todos = None


def get_todos_for_prompt(todos_collection: "TodoCollection") -> list[dict]:
    """
    Returns a list of todos suitable for inclusion in a prompt.
    Currently, this converts each TodoItem object to its dictionary representation.
    """
    return [todo.model_dump() for todo in todos_collection] if todos_collection else []
