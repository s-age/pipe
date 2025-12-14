"""
Collection for managing session files to be moved to backup.

Provides type-safe container for batch move operations.
"""

from pipe.core.repositories.session_repository import SessionRepository


class FilesToMove:
    """
    Collection representing session files to be moved to backup.

    Provides batch move operations with index updates.
    """

    def __init__(self, session_ids: list[str], repository: SessionRepository):
        self.session_ids = session_ids
        self.repository = repository

    def execute(self) -> int:
        """
        Execute the move of all session files in this collection to backup.

        Uses the repository's public move_to_backup() method to ensure
        proper encapsulation and atomic operations.

        Returns:
            Number of successfully moved sessions
        """
        moved_count = 0
        for session_id in self.session_ids:
            if self.repository.move_to_backup(session_id):
                moved_count += 1
        return moved_count
