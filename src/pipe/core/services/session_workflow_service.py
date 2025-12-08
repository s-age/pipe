"""
Service for session workflow operations.

This service handles complex business workflows that involve sessions,
such as forking sessions and initiating specialized workflow processes.
"""

from pipe.core.domains.session import fork_session
from pipe.core.domains.session_optimization import SessionModifications
from pipe.core.services.session_optimization_service import DoctorResultResponse


class SessionWorkflowService:
    """Service for session workflow operations."""

    def __init__(self, session_service):
        """Initialize with a reference to SessionService.

        Args:
            session_service: SessionService instance for data access and operations
        """
        self.session_service = session_service

    def fork_session(self, session_id: str, fork_index: int) -> str | None:
        """Fork a session at a specific turn index.

        Creates a new session that branches from the original session at the specified
        turn. The new session inherits all turns up to and including the fork point.

        Args:
            session_id: ID of the session to fork
            fork_index: Index of the turn to fork from (must be a model_response turn)

        Returns:
            ID of the newly created forked session

        Raises:
            FileNotFoundError: If the original session is not found
            IndexError: If fork_index is out of range
            ValueError: If the turn at fork_index is not a model_response
        """
        original_session = self.session_service._fetch_session(session_id)
        if not original_session:
            raise FileNotFoundError(
                f"Original session with ID '{session_id}' not found."
            )

        # Use domain logic for fork operation and validation
        new_session = fork_session(
            original_session, fork_index, self.session_service.timezone_obj
        )

        self.session_service.repository.save(new_session)

        return new_session.session_id

    def run_takt_for_therapist(self, session_id: str) -> dict[str, str]:
        """Create therapist session and run initial takt command.

        This workflow initiates a therapeutic optimization process for a session.

        Args:
            session_id: ID of the session to optimize

        Returns:
            Dictionary with workflow result information

        Delegates to SessionOptimizationService.
        """
        return self.session_service._get_optimization_service().run_therapist(
            session_id
        )

    def run_takt_for_doctor(
        self, session_id: str, modifications: SessionModifications
    ) -> DoctorResultResponse:
        """Create doctor session and run modifications.

        This workflow applies doctor-prescribed modifications to a session.

        Args:
            session_id: ID of the session to modify
            modifications: Modifications to apply

        Returns:
            Response containing the result of the doctor workflow

        Delegates to SessionOptimizationService.
        """
        return self.session_service._get_optimization_service().run_doctor(
            session_id, modifications
        )
