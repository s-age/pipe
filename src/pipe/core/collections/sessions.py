from __future__ import annotations
from typing import Dict, Optional, Iterator
import json
import hashlib

from pipe.core.models.session import Session
from pipe.core.utils.datetime import get_current_timestamp

class SessionCollection:
    """
    Manages a collection of Session objects in memory and provides collection-level operations.
    This class is designed to be independent of the storage layer.
    """
    def __init__(self, sessions: Dict[str, Session], timezone_obj):
        self._sessions: Dict[str, Session] = sessions
        self.timezone_obj = timezone_obj

    def __iter__(self) -> Iterator[str]:
        return iter(self._sessions)

    def __len__(self) -> int:
        return len(self._sessions)

    def find(self, session_id: str) -> Optional[Session]:
        """Finds a session by its ID."""
        return self._sessions.get(session_id)

    def add(self, session: Session):
        """Adds a new session to the collection."""
        if session.session_id in self._sessions:
            raise ValueError(f"Session with ID '{session.session_id}' already exists.")
        self._sessions[session.session_id] = session

    def delete(self, session_id: str) -> bool:
        """Deletes a session from the collection. Returns True if successful."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            # Also delete children sessions
            children_to_delete = [sid for sid in self._sessions if sid.startswith(f"{session_id}/")]
            for child_id in children_to_delete:
                del self._sessions[child_id]
            return True
        return False

    def fork(self, original_session_id: str, fork_index: int, default_hyperparameters) -> Session:
        """
        Creates a new forked session object from an existing session.
        This method returns the new Session object but does not add it to the collection itself.
        The caller (e.g., SessionService) is responsible for adding it.
        """
        original_session = self.find(original_session_id)
        if not original_session:
            raise FileNotFoundError(f"Original session with ID '{original_session_id}' not found.")

        if not (0 <= fork_index < len(original_session.turns)):
            raise IndexError("fork_index is out of range.")
        
        fork_turn = original_session.turns[fork_index]
        if fork_turn.type != "model_response":
            raise ValueError(f"Forking is only allowed from a 'model_response' turn. Turn {fork_index + 1} is of type '{fork_turn.type}'.")

        timestamp = get_current_timestamp(self.timezone_obj)
        forked_purpose = f"Fork of: {original_session.purpose}"
        forked_turns = original_session.turns[:fork_index + 1]

        identity_str = json.dumps({
            "purpose": forked_purpose, 
            "original_id": original_session_id,
            "fork_at_turn": fork_index,
            "timestamp": timestamp
        }, sort_keys=True)
        new_session_id_suffix = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

        parent_path = original_session_id.rsplit('/', 1)[0] if '/' in original_session_id else None
        new_session_id = f"{parent_path}/{new_session_id_suffix}" if parent_path else new_session_id_suffix

        new_session = Session(
            session_id=new_session_id,
            created_at=timestamp,
            purpose=forked_purpose,
            background=original_session.background,
            roles=original_session.roles,
            multi_step_reasoning_enabled=original_session.multi_step_reasoning_enabled,
            hyperparameters=original_session.hyperparameters or default_hyperparameters,
            references=original_session.references,
            turns=forked_turns
        )
        return new_session

    def list_all(self) -> Dict[str, Session]:
        """Returns the entire dictionary of sessions."""
        return self._sessions
