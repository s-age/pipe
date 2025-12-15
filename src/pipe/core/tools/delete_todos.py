import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.results.delete_todos_result import DeleteTodosResult


def delete_todos(session_service=None, session_id=None) -> DeleteTodosResult:
    """
    Deletes the list of TODO items from the current session data.
    """
    if not session_service:
        return DeleteTodosResult(error="This tool requires a session_service.")

    target_session_id = session_id or os.environ.get("PIPE_SESSION_ID")
    if not target_session_id:
        return DeleteTodosResult(error="No session_id provided.")

    try:
        factory = ServiceFactory(session_service.project_root, session_service.settings)
        todo_service = factory.create_session_todo_service()

        todo_service.delete_todos(target_session_id)
        # Retrieve the updated todos (should be empty)
        updated_session = session_service.get_session(target_session_id)
        if not updated_session:
            return DeleteTodosResult(
                error=f"Session with ID {target_session_id} not found."
            )
        # Handle the case where updated_session.todos is None (after deletion)
        updated_todos = (
            updated_session.todos if updated_session.todos is not None else []
        )

        return DeleteTodosResult(
            message=f"Todos successfully deleted from session {target_session_id}.",
            current_todos=[todo.model_dump() for todo in updated_todos],
        )
    except Exception as e:
        return DeleteTodosResult(error=f"Failed to delete todos from session: {e}")
