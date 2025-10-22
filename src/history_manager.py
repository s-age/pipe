"""
Manages conversation sessions, with each session stored as a single JSON file.
"""
import json
import hashlib
import os
import time
import fnmatch
from contextlib import contextmanager
import fnmatch

from datetime import timezone
import zoneinfo
from typing import Optional

from src.utils.datetime import get_current_timestamp
from src.utils.file import FileLock, locked_json_read_modify_write, locked_json_write, locked_json_read



class HistoryManager:
    """Manages history sessions, encapsulating all file I/O with file locks."""

    def __init__(self, sessions_dir: str, timezone_obj: zoneinfo.ZoneInfo = timezone.utc, default_hyperparameters: dict = None):
        self.sessions_dir = sessions_dir
        self.index_path = os.path.join(sessions_dir, "index.json")
        self.timezone_obj = timezone_obj
        self.default_hyperparameters = default_hyperparameters if default_hyperparameters is not None else {}
        self._index_lock_path = os.path.join(self.sessions_dir, "index.json.lock")
        self._initialize()

    def _get_session_lock_path(self, session_id: str) -> str:
        return os.path.join(self.sessions_dir, f"{session_id}.json.lock")

    def _initialize(self):
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(os.path.join(self.sessions_dir, 'backups'), exist_ok=True)
        # The index file is now created on demand by the _update_index function
        # if it doesn't exist. This just ensures the directories are present.
        if not os.path.exists(self.index_path):
            locked_json_read_modify_write(
                self._index_lock_path,
                self.index_path,
                lambda data: data, # No-op modifier to just create the file
                default_data={"sessions": {}}
            )

    def create_new_session(self, purpose: str, background: str, roles: list, multi_step_reasoning_enabled: bool = False, token_count: int = 0, hyperparameters: dict = None) -> str:
        timestamp = get_current_timestamp(self.timezone_obj)
        identity_str = json.dumps({"purpose": purpose, "background": background, "roles": roles, "multi_step_reasoning_enabled": multi_step_reasoning_enabled, "timestamp": timestamp}, sort_keys=True)
        session_id = self._generate_hash(identity_str)
        
        session_data = {
            "session_id": session_id,
            "created_at": timestamp,
            "purpose": purpose,
            "background": background,
            "roles": roles,
            "multi_step_reasoning_enabled": multi_step_reasoning_enabled,
            "token_count": token_count,
            "hyperparameters": hyperparameters if hyperparameters is not None else self.default_hyperparameters,
            "references": [],
            "turns": [],
            "pools": []
        }

        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        locked_json_write(session_lock_path, session_path, session_data)

        self._update_index(session_id, purpose, timestamp)
        return session_id

    def add_turn_to_session(self, session_id: str, turn_data: dict, token_count: Optional[int] = None):
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            turn_with_meta = turn_data.copy()
            if 'timestamp' not in turn_with_meta:
                turn_with_meta['timestamp'] = get_current_timestamp(self.timezone_obj)
            data.setdefault("turns", []).append(turn_with_meta)
            if token_count is not None:
                data["token_count"] = token_count
        
        locked_json_read_modify_write(session_lock_path, session_path, modifier)
        self._update_index(session_id)

    def update_turns(self, session_id: str, turns: list):
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            data["turns"] = turns
        
        locked_json_read_modify_write(session_lock_path, session_path, modifier)
        self._update_index(session_id)

    def update_references(self, session_id: str, references: list):
        """Updates the references for a given session."""
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            data["references"] = references
        
        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def update_todos(self, session_id: str, todos: list):
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            data["todos"] = todos
        
        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def delete_todos(self, session_id: str):
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            if "todos" in data:
                del data["todos"]

        if not os.path.exists(session_path):
            return
        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def get_session(self, session_id: str) -> dict:
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)
        
        session_data = locked_json_read(session_lock_path, session_path)
        
        if session_data:
            session_data.setdefault('references', [])
            session_data.setdefault('pools', [])
        
        return session_data

    def list_sessions(self) -> dict:
        index_data = locked_json_read(self._index_lock_path, self.index_path, default_data={})
        return index_data.get("sessions", {})

    def delete_turn(self, session_id: str, turn_index: int):
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            if 0 <= turn_index < len(data.get("turns", [])):
                del data["turns"][turn_index]
            else:
                raise IndexError("Turn index out of range.")

        locked_json_read_modify_write(session_lock_path, session_path, modifier)
        self._update_index(session_id)

    def edit_session_meta(self, session_id: str, new_meta_data: dict):
        self.backup_session(session_id)
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            if "purpose" in new_meta_data:
                data["purpose"] = new_meta_data["purpose"]
            if "background" in new_meta_data:
                data["background"] = new_meta_data["background"]
            if "multi_step_reasoning_enabled" in new_meta_data:
                data["multi_step_reasoning_enabled"] = new_meta_data["multi_step_reasoning_enabled"]
            if "token_count" in new_meta_data:
                data["token_count"] = new_meta_data["token_count"]
            if "hyperparameters" in new_meta_data:
                data["hyperparameters"] = new_meta_data["hyperparameters"]

        locked_json_read_modify_write(session_lock_path, session_path, modifier)
        
        # Call _update_index, passing purpose if it exists
        purpose_to_update = new_meta_data.get("purpose")
        self._update_index(session_id, purpose=purpose_to_update)

    def get_session_turns(self, session_id: str) -> list[dict]:
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)
        session_data = locked_json_read(session_lock_path, session_path, default_data={})
        return session_data.get("turns", [])

    def get_session_turns_range(self, session_id: str, start_index: int, end_index: int) -> list[dict]:
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)
        
        session_data = locked_json_read(session_lock_path, session_path)
        if not session_data:
            raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            
        turns = session_data.get("turns", [])
        if not (0 <= start_index < len(turns) and 0 <= end_index < len(turns) and start_index <= end_index):
            raise IndexError("Turn indices are out of range.")
        return turns[start_index:end_index + 1]

    def replace_turn_range_with_summary(self, session_id: str, summary_text: str, start_index: int, end_index: int):
        self.backup_session(session_id)
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)
        
        summary_turn = {
            "type": "compressed_history",
            "content": summary_text,
            "timestamp": get_current_timestamp(self.timezone_obj)
        }

        def modifier(data):
            turns = data.get("turns", [])
            
            if not (0 <= start_index < len(turns) and 0 <= end_index < len(turns) and start_index <= end_index):
                raise IndexError("Turn indices are out of range for replacement.")

            # Replace the specified range with the single summary turn
            del turns[start_index:end_index + 1]
            turns.insert(start_index, summary_turn)
            
            data["turns"] = turns

        locked_json_read_modify_write(session_lock_path, session_path, modifier)
        self._update_index(session_id)

    def edit_turn(self, session_id: str, turn_index: int, new_turn_data: dict):
        self.backup_session(session_id)
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            if 0 <= turn_index < len(data.get("turns", [])):
                original_turn = data["turns"][turn_index]
                original_turn.update(new_turn_data)
            else:
                raise IndexError("Turn index out of range.")

        locked_json_read_modify_write(session_lock_path, session_path, modifier)
        self._update_index(session_id)

    def add_to_pool(self, session_id: str, pool_data: dict):
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            data.setdefault("pools", []).append(pool_data)

        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def get_pool(self, session_id: str) -> list:
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)
        
        session_data = locked_json_read(session_lock_path, session_path)
        
        if session_data:
            return session_data.get('pools', [])
        
        return []

    def get_and_clear_pool(self, session_id: str) -> list:
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            pools = data.get("pools", [])
            if pools:
                data["pools"] = []
            return data, pools # Return tuple: (modified_data, value_to_return)

        pools_to_return = locked_json_read_modify_write(session_lock_path, session_path, modifier)
        return pools_to_return if pools_to_return is not None else []

    def backup_session(self, session_id: str) -> str:
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if not os.path.exists(session_path):
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            timestamp = get_current_timestamp(timezone.utc, fmt='%Y%m%d%H%M%S')
            backup_path = os.path.join(self.sessions_dir, "backups", f"{session_id}-{timestamp}.json")
            import shutil
            shutil.copy2(session_path, backup_path)
            return backup_path

    def replace_turns_with_summary(self, session_id: str, summary_text: str):
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)
        
        summary_turn = {
            "type": "condensed_history",
            "content": summary_text,
            "timestamp": get_current_timestamp(self.timezone_obj)
        }

        def modifier(data):
            data["turns"] = [summary_turn]

        locked_json_read_modify_write(session_lock_path, session_path, modifier)
        self._update_index(session_id)

    def delete_session(self, session_id: str):
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if os.path.exists(session_path):
                os.remove(session_path)

        backup_dir = os.path.join(self.sessions_dir, "backups")
        for filename in os.listdir(backup_dir):
            if fnmatch.fnmatch(filename, f"{session_id}-*.json"):
                os.remove(os.path.join(backup_dir, filename))

        def modifier(data):
            if session_id in data.get("sessions", {}):
                del data["sessions"][session_id]
        
        locked_json_read_modify_write(
            self._index_lock_path,
            self.index_path,
            modifier,
            default_data={"sessions": {}}
        )

    def _update_index(self, session_id: str, purpose: str = None, created_at: str = None):
        def modifier(data):
            if session_id not in data["sessions"]:
                data["sessions"][session_id] = {}
            data["sessions"][session_id]['last_updated'] = get_current_timestamp(self.timezone_obj)
            if created_at:
                data["sessions"][session_id]['created_at'] = created_at
            if purpose:
                data["sessions"][session_id]['purpose'] = purpose
        
        locked_json_read_modify_write(
            self._index_lock_path,
            self.index_path,
            modifier,
            default_data={"sessions": {}}
        )

    def _generate_hash(self, content: str) -> str:
        """Generates a SHA-256 hash for the given content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def fork_session(self, original_session_id: str, fork_at_turn_index: int) -> Optional[str]:
        original_session_path = os.path.join(self.sessions_dir, f"{original_session_id}.json")
        original_session_lock_path = self._get_session_lock_path(original_session_id)

        original_data = locked_json_read(original_session_lock_path, original_session_path)
        if not original_data:
            raise FileNotFoundError(f"Original session file for ID '{original_session_id}' not found.")

        # Create a new session based on the original data
        forked_purpose = f"Fork of: {original_data.get('purpose', 'Untitled')}"
        timestamp = get_current_timestamp(self.timezone_obj)
        
        # Ensure fork_at_turn_index is valid and is a model_response
        original_turns = original_data.get('turns', [])
        if not (0 <= fork_at_turn_index < len(original_turns)):
            raise IndexError("fork_at_turn_index is out of range.")
        
        fork_turn = original_turns[fork_at_turn_index]
        if fork_turn.get("type") != "model_response":
            raise ValueError(f"Forking is only allowed from a 'model_response' turn. Turn {fork_at_turn_index + 1} is of type '{fork_turn.get('type')}''.")

        # Slice the history
        forked_turns = original_turns[:fork_at_turn_index + 1]

        # Generate a new unique ID for the forked session
        identity_str = json.dumps({
            "purpose": forked_purpose, 
            "original_id": original_session_id,
            "fork_at_turn": fork_at_turn_index,
            "timestamp": timestamp
        }, sort_keys=True)
        new_session_id = self._generate_hash(identity_str)

        new_session_data = {
            "session_id": new_session_id,
            "created_at": timestamp,
            "purpose": forked_purpose,
            "background": original_data.get('background', ''),
            "roles": original_data.get('roles', []),
            "multi_step_reasoning_enabled": original_data.get('multi_step_reasoning_enabled', False),
            "token_count": 0, # Reset token count
            "references": original_data.get('references', []),
            "turns": forked_turns
        }

        new_session_path = os.path.join(self.sessions_dir, f"{new_session_id}.json")
        new_session_lock_path = self._get_session_lock_path(new_session_id)

        locked_json_write(new_session_lock_path, new_session_path, new_session_data)

        self._update_index(new_session_id, forked_purpose, timestamp)
        return new_session_id