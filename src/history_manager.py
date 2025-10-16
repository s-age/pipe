"""
Manages conversation sessions, with each session stored as a single JSON file.
"""
import json
import hashlib
import os
import time
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
import zoneinfo
from typing import Optional

@contextmanager
def FileLock(lock_file_path: Path):
    """A simple file-based lock context manager for process-safe file operations."""
    retry_interval = 0.1
    timeout = 10.0
    start_time = time.monotonic()

    while True:
        try:
            fd = os.open(lock_file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() - start_time >= timeout:
                raise TimeoutError(f"Could not acquire lock on {lock_file_path} within {timeout} seconds.")
            time.sleep(retry_interval)
    
    try:
        yield
    finally:
        try:
            os.remove(lock_file_path)
        except OSError:
            pass

class HistoryManager:
    """Manages history sessions, encapsulating all file I/O with file locks."""

    def __init__(self, sessions_dir: Path, timezone_obj: zoneinfo.ZoneInfo = timezone.utc):
        self.sessions_dir = sessions_dir
        self.index_path = sessions_dir / "index.json"
        self.timezone_obj = timezone_obj
        self._index_lock_path = self.sessions_dir / "index.json.lock"
        self._initialize()

    def _get_session_lock_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json.lock"

    def _initialize(self):
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        (self.sessions_dir / 'backups').mkdir(exist_ok=True)
        with FileLock(self._index_lock_path):
            if not self.index_path.exists():
                with self.index_path.open("w", encoding="utf-8") as f:
                    json.dump({"sessions": {}}, f, indent=2, ensure_ascii=False)

    def create_new_session(self, purpose: str, background: str, roles: list, multi_step_reasoning_enabled: bool = False, token_count: int = 0) -> str:
        timestamp = datetime.now(self.timezone_obj).isoformat()
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
            "references": [],
            "turns": []
        }

        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)

        with FileLock(session_lock_path):
            with session_path.open("w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

        self._update_index(session_id, purpose, timestamp)
        return session_id

    def add_turn_to_session(self, session_id: str, turn_data: dict, token_count: Optional[int] = None):
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)

        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                turn_with_meta = turn_data.copy()
                turn_with_meta['timestamp'] = datetime.now(self.timezone_obj).isoformat()
                session_data["turns"].append(turn_with_meta)
                if token_count is not None:
                    session_data["token_count"] = token_count
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()
        
        self._update_index(session_id)

    def update_turns(self, session_id: str, turns: list):
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)

        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{{session_id}}' not found.")
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                session_data["turns"] = turns
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()
        
        self._update_index(session_id)

    def update_references(self, session_id: str, references: list):
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)

        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                session_data["references"] = references
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()
        
        self._update_index(session_id)

    def update_todos(self, session_id: str, todos: list):
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)

        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                session_data["todos"] = todos
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()

    def delete_todos(self, session_id: str):
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)

        with FileLock(session_lock_path):
            if not session_path.exists():
                return
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                if "todos" in session_data:
                    del session_data["todos"]
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()

    def get_session(self, session_id: str) -> dict:
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if not session_path.exists():
                return None
            with session_path.open("r", encoding="utf-8") as f:
                session_data = json.load(f)
                session_data.setdefault('references', [])
                return session_data

    def list_sessions(self) -> dict:
        with FileLock(self._index_lock_path):
            if not self.index_path.exists():
                return {}
            with self.index_path.open("r", encoding="utf-8") as f:
                return json.load(f).get("sessions", {})

    def delete_turn(self, session_id: str, turn_index: int):
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                if 0 <= turn_index < len(session_data["turns"]):
                    del session_data["turns"][turn_index]
                else:
                    raise IndexError("Turn index out of range.")
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()
        self._update_index(session_id)

    def edit_session_meta(self, session_id: str, new_meta_data: dict):
        self.backup_session(session_id)
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                if "purpose" in new_meta_data:
                    session_data["purpose"] = new_meta_data["purpose"]
                if "background" in new_meta_data:
                    session_data["background"] = new_meta_data["background"]
                if "multi_step_reasoning_enabled" in new_meta_data:
                    session_data["multi_step_reasoning_enabled"] = new_meta_data["multi_step_reasoning_enabled"]
                if "token_count" in new_meta_data:
                    session_data["token_count"] = new_meta_data["token_count"]
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()
        
        if "purpose" in new_meta_data:
            self._update_index(session_id, purpose=new_meta_data["purpose"])
        else:
            self._update_index(session_id)

    def get_session_turns(self, session_id: str) -> list[dict]:
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if not session_path.exists():
                return []
            with session_path.open("r", encoding="utf-8") as f:
                return json.load(f).get("turns", [])

    def get_session_turns_range(self, session_id: str, start_index: int, end_index: int) -> list[dict]:
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            with session_path.open("r", encoding="utf-8") as f:
                session_data = json.load(f)
                turns = session_data.get("turns", [])
                if not (0 <= start_index < len(turns) and 0 <= end_index < len(turns) and start_index <= end_index):
                    raise IndexError("Turn indices are out of range.")
                return turns[start_index:end_index + 1]

    def replace_turn_range_with_summary(self, session_id: str, summary_text: str, start_index: int, end_index: int):
        self.backup_session(session_id)
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            
            summary_turn = {
                "type": "compressed_history",
                "content": summary_text,
                "timestamp": datetime.now(self.timezone_obj).isoformat()
            }

            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                turns = session_data.get("turns", [])
                
                if not (0 <= start_index < len(turns) and 0 <= end_index < len(turns) and start_index <= end_index):
                    raise IndexError("Turn indices are out of range for replacement.")

                # Replace the specified range with the single summary turn
                del turns[start_index:end_index + 1]
                turns.insert(start_index, summary_turn)
                
                session_data["turns"] = turns
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()
        self._update_index(session_id)

    def edit_turn(self, session_id: str, turn_index: int, new_turn_data: dict):
        self.backup_session(session_id)
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                if 0 <= turn_index < len(session_data["turns"]):
                    original_turn = session_data["turns"][turn_index]
                    original_turn.update(new_turn_data)
                else:
                    raise IndexError("Turn index out of range.")
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()
        self._update_index(session_id)

    def backup_session(self, session_id: str) -> Path:
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
            backup_path = self.sessions_dir / "backups" / f"{session_id}-{timestamp}.json"
            import shutil
            shutil.copy2(session_path, backup_path)
            return backup_path

    def replace_turns_with_summary(self, session_id: str, summary_text: str):
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if not session_path.exists():
                raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            summary_turn = {
                "type": "condensed_history",
                "content": summary_text,
                "timestamp": datetime.now(self.timezone_obj).isoformat()
            }
            with session_path.open("r+", encoding="utf-8") as f:
                session_data = json.load(f)
                session_data["turns"] = [summary_turn]
                f.seek(0)
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                f.truncate()
        self._update_index(session_id)

    def delete_session(self, session_id: str):
        session_path = self.sessions_dir / f"{session_id}.json"
        session_lock_path = self._get_session_lock_path(session_id)
        with FileLock(session_lock_path):
            if session_path.exists():
                session_path.unlink()

        backup_dir = self.sessions_dir / "backups"
        for backup_file in backup_dir.glob(f"{session_id}-*.json"):
            # No need to lock individual backup files for deletion
            backup_file.unlink()

        with FileLock(self._index_lock_path):
            with self.index_path.open("r+", encoding="utf-8") as f:
                index_data = json.load(f)
                if session_id in index_data["sessions"]:
                    del index_data["sessions"][session_id]
                f.seek(0)
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                f.truncate()

    def _update_index(self, session_id: str, purpose: str = None, created_at: str = None):
        with FileLock(self._index_lock_path):
            with self.index_path.open("r+", encoding="utf-8") as f:
                index_data = json.load(f)
                if session_id not in index_data["sessions"]:
                    index_data["sessions"][session_id] = {}
                index_data["sessions"][session_id]['last_updated'] = datetime.now(self.timezone_obj).isoformat()
                if purpose and created_at:
                    index_data["sessions"][session_id]['created_at'] = created_at
                    index_data["sessions"][session_id]['purpose'] = purpose
                f.seek(0)
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                f.truncate()

    def _generate_hash(self, content: str) -> str:
        """Generates a SHA-256 hash for the given content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def fork_session(self, original_session_id: str, fork_at_turn_index: int) -> Optional[str]:
        original_session_path = self.sessions_dir / f"{original_session_id}.json"
        original_session_lock_path = self._get_session_lock_path(original_session_id)

        with FileLock(original_session_lock_path):
            if not original_session_path.exists():
                raise FileNotFoundError(f"Original session file for ID '{{original_session_id}}' not found.")
            with original_session_path.open("r", encoding="utf-8") as f:
                original_data = json.load(f)

        # Create a new session based on the original data
        forked_purpose = f"Fork of: {original_data.get('purpose', 'Untitled')}"
        timestamp = datetime.now(self.timezone_obj).isoformat()
        
        # Ensure fork_at_turn_index is valid and is a model_response
        original_turns = original_data.get('turns', [])
        if not (0 <= fork_at_turn_index < len(original_turns)):
            raise IndexError("fork_at_turn_index is out of range.")
        
        fork_turn = original_turns[fork_at_turn_index]
        if fork_turn.get("type") != "model_response":
            raise ValueError(f"Forking is only allowed from a 'model_response' turn. Turn {fork_at_turn_index + 1} is of type '{fork_turn.get('type')}'.")

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

        new_session_path = self.sessions_dir / f"{new_session_id}.json"
        new_session_lock_path = self._get_session_lock_path(new_session_id)

        with FileLock(new_session_lock_path):
            with new_session_path.open("w", encoding="utf-8") as f:
                json.dump(new_session_data, f, indent=2, ensure_ascii=False)

        self._update_index(new_session_id, forked_purpose, timestamp)
        return new_session_id
