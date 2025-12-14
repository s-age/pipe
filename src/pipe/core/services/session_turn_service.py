"""Service for managing session turns and pools."""

import zoneinfo
from typing import Any

from pipe.core.collections.pools import PoolCollection
from pipe.core.domains.turns import delete_turns, expire_old_tool_responses
from pipe.core.models.settings import Settings
from pipe.core.models.turn import (
    ModelResponseTurnUpdate,
    Turn,
    UserTaskTurnUpdate,
)
from pipe.core.repositories.session_repository import SessionRepository


class SessionTurnService:
    """Handles all turn and pool-related operations for sessions."""

    def __init__(
        self,
        settings: Settings,
        repository: SessionRepository,
    ):
        self.settings = settings
        self.repository = repository

        # Convert timezone string to ZoneInfo object
        try:
            self.timezone = zoneinfo.ZoneInfo(settings.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            # Fallback to UTC if timezone not found
            self.timezone = zoneinfo.ZoneInfo("UTC")

    def delete_turn(self, session_id: str, turn_index: int):
        """Deletes a specific turn from a session."""
        session = self.repository.find(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")
        session.turns.delete_by_index(turn_index)
        self.repository.save(session)

    def delete_turns(self, session_id: str, turn_indices: list[int]):
        """Deletes multiple turns from a session, handling index shifts."""
        session = self.repository.find(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        delete_turns(session, turn_indices)
        self.repository.save(session)

    def edit_turn(
        self,
        session_id: str,
        turn_index: int,
        new_data: UserTaskTurnUpdate | ModelResponseTurnUpdate | dict[str, Any],
    ):
        """
        Edits a specific turn in a session.

        Args:
            session_id: The session ID
            turn_index: Index of the turn to edit
            new_data: Update data - accepts typed Update DTOs or dict[str, Any]
                     Dict is converted to appropriate DTO at I/O boundary

        Raises:
            FileNotFoundError: If session not found
            IndexError: If turn_index is out of range
            ValueError: If turn type cannot be edited or invalid update data

        Note:
            This method accepts dict[str, Any] at the service layer (I/O boundary)
            to support external callers (API, CLI, etc.). Dicts are automatically
            validated and converted to typed DTOs before being passed to the
            domain layer.
        """
        session = self.repository.find(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        # Validate turn index first
        if not (0 <= turn_index < len(session.turns)):
            raise IndexError("Turn index out of range.")

        # Convert dict to appropriate DTO at I/O boundary
        if isinstance(new_data, dict):
            turn = session.turns[turn_index]
            try:
                if turn.type == "user_task":
                    new_data = UserTaskTurnUpdate.model_validate(new_data)
                elif turn.type == "model_response":
                    new_data = ModelResponseTurnUpdate.model_validate(new_data)
                else:
                    raise ValueError(
                        f"Editing turns of type '{turn.type}' is not allowed."
                    )
            except ValueError as e:
                # Re-raise Pydantic validation errors with context
                raise ValueError(f"Invalid turn update data: {e}") from e

        session.turns.edit_by_index(turn_index, new_data)
        self.repository.save(session)

    def add_turn_to_session(self, session_id: str, turn_data: Turn):
        """Adds a turn to a session."""
        session = self.repository.find(session_id)
        if session:
            session.turns.add(turn_data)
            self.repository.save(session)

    def merge_pool_into_turns(self, session_id: str):
        """Merges all turns from the pool into the main turns list and clears the
        pool."""
        from pipe.core.collections.turns import TurnCollection

        session = self.repository.find(session_id)
        if session and session.pools:
            session.turns.merge_from(session.pools)
            session.pools = TurnCollection()
            self.repository.save(session)

    def add_to_pool(self, session_id: str, pool_data: Turn):
        """Adds a turn to the session's pool."""
        session = self.repository.find(session_id)
        if session:
            PoolCollection.add(session, pool_data)
            self.repository.save(session)

    def get_pool(self, session_id: str) -> list[Turn]:
        """Gets all turns from the session's pool."""
        session = self.repository.find(session_id)
        return session.pools if session else []

    def get_and_clear_pool(self, session_id: str) -> list[Turn]:
        """Gets all turns from the pool and clears it."""
        session = self.repository.find(session_id)
        if not session:
            return []

        pools_to_return = PoolCollection.get_and_clear(session)
        self.repository.save(session)
        return pools_to_return

    def expire_old_tool_responses(self, session_id: str):
        """Expires the message content of old tool_responses to save tokens."""
        session = self.repository.find(session_id)
        if session:
            if expire_old_tool_responses(
                session.turns, self.settings.tool_response_expiration
            ):
                self.repository.save(session)

    # ========== Transaction Methods ==========

    def start_transaction(self, session_id: str, instruction: str):
        """
        Start a transaction by adding user_instruction to pools.

        Transaction Flow:
        1. Read or create session file
        2. Create user_task turn and add to pools (temporary area)
        3. Save session with updated pools

        Args:
            session_id: Session identifier
            instruction: User instruction to execute

        Returns:
            Session object with user_task in pools

        Note:
            pools is a temporary storage area. Changes are not reflected in turns
            until commit_transaction() is called.
        """
        from pipe.core.models.turn import UserTaskTurn
        from pipe.core.utils.datetime import get_current_timestamp

        session = self.repository.find(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Create user_task turn and add to pools
        user_turn = UserTaskTurn(
            type="user_task",
            instruction=instruction,
            timestamp=get_current_timestamp(self.timezone),
        )

        PoolCollection.add(session, user_turn)
        self.repository.save(session)

        return session

    def add_to_transaction(self, session_id: str, turn_data: Turn) -> None:
        """
        Add a turn to the transaction (pools area).

        Args:
            session_id: Session identifier
            turn_data: Turn to add (model_response, function_calling,
                tool_response, etc.)

        Note:
            pools is a temporary storage area (not the main database).
            Changes are saved to the session file but only in the pools field.
            Call commit_transaction() to merge pools into turns for persistence.
        """
        session = self.repository.find(session_id)
        if session:
            PoolCollection.add(session, turn_data)
            self.repository.save(session)

    def commit_transaction(self, session_id: str) -> None:
        """
        Commit the transaction by merging pools into turns.

        Transaction Flow:
        1. Move all turns from pools to turns
        2. Clear pools
        3. Save session (transaction completed)

        Args:
            session_id: Session identifier

        Note:
            After this operation, all changes in pools are persisted to turns.
            This completes the transaction.
        """
        from pipe.core.collections.turns import TurnCollection

        session = self.repository.find(session_id)
        if session and session.pools:
            session.turns.merge_from(session.pools)
            session.pools = TurnCollection()
            self.repository.save(session)

    def rollback_transaction(self, session_id: str) -> None:
        """
        Rollback the transaction by discarding all changes in pools.

        Transaction Flow:
        1. Clear pools (discard all temporary changes)
        2. Save session

        Args:
            session_id: Session identifier

        Note:
            Used when errors occur or process is stopped. Discards all changes
            made since start_transaction(), effectively rolling back to the
            state before the transaction started.
        """
        from pipe.core.collections.turns import TurnCollection

        session = self.repository.find(session_id)
        if session:
            session.pools = TurnCollection()
            self.repository.save(session)
