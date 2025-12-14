"""Session stop action."""

import logging

from pipe.web.action_responses import SessionStopResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.stop_session import StopSessionRequest

logger = logging.getLogger(__name__)


class SessionStopAction(BaseAction):
    """
    Stops a running session by killing its process and rolling back the transaction.

    Flow:
    1. Kill the process (SIGTERM -> SIGKILL if needed)
    2. Rollback transaction (discard changes in pools)
    3. Cleanup process information

    Returns:
        Success message confirming the session was stopped
    """

    request_model = StopSessionRequest

    def execute(self) -> SessionStopResponse:
        from pipe.core.factories.service_factory import ServiceFactory
        from pipe.core.services.process_manager_service import ProcessManagerService
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        session_service = get_session_service()
        session_id = request.session_id

        # Initialize services
        process_manager = ProcessManagerService(session_service.project_root)
        service_factory = ServiceFactory(
            session_service.project_root, session_service.settings
        )
        turn_service = service_factory.create_session_turn_service()

        # 1. Kill the process
        logger.info(f"Attempting to kill process for session {session_id}")
        kill_success = process_manager.kill_process(session_id)

        if not kill_success:
            logger.warning(
                f"Failed to kill process for session {session_id}, "
                "but continuing with cleanup"
            )

        # 2. Rollback transaction (discard all changes in pools)
        logger.info(f"Rolling back transaction for session {session_id}")
        turn_service.rollback_transaction(session_id)

        # 3. Cleanup process information
        logger.info(f"Cleaning up process information for session {session_id}")
        process_manager.cleanup_process(session_id)

        return SessionStopResponse(
            message=f"Session {session_id} stopped and transaction rolled back.",
            session_id=session_id,
        )
