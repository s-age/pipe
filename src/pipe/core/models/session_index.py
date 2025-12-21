"""
Pydantic models for session index management.

The SessionIndex corresponds to the `sessions/index.json` file,
which maintains metadata for all active sessions without storing
the full session state.
"""

from pipe.core.models.base import CamelCaseModel
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

# Type alias for sorted sessions
SessionSortedEntry = tuple[str, "SessionIndexEntry"]


class SessionIndexEntry(CamelCaseModel):
    """
    Represents metadata for a single session in the index.

    Each session has:
    - created_at: When the session was created (serialized as createdAt)
    - last_updated_at: When the session was last modified (serialized as lastUpdatedAt)
    - purpose: Brief description of the session's purpose
    """

    created_at: str
    last_updated_at: str
    purpose: str | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,  # Convert snake_case to camelCase
        populate_by_name=True,  # Accept both forms
        extra="forbid",  # Strict validation - no extra fields
    )


class SessionIndex(CamelCaseModel):
    """
    Represents the complete session index (index.json).

    Contains a mapping of session IDs to their metadata entries.
    This model ensures type-safe access to the index structure,
    replacing raw dict[str, dict] usage.
    """

    sessions: dict[str, SessionIndexEntry] = Field(default_factory=dict)
    version: str = Field(
        default="1.0", description="Schema version for future migrations"
    )

    model_config = ConfigDict(
        alias_generator=to_camel,  # Convert snake_case to camelCase
        populate_by_name=True,  # Accept both forms
        extra="forbid",  # Strict validation - no extra fields
    )

    def add_session(self, session_id: str, entry: SessionIndexEntry) -> None:
        """Adds or updates a session entry in the index."""
        self.sessions[session_id] = entry

    def remove_session(self, session_id: str) -> bool:
        """Removes a session from the index. Returns True if successful."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def get_session(self, session_id: str) -> SessionIndexEntry | None:
        """Retrieves a session entry by ID."""
        return self.sessions.get(session_id)

    def contains_session(self, session_id: str) -> bool:
        """Checks if a session ID exists in the index."""
        return session_id in self.sessions

    def get_all_session_ids(self) -> list[str]:
        """Returns a list of all session IDs in the index."""
        return list(self.sessions.keys())

    def get_sessions_sorted_by_last_updated(self) -> list[SessionSortedEntry]:
        """
        Returns sessions sorted by last_updated_at in descending order.
        Most recently updated sessions appear first.
        """
        return sorted(
            self.sessions.items(),
            key=lambda item: item[1].last_updated_at,
            reverse=True,
        )

    def get_child_sessions(self, parent_id: str) -> list[str]:
        """
        Returns all session IDs that are children of the given parent session.
        Child sessions have IDs in the format: {parent_id}/{child_id}
        """
        prefix = f"{parent_id}/"
        return [sid for sid in self.sessions.keys() if sid.startswith(prefix)]

    def remove_session_tree(self, session_id: str) -> int:
        """
        Removes a session and all its children from the index.
        Returns the number of sessions removed.
        """
        removed_count = 0

        # Remove the session itself
        if self.remove_session(session_id):
            removed_count += 1

        # Remove all children
        children = self.get_child_sessions(session_id)
        for child_id in children:
            if self.remove_session(child_id):
                removed_count += 1

        return removed_count
