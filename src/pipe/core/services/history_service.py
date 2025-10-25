"""
Manages the conversation_history of a session.
"""
import json
import os
import zoneinfo
from typing import Optional

from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import locked_json_read_modify_write, locked_json_read

class HistoryService:
    """Manages history sessions, encapsulating all file I/O with file locks."""

    def __init__(self, sessions_dir: str, timezone_obj: zoneinfo.ZoneInfo):
        self.sessions_dir = sessions_dir
        self.timezone_obj = timezone_obj

    def _get_session_path(self, session_id: str) -> str:
        """Constructs the file path for a session."""
        safe_path_parts = [part for part in session_id.split('/') if part not in ('', '.', '..')]
        final_path = os.path.join(self.sessions_dir, *safe_path_parts)
        return f"{final_path}.json"

    def _get_session_lock_path(self, session_id: str) -> str:
        return f"{self._get_session_path(session_id)}.lock"

    def add_turn_to_session(self, session_id: str, turn_data: dict):
        session_path = self._get_session_path(session_id)
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            turn_with_meta = turn_data.copy()
            if 'timestamp' not in turn_with_meta:
                turn_with_meta['timestamp'] = get_current_timestamp(self.timezone_obj)
            data.setdefault("turns", []).append(turn_with_meta)
        
        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def update_turns(self, session_id: str, turns: list):
        session_path = self._get_session_path(session_id)
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            data["turns"] = turns
        
        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def delete_turn(self, session_id: str, turn_index: int):
        session_path = self._get_session_path(session_id)
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            if 0 <= turn_index < len(data.get("turns", [])):
                del data["turns"][turn_index]
            else:
                raise IndexError("Turn index out of range.")

        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def get_session_turns(self, session_id: str) -> list[dict]:
        session_path = self._get_session_path(session_id)
        session_lock_path = self._get_session_lock_path(session_id)
        session_data = locked_json_read(session_lock_path, session_path, default_data={})
        return session_data.get("turns", [])

    def get_session_turns_range(self, session_id: str, start_index: int, end_index: int) -> list[dict]:
        session_path = self._get_session_path(session_id)
        session_lock_path = self._get_session_lock_path(session_id)
        
        session_data = locked_json_read(session_lock_path, session_path)
        if not session_data:
            raise FileNotFoundError(f"Session file for ID '{session_id}' not found.")
            
        turns = session_data.get("turns", [])
        if not (0 <= start_index < len(turns) and 0 <= end_index < len(turns) and start_index <= end_index):
            raise IndexError("Turn indices are out of range.")
        return turns[start_index:end_index + 1]

    def replace_turn_range_with_summary(self, session_id: str, summary_text: str, start_index: int, end_index: int):
        session_path = self._get_session_path(session_id)
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

            del turns[start_index:end_index + 1]
            turns.insert(start_index, summary_turn)
            
            data["turns"] = turns

        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def edit_turn(self, session_id: str, turn_index: int, new_turn_data: dict):
        session_path = self._get_session_path(session_id)
        session_lock_path = self._get_session_lock_path(session_id)

        def modifier(data):
            if 0 <= turn_index < len(data.get("turns", [])):
                original_turn = data["turns"][turn_index]
                original_turn.update(new_turn_data)
            else:
                raise IndexError("Turn index out of range.")

        locked_json_read_modify_write(session_lock_path, session_path, modifier)

    def replace_turns_with_summary(self, session_id: str, summary_text: str):
        session_path = self._get_session_path(session_id)
        session_lock_path = self._get_session_lock_path(session_id)
        
        summary_turn = {
            "type": "condensed_history",
            "content": summary_text,
            "timestamp": get_current_timestamp(self.timezone_obj)
        }

        def modifier(data):
            data["turns"] = [summary_turn]

        locked_json_read_modify_write(session_lock_path, session_path, modifier)
