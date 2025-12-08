"""Service for managing session metadata."""

from typing import Any

from pipe.core.domains.hyperparameters import merge_hyperparameters
from pipe.core.models.session import Session, SessionMetaUpdate
from pipe.core.services.session_service import SessionService


class SessionMetaService:
    """Handles all metadata-related operations for sessions."""

    def __init__(self, session_service: SessionService):
        self.session_service = session_service

    def edit_session_meta(
        self, session_id: str, update_data: SessionMetaUpdate | dict[str, Any]
    ):
        """Edit session metadata with type-safe updates.

        Args:
            session_id: Session ID to edit
            update_data: SessionMetaUpdate model or dict (for backward compatibility)
        """
        session = self.session_service._fetch_session(session_id)
        if not session:
            return

        # Convert dict to SessionMetaUpdate for validation
        if isinstance(update_data, dict):
            update_data = SessionMetaUpdate(**update_data)

        self.session_service.repository.backup(session)

        # Only update fields that were explicitly set
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(session, key):
                setattr(session, key, value)

        self.session_service.repository.save(session)

    def update_hyperparameters(
        self, session_id: str, new_params: dict[str, Any]
    ) -> Session:
        """Update session hyperparameters with partial updates.

        Args:
            session_id: Session ID to update
            new_params: Dictionary with hyperparameter updates (partial allowed)

        Returns:
            Updated Session object

        Raises:
            FileNotFoundError: If session not found
        """
        session = self.session_service._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session {session_id} not found.")

        # Use domain logic to merge hyperparameters
        session.hyperparameters = merge_hyperparameters(
            session.hyperparameters, new_params
        )
        self.session_service.repository.save(session)

        return session

    def update_token_count(self, session_id: str, token_count: int):
        session = self.session_service._fetch_session(session_id)
        if session:
            session.token_count = token_count
            self.session_service.repository.save(session)
