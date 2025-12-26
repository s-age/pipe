"""
Service for session workflow operations.

This service handles complex business workflows that involve sessions,
such as forking sessions and initiating specialized workflow processes.
"""

import sys
import zoneinfo

from pipe.core.domains.session import fork_session
from pipe.core.models.session_optimization import SessionModifications
from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_optimization_service import (
    DoctorResultResponse,
    TherapistResult,
)


class SessionWorkflowService:
    """Service for session workflow operations."""

    def __init__(
        self,
        optimization_service=None,
        repository: SessionRepository = None,
        settings: Settings = None,
        project_root: str | None = None,
    ):
        """Initialize with dependencies.

        Args:
            optimization_service: SessionOptimizationService for workflow operations
            repository: SessionRepository for persistence
            settings: Settings for timezone and model configuration
            project_root: Project root directory for tool loading
        """
        self.optimization_service = optimization_service
        self.repository = repository
        self.settings = settings
        self.project_root = project_root

        # Initialize timezone_obj
        if settings:
            tz_name = settings.timezone
            try:
                self.timezone_obj = zoneinfo.ZoneInfo(tz_name)
            except zoneinfo.ZoneInfoNotFoundError:
                print(
                    f"Warning: Timezone '{tz_name}' not found. Using UTC.",
                    file=sys.stderr,
                )
                self.timezone_obj = zoneinfo.ZoneInfo("UTC")
        else:
            self.timezone_obj = zoneinfo.ZoneInfo("UTC")

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
        original_session = self.repository.find(session_id)
        if not original_session:
            raise FileNotFoundError(
                f"Original session with ID '{session_id}' not found."
            )

        # Use domain logic for fork operation and validation
        new_session = fork_session(original_session, fork_index, self.timezone_obj)

        # Calculate token count for the forked session
        if self.settings and self.project_root:
            new_session.token_count = self._calculate_token_count(new_session)

        self.repository.save(new_session)

        return new_session.session_id

    def _calculate_token_count(self, session) -> int:
        """Calculate token count for a session using GeminiTokenCountService.

        Args:
            session: The session to calculate token count for

        Returns:
            The calculated token count
        """
        try:
            from pipe.core.factories.service_factory import ServiceFactory
            from pipe.core.services.gemini_token_count_service import (
                GeminiTokenCountService,
            )
            from pipe.core.services.gemini_tool_service import GeminiToolService

            # Create service factory to get properly initialized services
            service_factory = ServiceFactory(self.project_root, self.settings)

            # Initialize token count service
            tool_service = GeminiToolService()
            token_count_service = GeminiTokenCountService(
                self.settings, tool_service, self.project_root
            )

            # Get session and prompt services from factory
            session_service = service_factory.create_session_service()
            prompt_service = service_factory.create_prompt_service()

            # Temporarily set the current session to the forked session
            session_service.current_session = session
            session_service.current_session_id = session.session_id

            # Calculate tokens
            token_count = token_count_service.count_tokens_from_prompt(
                session_service, prompt_service
            )

            return token_count
        except Exception as e:
            print(f"Warning: Failed to calculate token count for forked session: {e}")
            # Fallback: return 0 if calculation fails
            return 0

    def run_takt_for_therapist(self, session_id: str) -> TherapistResult:
        """Create therapist session and run initial takt command.

        This workflow initiates a therapeutic optimization process for a session.

        Args:
            session_id: ID of the session to optimize

        Returns:
            TherapistResult with workflow result information

        Delegates to SessionOptimizationService.
        """
        return self.optimization_service.run_therapist(session_id)

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
        return self.optimization_service.run_doctor(session_id, modifications)

    def stop_session(self, session_id: str, project_root: str) -> None:
        """Stop a running session by killing its process and rolling back transaction.

        This workflow consolidates all session stop logic:
        1. Kill the process (SIGTERM -> SIGKILL if needed)
        2. Rollback transaction (discard changes in pools)
        3. Cleanup process information

        Args:
            session_id: ID of the session to stop
            project_root: Path to the project root directory
        """
        import logging

        from pipe.core.factories.service_factory import ServiceFactory
        from pipe.core.factories.settings_factory import SettingsFactory
        from pipe.core.services.process_manager_service import ProcessManagerService

        logger = logging.getLogger(__name__)

        # Get settings from SettingsFactory
        settings = SettingsFactory.get_settings()

        # Initialize services
        process_manager = ProcessManagerService(project_root)
        service_factory = ServiceFactory(project_root, settings)
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
