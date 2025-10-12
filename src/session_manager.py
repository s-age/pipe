import json
from pathlib import Path
from datetime import datetime, timezone
import zoneinfo
from typing import Optional
import os

from src.history_manager import HistoryManager

class SessionManager:
    def __init__(self, sessions_dir: Path):
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

    def create_new_session(self, purpose: str, background: str, roles: list, multi_step_reasoning_enabled: bool = False, token_count: int = 0) -> str:
        return self.history_manager.create_new_session(purpose, background, roles, multi_step_reasoning_enabled, token_count)
