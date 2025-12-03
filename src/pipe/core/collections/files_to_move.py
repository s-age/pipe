"""
Collection for managing session files to be moved to backup.

Provides type-safe container for batch move operations.
"""

import os

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

        Returns:
            Number of successfully moved sessions
        """
        moved_count = 0
        for session_id in self.session_ids:
            try:
                # Get session
                session = self.repository.find(session_id)
                if session:
                    # Create backup
                    self.repository.backup(session)

                    # Delete original file
                    session_path = self.repository._get_path_for_id(session_id)
                    if os.path.exists(session_path):
                        os.remove(session_path)

                    # Remove from index
                    index_data = self.repository._locked_read_json(
                        self.repository.index_lock_path,
                        self.repository.index_path,
                        default_data={"sessions": {}},
                    )
                    if (
                        "sessions" in index_data
                        and session_id in index_data["sessions"]
                    ):
                        del index_data["sessions"][session_id]
                        # Also delete children sessions
                        children_to_delete = [
                            sid
                            for sid in index_data["sessions"]
                            if sid.startswith(f"{session_id}/")
                        ]
                        for child_id in children_to_delete:
                            del index_data["sessions"][child_id]

                    self.repository._locked_write_json(
                        self.repository.index_lock_path,
                        self.repository.index_path,
                        index_data,
                    )

                    moved_count += 1
            except Exception:
                continue
        return moved_count
