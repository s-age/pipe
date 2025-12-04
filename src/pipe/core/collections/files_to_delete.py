"""
Collection for managing session files to be deleted.

Provides type-safe container for batch deletion operations.
"""

from pipe.core.repositories.session_repository import SessionRepository


class FilesToDelete:
    """
    Collection representing session files to be deleted.

    Provides batch deletion operations with error handling.
    """

    def __init__(self, session_ids: list[str], repository: SessionRepository):
        self.session_ids = session_ids
        self.repository = repository

    def execute(self) -> int:
        """
        Execute the deletion of all session files in this collection.

        Returns:
            Number of successfully deleted sessions
        """
        deleted_count = 0
        for session_id in self.session_ids:
            try:
                self.repository.delete(session_id)
                deleted_count += 1
            except Exception:
                # Continue with other deletions even if one fails
                continue
        return deleted_count
