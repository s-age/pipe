"""
Repository for managing Session persistence.

Implements Pydantic I/O design with type-safe validation and Atomic Update pattern
for maintaining consistency between session files and the index.
"""

import hashlib
import os
import shutil
import sys
import zoneinfo
from collections.abc import Callable

from pipe.core.models.session import Session
from pipe.core.models.session_index import SessionIndex, SessionIndexEntry
from pipe.core.models.settings import Settings
from pipe.core.repositories.file_repository import FileRepository, file_lock
from pipe.core.utils.datetime import get_current_timestamp


class SessionRepository(FileRepository):
    """
    Handles the reading and writing of Session objects to and from the filesystem.

    This repository maintains:
    - Individual session files (`${session_id}.json`) - validated with Session model
    - Session index file (`index.json`) - validated with SessionIndex model

    Uses Pydantic I/O pattern:
    - Load: JSON -> dict -> model_validate() -> typed model instance
    - Save: model instance -> model_dump(mode='json') -> JSON

    Implements Atomic Update pattern for consistency:
    - Lock -> Read -> Validate -> Modify -> Serialize -> Write -> Unlock
    """

    def __init__(self, project_root: str, settings: Settings):
        super().__init__()
        self.project_root = project_root
        self.settings = settings

        tz_name = settings.timezone
        try:
            self.timezone_obj = zoneinfo.ZoneInfo(tz_name)
        except zoneinfo.ZoneInfoNotFoundError:
            print(
                f"Warning: Timezone '{tz_name}' not found. Using UTC.", file=sys.stderr
            )
            self.timezone_obj = zoneinfo.ZoneInfo("UTC")

        self.sessions_dir = os.path.join(project_root, settings.sessions_path)
        self.backups_dir = os.path.join(self.sessions_dir, "backups")
        self.index_path = os.path.join(self.sessions_dir, "index.json")
        self.index_lock_path = f"{self.index_path}.lock"

        self._initialize_dirs()

    def _initialize_dirs(self) -> None:
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)

    def find(self, session_id: str) -> Session | None:
        """Loads a single session from its JSON file.

        Applies data migrations if necessary.
        """
        session_path = self._get_path_for_id(session_id)
        lock_path = f"{session_path}.lock"

        try:
            with file_lock(lock_path):
                data = self._read_json(session_path)
            if data is None:
                return None
        except (FileNotFoundError, ValueError):
            return None

        # --- Data Migration ---
        session_creation_time = data.get(
            "created_at", get_current_timestamp(self.timezone_obj)
        )
        for turn_list_key in ["turns", "pools"]:
            if turn_list_key in data and isinstance(data[turn_list_key], list):
                for turn_data in data[turn_list_key]:
                    if not isinstance(turn_data, dict):
                        continue
                    if "timestamp" not in turn_data:
                        turn_data["timestamp"] = session_creation_time
                    if (
                        turn_data.get("type") == "compressed_history"
                        and "original_turns_range" not in turn_data
                    ):
                        turn_data["original_turns_range"] = [0, 0]
        # --- End of Data Migration ---

        instance = Session.model_validate(data)
        return instance

    def _get_path_for_id(self, session_id: str) -> str:
        """A utility to get a session path from a session ID."""
        safe_path_parts = [
            part for part in session_id.split("/") if part not in ("", ".", "..")
        ]
        final_path = os.path.join(self.sessions_dir, *safe_path_parts)
        return f"{final_path}.json"

    def save(self, session: Session) -> None:
        """
        Saves a session to its file and updates the main index.

        Uses Atomic Update pattern:
        1. Acquire index lock
        2. Save session file
        3. Load index with Pydantic validation
        4. Update session metadata
        5. Validate and serialize index
        6. Write index file
        7. Release lock
        """
        session_path = self._get_path_for_id(session.session_id)
        lock_path = f"{session_path}.lock"

        # Acquire locks in a consistent order: always index lock first,
        # then session lock
        # This prevents deadlocks when multiple processes access different sessions
        with file_lock(self.index_lock_path):
            # Part 1: Save the session object to its own JSON file (Pydantic I/O)
            with file_lock(lock_path):
                session_json = session.model_dump(mode="json")
                self._write_json(session_path, session_json)

            # Part 2: Update the `index.json` with session metadata (Atomic Update)
            # Load index with validation
            index_data = self._read_json(self.index_path, default_data={"sessions": {}})

            # Convert to SessionIndex model for type-safe manipulation
            sessions = {}
            for sid, entry_data in index_data.get("sessions", {}).items():
                if isinstance(entry_data, SessionIndexEntry):
                    sessions[sid] = entry_data
                else:
                    # Migrate old format: last_updated -> last_updated_at
                    if isinstance(entry_data, dict):
                        if "last_updated" in entry_data:
                            if "last_updated_at" not in entry_data:
                                value = entry_data.pop("last_updated")
                                entry_data["last_updated_at"] = value
                            else:
                                entry_data.pop("last_updated", None)
                    sessions[sid] = SessionIndexEntry.model_validate(entry_data)

            index = SessionIndex(sessions=sessions)

            # Modify session metadata
            entry = SessionIndexEntry(
                created_at=session.created_at,
                last_updated_at=get_current_timestamp(self.timezone_obj),
                purpose=session.purpose,
            )
            index.add_session(session.session_id, entry)

            # Serialize and write index
            index_json = index.model_dump(mode="json")
            self._write_json(self.index_path, index_json)

    def load_index(self) -> SessionIndex:
        """
        Loads and validates the session index using Pydantic model.

        Returns:
            SessionIndex: The validated session index model

        Raises:
            ValueError: If the index data is invalid
        """
        with file_lock(self.index_lock_path):
            index_data = self._read_json(self.index_path, default_data={"sessions": {}})
        # Convert dict entries to SessionIndexEntry objects
        sessions = {}
        for session_id, entry_data in index_data.get("sessions", {}).items():
            # Ensure entry_data is a dict before validating
            if isinstance(entry_data, SessionIndexEntry):
                sessions[session_id] = entry_data
            else:
                # Migrate old format: last_updated -> last_updated_at
                if isinstance(entry_data, dict):
                    if "last_updated" in entry_data:
                        if "last_updated_at" not in entry_data:
                            value = entry_data.pop("last_updated")
                            entry_data["last_updated_at"] = value
                        else:
                            entry_data.pop("last_updated", None)
                sessions[session_id] = SessionIndexEntry.model_validate(entry_data)

        return SessionIndex(sessions=sessions)

    def get_index(self) -> dict[str, dict[str, str]]:
        """Reads and returns the raw session index data (deprecated).

        Use load_index() instead for type-safe access.
        """
        return self._locked_read_json(
            self.index_lock_path, self.index_path, default_data={"sessions": {}}
        )

    def delete(self, session_id: str) -> bool:
        """
        Deletes a session file and its entry from the index.

        Uses Atomic Update pattern to maintain consistency between
        session files and index.

        Returns:
            True if a session was found and deleted, False otherwise
        """
        session_path = self._get_path_for_id(session_id)
        session_deleted = False

        # Delete session file if it exists
        if os.path.exists(session_path):
            lock_path = f"{session_path}.lock"
            with file_lock(lock_path):
                try:
                    os.remove(session_path)
                    session_deleted = True
                except OSError as e:
                    print(
                        f"Error deleting session file {session_path}: {e}",
                        file=sys.stderr,
                    )
                    raise

            # Attempt to remove empty parent directories
            current_dir = os.path.dirname(session_path)
            while current_dir != self.sessions_dir and not os.listdir(current_dir):
                try:
                    os.rmdir(current_dir)
                    current_dir = os.path.dirname(current_dir)
                except OSError as e:
                    print(
                        f"Error deleting empty directory {current_dir}: {e}",
                        file=sys.stderr,
                    )
                    break  # Stop if we encounter an error or non-empty directory

        # Delete from index with Atomic Update pattern
        with file_lock(self.index_lock_path):
            index_data = self._read_json(self.index_path, default_data={"sessions": {}})

            if "sessions" in index_data and session_id in index_data["sessions"]:
                # Load and validate index
                sessions = {}
                for sid, entry_data in index_data.get("sessions", {}).items():
                    if isinstance(entry_data, SessionIndexEntry):
                        sessions[sid] = entry_data
                    else:
                        # Migrate old format: last_updated -> last_updated_at
                        if isinstance(entry_data, dict):
                            if "last_updated" in entry_data:
                                if "last_updated_at" not in entry_data:
                                    value = entry_data.pop("last_updated")
                                    entry_data["last_updated_at"] = value
                                else:
                                    entry_data.pop("last_updated", None)
                        sessions[sid] = SessionIndexEntry.model_validate(entry_data)

                index = SessionIndex(sessions=sessions)

                # Delete using type-safe method
                removed_count = index.remove_session_tree(session_id)

                # Serialize and write index
                index_json = index.model_dump(mode="json")
                self._write_json(self.index_path, index_json)

                # Consider it deleted if it was in the index and removed
                return removed_count > 0

        # Return true if file existed and deleted
        return session_deleted

    def backup(self, session: Session) -> None:
        """Creates a timestamped backup of the session file."""
        session_path = self._get_path_for_id(session.session_id)
        if not os.path.exists(session_path):
            return

        session_hash = hashlib.sha256(session.session_id.encode("utf-8")).hexdigest()
        timestamp = get_current_timestamp(self.timezone_obj).replace(":", "")
        backup_filename = f"{session_hash}-{timestamp}.json"
        backup_path = os.path.join(self.backups_dir, backup_filename)

        shutil.copy(session_path, backup_path)

    def move_to_backup(self, session_id: str) -> bool:
        """
        Moves a session to backup and removes it from the active sessions.

        This operation:
        1. Creates a backup of the session
        2. Deletes the original session file
        3. Removes the session from the index

        Args:
            session_id: ID of the session to move to backup

        Returns:
            True if the session was successfully moved, False otherwise
        """
        try:
            # Load session
            session = self.find(session_id)
            if not session:
                return False

            # Create backup
            self.backup(session)

            # Delete original (which also removes from index)
            return self.delete(session_id)

        except Exception:
            return False

    def delete_backup(self, session_id: str) -> None:
        """Deletes a backup session file."""
        # Find the backup file for the session_id
        backups_dir = self.backups_dir
        if not os.path.exists(backups_dir):
            return

        session_hash = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
        for filename in os.listdir(backups_dir):
            if filename.startswith(session_hash) and filename.endswith(".json"):
                backup_path = os.path.join(backups_dir, filename)
                lock_path = f"{backup_path}.lock"
                with file_lock(lock_path):
                    if os.path.exists(backup_path):
                        try:
                            os.remove(backup_path)
                        except OSError as e:
                            print(
                                f"Error deleting backup file {backup_path}: {e}",
                                file=sys.stderr,
                            )
                            raise
                break

    def _atomic_update(
        self, session_id: str, update_fn: Callable[[Session], None]
    ) -> Session:
        """
        Performs atomic partial update of a session.

        This method implements the Atomic Update pattern:
        1. Lock session file
        2. Read and validate session
        3. Apply modifications via callback
        4. Serialize and write back
        5. Update index metadata

        Args:
            session_id: ID of the session to update
            update_fn: Callback function that modifies the session in-place
                      Signature: (Session) -> None

        Returns:
            The updated Session instance

        Raises:
            FileNotFoundError: If the session does not exist
            TimeoutError: If lock acquisition times out

        Example:
            def update_refs(session: Session):
                session.references.clear()
                session.references.append(new_ref)

            updated = repo._atomic_update("session-123", update_refs)
        """
        session_path = self._get_path_for_id(session_id)
        lock_path = f"{session_path}.lock"

        with file_lock(lock_path):
            # 1. Read
            data = self._read_json(session_path)
            if data is None:
                raise FileNotFoundError(f"Session {session_id} not found")

            # 2. Validate
            session = Session.model_validate(data)

            # 3. Modify
            update_fn(session)

            # 4. Serialize & Save
            self._write_json(session_path, session.model_dump(mode="json"))

        # 5. Update index metadata (outside session lock)
        self._update_index_metadata(session_id)

        return session

    def _update_index_metadata(self, session_id: str) -> None:
        """
        Updates the last_updated_at timestamp in index.json.

        This method is called after a session file has been modified.
        It only updates the timestamp, not other metadata fields.

        Note:
            This method assumes the session file lock has already been released.
            It acquires only the index lock.

        Args:
            session_id: ID of the session whose metadata should be updated
        """
        with file_lock(self.index_lock_path):
            index = self.load_index()

            if session_id in index.sessions:
                index.sessions[session_id].last_updated_at = get_current_timestamp(
                    self.timezone_obj
                )

                self._write_json(self.index_path, index.model_dump(mode="json"))
