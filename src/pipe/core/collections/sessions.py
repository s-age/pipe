from __future__ import annotations

from collections.abc import Iterator
from datetime import tzinfo

from pipe.core.models.session import Session
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import locked_json_read, locked_json_write


class SessionCollection:
    """
    Manages the collection of session metadata, corresponding to the
    `sessions/index.json` file.
    This class is responsible for loading, saving, and managing the session index.
    It provides methods for finding, adding, and deleting session entries from the
    index, but it does not handle the loading or saving of individual session
    files (e.g., `${session_id}.json`).
    """

    def __init__(
        self,
        index_path: str,
        timezone_obj: tzinfo,
        purpose: str | None = None,
        created_at: str | None = None,
    ):
        self.index_path = index_path
        self.lock_path = f"{index_path}.lock"
        self.timezone_obj = timezone_obj
        self._index_data = locked_json_read(
            self.lock_path, self.index_path, default_data={"sessions": {}}
        )

    def save(self):
        """Saves the current session index to `index.json`."""
        locked_json_write(self.lock_path, self.index_path, self._index_data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._index_data.get("sessions", {}))

    def __len__(self) -> int:
        return len(self._index_data.get("sessions", {}))

    def find(self, session_id: str) -> dict | None:
        """Finds a session's metadata by its ID from the index."""
        return self._index_data.get("sessions", {}).get(session_id)

    def add(self, session: Session):
        """Adds a new session to the collection."""
        if "sessions" not in self._index_data:
            self._index_data["sessions"] = {}
        if session.session_id in self._index_data["sessions"]:
            raise ValueError(f"Session with ID '{session.session_id}' already exists.")

        self.update(session.session_id, session.purpose, session.created_at)

    def update(
        self, session_id: str, purpose: str | None = None, created_at: str | None = None
    ):
        """Updates an existing session's metadata in the index."""
        if "sessions" not in self._index_data:
            self._index_data["sessions"] = {}
        if session_id not in self._index_data["sessions"]:
            self._index_data["sessions"][session_id] = {}

        self._index_data["sessions"][session_id]["last_updated"] = (
            get_current_timestamp(self.timezone_obj)
        )
        if created_at:
            self._index_data["sessions"][session_id]["created_at"] = created_at
        if purpose:
            self._index_data["sessions"][session_id]["purpose"] = purpose

    def delete(self, session_id: str) -> bool:
        """Deletes a session from the collection. Returns True if successful."""
        if (
            "sessions" in self._index_data
            and session_id in self._index_data["sessions"]
        ):
            del self._index_data["sessions"][session_id]
            # Also delete children sessions
            children_to_delete = [
                sid
                for sid in self._index_data["sessions"]
                if sid.startswith(f"{session_id}/")
            ]
            for child_id in children_to_delete:
                del self._index_data["sessions"][child_id]
            return True
        return False

    def get_sorted_by_last_updated(self) -> list[tuple[str, dict]]:
        """
        Returns a list of (session_id, session_meta) tuples,
        sorted by 'last_updated' in descending order.
        """
        if not self._index_data or "sessions" not in self._index_data:
            return []

        return sorted(
            self._index_data["sessions"].items(),
            key=lambda item: item[1].get("last_updated", ""),
            reverse=True,
        )
