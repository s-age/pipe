from __future__ import annotations

import sys
import zoneinfo
from collections.abc import Iterator


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
        index_data: dict,
        timezone_name: str,
    ):
        self._index_data = index_data
        try:
            self.timezone_obj = zoneinfo.ZoneInfo(timezone_name)
        except zoneinfo.ZoneInfoNotFoundError:
            print(
                f"Warning: Timezone '{timezone_name}' not found. Using UTC.",
                file=sys.stderr,
            )
            self.timezone_obj = zoneinfo.ZoneInfo("UTC")

    def __iter__(self) -> Iterator[str]:
        return iter(self._index_data.get("sessions", {}))

    def __len__(self) -> int:
        return len(self._index_data.get("sessions", {}))

    def find(self, session_id: str) -> dict | None:
        """Finds a session's metadata by its ID from the index."""
        return self._index_data.get("sessions", {}).get(session_id)

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
