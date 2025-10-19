import json

from datetime import datetime, timezone
import zoneinfo
from typing import Optional
import os
import sys

from src.history_manager import HistoryManager

class SessionManager:
    def __init__(self, sessions_dir: str):
        tz_name = os.getenv('TIMEZONE', 'UTC')
        try:
            self.local_tz = zoneinfo.ZoneInfo(tz_name)
        except zoneinfo.ZoneInfoNotFoundError:
            print(f"Warning: Timezone '{tz_name}' not found. Using UTC.", file=sys.stderr)
            self.local_tz = timezone.utc

        self.history_manager = HistoryManager(sessions_dir, self.local_tz)

    def get_or_create_session_data(
        self,
        session_id: Optional[str],
        purpose: Optional[str],
        background: Optional[str],
        roles: Optional[list[str]],
        multi_step_reasoning_enabled: bool,
        instruction: Optional[str],
        local_tz: zoneinfo.ZoneInfo,
    ) -> dict:
        if session_id:
            session_data = self.history_manager.get_session(session_id)
            if not session_data:
                raise ValueError(f"Session ID '{session_id}' not found.")
            # Ensure multi_step_reasoning_enabled is updated if provided in args
            session_data['multi_step_reasoning_enabled'] = multi_step_reasoning_enabled
        else:
            if not all([purpose, background]):
                raise ValueError("A new session requires purpose and background.")
            session_data = {
                "purpose": purpose,
                "background": background,
                "roles": roles if roles is not None else [],
                "multi_step_reasoning_enabled": multi_step_reasoning_enabled,
                "turns": []
            }
        
        if instruction:
            session_data['turns'].append({"type": "user_task", "instruction": instruction, "timestamp": datetime.now(local_tz).isoformat()})

        return session_data

    def add_turn_to_session(self, session_id: str, turn_data: dict, token_count: Optional[int] = None):
        self.history_manager.add_turn_to_session(session_id, turn_data, token_count)

    def add_references(self, session_id: str, file_paths: list[str]):
        if not session_id:
            # This case should ideally be handled by the CLI logic before calling.
            return

        session_data = self.history_manager.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session ID '{session_id}' not found.")

        references = session_data.get('references', [])
        existing_paths = {ref['path'] for ref in references}

        added_count = 0
        for file_path in file_paths:
            abs_path = os.path.abspath(file_path)
            if not os.path.isfile(abs_path):
                print(f"Warning: Path is not a file, skipping: {abs_path}", file=sys.stderr)
                continue

            if abs_path not in existing_paths:
                references.append({"path": abs_path, "disabled": False})
                existing_paths.add(abs_path)
                added_count += 1

        if added_count > 0:
            self.history_manager.update_references(session_id, references)

    def create_new_session(self, purpose: str, background: str, roles: list, multi_step_reasoning_enabled: bool = False, token_count: int = 0) -> str:
        return self.history_manager.create_new_session(purpose, background, roles, multi_step_reasoning_enabled, token_count)
