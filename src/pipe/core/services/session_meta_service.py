"""Service for managing session metadata."""

from pipe.core.domains.hyperparameters import merge_hyperparameters
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import Session, SessionMetaUpdate
from pipe.core.repositories.session_repository import SessionRepository


class SessionMetaService:
    """Handles all metadata-related operations for sessions."""

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def edit_session_meta(self, session_id: str, update_data: SessionMetaUpdate):
        """Edit session metadata with type-safe updates.

        Args:
            session_id: Session ID to edit
            update_data: SessionMetaUpdate model
        """
        session = self.repository.find(session_id)
        if not session:
            return

        self.repository.backup(session)

        # Only update fields that were explicitly set
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(session, key):
                setattr(session, key, value)

        self.repository.save(session)

    def update_hyperparameters(
        self, session_id: str, new_params: Hyperparameters
    ) -> Session:
        """Update session hyperparameters with partial updates.

        Args:
            session_id: Session ID to update
            new_params: Hyperparameters with updates (fields can be None for no change)

        Returns:
            Updated Session object

        Raises:
            FileNotFoundError: If session not found
        """
        session = self.repository.find(session_id)
        if not session:
            raise FileNotFoundError(f"Session {session_id} not found.")

        # Use domain logic to merge hyperparameters
        session.hyperparameters = merge_hyperparameters(
            session.hyperparameters, new_params
        )
        self.repository.save(session)

        return session

    def update_token_count(self, session_id: str, token_count: int):
        session = self.repository.find(session_id)
        if session:
            session.token_count = token_count
            self.repository.save(session)

    def update_cached_content_token_count(
        self, session_id: str, cached_content_token_count: int
    ):
        """Update the cached content token count from API response.

        Args:
            session_id: Session ID to update
            cached_content_token_count: From usage_metadata.cached_content_token_count
        """
        session = self.repository.find(session_id)
        if session:
            session.cached_content_token_count = cached_content_token_count
            self.repository.save(session)

    def update_cached_turn_count(self, session_id: str, cached_turn_count: int):
        """Update the number of turns included in the cache.

        Args:
            session_id: Session ID to update
            cached_turn_count: Number of turns cached
        """
        session = self.repository.find(session_id)
        if session:
            session.cached_turn_count = cached_turn_count
            self.repository.save(session)
