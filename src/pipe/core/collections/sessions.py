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
    def __init__(self, sessions: Dict[str, Session], timezone_obj, index_data: Dict):
        self._sessions: Dict[str, Session] = sessions # This will be empty initially
        self.timezone_obj = timezone_obj
        self._index_data = index_data

    def __iter__(self) -> Iterator[str]:
        return iter(self._index_data.get('sessions', {}))

    def __len__(self) -> int:
        return len(self._index_data.get('sessions', {}))

    def find(self, session_id: str) -> Optional[dict]:
        """Finds a session's metadata by its ID from the index."""
        return self._index_data.get('sessions', {}).get(session_id)

    def add(self, session: Session):
        """Adds a new session to the collection."""
        if 'sessions' not in self._index_data:
            self._index_data['sessions'] = {}
        if session.session_id in self._index_data['sessions']:
            raise ValueError(f"Session with ID '{session.session_id}' already exists.")
        self._index_data['sessions'][session.session_id] = {
            "purpose": session.purpose,
            "created_at": session.created_at,
            "last_updated": get_current_timestamp(self.timezone_obj)
        }

    def delete(self, session_id: str) -> bool:
        """Deletes a session from the collection. Returns True if successful."""
        if 'sessions' in self._index_data and session_id in self._index_data['sessions']:
            del self._index_data['sessions'][session_id]
            # Also delete children sessions
            children_to_delete = [sid for sid in self._index_data['sessions'] if sid.startswith(f"{session_id}/")]
            for child_id in children_to_delete:
                del self._index_data['sessions'][child_id]
            return True
        return False

    def get_sorted_by_last_updated(self) -> list[tuple[str, dict]]:
        """
        Returns a list of (session_id, session_meta) tuples,
        sorted by 'last_updated' in descending order.
        """
        if not self._index_data or 'sessions' not in self._index_data:
            return []
            
        return sorted(
            self._index_data['sessions'].items(),
            key=lambda item: item[1].get('last_updated', ''),
            reverse=True
        )

    def list_all(self) -> Dict[str, Session]:
        """Returns the entire dictionary of sessions."""
        return self._sessions
