"""
Repository for managing Session persistence.
"""

import hashlib
import os
import shutil
import sys
import zoneinfo

from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.repositories.file_repository import FileRepository
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import FileLock as file_lock


class SessionRepository(FileRepository):
    """
    Handles the reading and writing of Session objects to and from the filesystem.
    This includes managing the main session file (`${session_id}.json`) and the
    corresponding entry in the `index.json`.
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

    def _initialize_dirs(self):
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)

    def find(self, session_id: str) -> Session | None:
        """Loads a single session from its JSON file.

        Applies data migrations if necessary.
        """
        session_path = self._get_path_for_id(session_id)

        try:
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

    def save(self, session: Session):
        """Saves a session to its file and updates the main index."""
        # Part 1: Save the session object to its own JSON file.
        session_path = self._get_path_for_id(session.session_id)
        lock_path = f"{session_path}.lock"
        self._locked_write_json(
            lock_path, session_path, session.model_dump(mode="json")
        )

        # Part 2: Update the `index.json` with the session's metadata.
        index_data = self._locked_read_json(
            self.index_lock_path, self.index_path, default_data={"sessions": {}}
        )

        if "sessions" not in index_data:
            index_data["sessions"] = {}
        if session.session_id not in index_data["sessions"]:
            index_data["sessions"][session.session_id] = {}

        session_meta = index_data["sessions"][session.session_id]
        session_meta["last_updated"] = get_current_timestamp(self.timezone_obj)
        session_meta["created_at"] = session.created_at
        session_meta["purpose"] = session.purpose

        self._locked_write_json(self.index_lock_path, self.index_path, index_data)

    def get_index(self) -> dict:
        """Reads and returns the raw session index data."""
        return self._locked_read_json(
            self.index_lock_path, self.index_path, default_data={"sessions": {}}
        )

    def delete(self, session_id: str):
        """Deletes a session file and its entry from the index."""
        # Delete session file
        session_path = self._get_path_for_id(session_id)
        lock_path = f"{session_path}.lock"
        with file_lock(lock_path):
            if os.path.exists(session_path):
                try:
                    os.remove(session_path)
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
                self._write_error_log(
                    f"Error deleting empty directory {current_dir}: {e}"
                )
                break  # Stop if we encounter an error or non-empty directory

        # Delete from index
        index_data = self._locked_read_json(
            self.index_lock_path, self.index_path, default_data={"sessions": {}}
        )
        if "sessions" in index_data and session_id in index_data["sessions"]:
            del index_data["sessions"][session_id]
            # Also delete children sessions
            children_to_delete = [
                sid
                for sid in index_data["sessions"]
                if sid.startswith(f"{session_id}/")
            ]
            for child_id in children_to_delete:
                del index_data["sessions"][child_id]

        self._locked_write_json(self.index_lock_path, self.index_path, index_data)

    def backup(self, session: Session):
        """Creates a timestamped backup of the session file."""
        session_path = self._get_path_for_id(session.session_id)
        if not os.path.exists(session_path):
            return

        session_hash = hashlib.sha256(session.session_id.encode("utf-8")).hexdigest()
        timestamp = get_current_timestamp(self.timezone_obj).replace(":", "")
        backup_filename = f"{session_hash}-{timestamp}.json"
        backup_path = os.path.join(self.backups_dir, backup_filename)

        shutil.copy(session_path, backup_path)
