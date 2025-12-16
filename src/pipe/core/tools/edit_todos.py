import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.results.edit_todos_result import EditTodosResult
from pipe.core.models.todo import TodoItem
from pipe.core.models.tool_result import ToolResult


def edit_todos(
    todos: list[TodoItem], session_service=None, session_id=None
) -> ToolResult[EditTodosResult]:
    """
    Edits the list of TODO items directly within the session data.

    Example:
    edit_todos(todos=[{"title": "test1", "description": "", "checked": False},
    {"title": "test2", "description": "", "checked": False}])
    """
    if not session_service:
        return ToolResult(error="This tool requires a session_service.")

    target_session_id = session_id or os.environ.get("PIPE_SESSION_ID")
    if not target_session_id:
        return ToolResult(error="No session_id provided.")

    try:
        factory = ServiceFactory(session_service.project_root, session_service.settings)
        todo_service = factory.create_session_todo_service()

        todo_service.update_todos(target_session_id, todos)
        # Retrieve the updated todos by getting the session and accessing its
        # todos attribute
        updated_session = session_service.get_session(target_session_id)
        if not updated_session:
            return ToolResult(error=f"Session with ID {target_session_id} not found.")
        updated_todos = updated_session.todos

        result = EditTodosResult(
            message=f"Todos successfully updated in session {target_session_id}.",
            current_todos=[todo.model_dump() for todo in updated_todos],
        )
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(error=f"Failed to update todos in session: {e}")
