"""Service for managing session turns and pools."""

from typing import Any

from pipe.core.collections.pools import PoolCollection
from pipe.core.domains.turns import delete_turns, expire_old_tool_responses
from pipe.core.models.settings import Settings
from pipe.core.models.turn import (
    ModelResponseTurnUpdate,
    Turn,
    UserTaskTurnUpdate,
)
from pipe.core.services.session_service import SessionService


class SessionTurnService:
    """Handles all turn and pool-related operations for sessions."""

    def __init__(self, settings: Settings, session_service: SessionService):
        self.settings = settings
        self.session_service = session_service

    def delete_turn(self, session_id: str, turn_index: int):
        """Deletes a specific turn from a session."""
        session = self.session_service._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")
        session.turns.delete_by_index(turn_index)
        self.session_service.repository.save(session)

    def delete_turns(self, session_id: str, turn_indices: list[int]):
        """Deletes multiple turns from a session, handling index shifts."""
        session = self.session_service._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        delete_turns(session, turn_indices)
        self.session_service.repository.save(session)

    def edit_turn(
        self,
        session_id: str,
        turn_index: int,
        new_data: UserTaskTurnUpdate | ModelResponseTurnUpdate | dict[str, Any],
    ):
        """Edits a specific turn in a session.

        Args:
            session_id: The session ID
            turn_index: Index of the turn to edit
            new_data: Update data - accepts typed Update DTOs or dict
                      for I/O Boundary (5-1)
        """
        session = self.session_service._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")
        session.turns.edit_by_index(turn_index, new_data)
        self.session_service.repository.save(session)

    def add_turn_to_session(self, session_id: str, turn_data: Turn):
        """Adds a turn to a session."""
        session = self.session_service._fetch_session(session_id)
        if session:
            session.turns.add(turn_data)
            self.session_service.repository.save(session)

    def merge_pool_into_turns(self, session_id: str):
        """Merges all turns from the pool into the main turns list and clears the
        pool."""
        from pipe.core.collections.turns import TurnCollection

        session = self.session_service._fetch_session(session_id)
        if session and session.pools:
            session.turns.merge_from(session.pools)
            session.pools = TurnCollection()
            self.session_service.repository.save(session)

    def add_to_pool(self, session_id: str, pool_data: Turn):
        """Adds a turn to the session's pool."""
        session = self.session_service._fetch_session(session_id)
        if session:
            PoolCollection.add(session, pool_data)
            self.session_service.repository.save(session)

    def get_pool(self, session_id: str) -> list[Turn]:
        """Gets all turns from the session's pool."""
        session = self.session_service._fetch_session(session_id)
        return session.pools if session else []

    def get_and_clear_pool(self, session_id: str) -> list[Turn]:
        """Gets all turns from the pool and clears it."""
        session = self.session_service._fetch_session(session_id)
        if not session:
            return []

        pools_to_return = PoolCollection.get_and_clear(session)
        self.session_service.repository.save(session)
        return pools_to_return

    def expire_old_tool_responses(self, session_id: str):
        """Expires the message content of old tool_responses to save tokens."""
        session = self.session_service._fetch_session(session_id)
        if session:
            if expire_old_tool_responses(
                session.turns, self.settings.tool_response_expiration
            ):
                self.session_service._save_session(session)
