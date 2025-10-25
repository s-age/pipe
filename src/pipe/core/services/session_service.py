"""
Manages the overall session, excluding conversation_history.
"""
import json
import hashlib
import os
import sys
import shutil
import fnmatch
from datetime import datetime, timezone
import zoneinfo
from typing import Optional, List, Dict, Any

from pipe.core.models.session import Session, Reference
from pipe.core.models.turn import Turn, UserTaskTurn
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.services.history_service import HistoryService
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import FileLock, locked_json_read_modify_write, locked_json_write, locked_json_read

from pipe.core.models.hyperparameters import Hyperparameters

class SessionService:
    def __init__(self, sessions_dir: str, default_hyperparameters: dict = None):
        tz_name = os.getenv('TIMEZONE', 'UTC')
        try:
            self.timezone_obj = zoneinfo.ZoneInfo(tz_name)
        except zoneinfo.ZoneInfoNotFoundError:
            print(f"Warning: Timezone '{tz_name}' not found. Using UTC.", file=sys.stderr)
            self.timezone_obj = timezone.utc

        self.sessions_dir = sessions_dir
        self.backups_dir = os.path.join(sessions_dir, 'backups')
        self.index_path = os.path.join(sessions_dir, "index.json")
        self.default_hyperparameters = Hyperparameters(**(default_hyperparameters or {}))
        self._index_lock_path = os.path.join(self.sessions_dir, "index.json.lock")
        
        self.history_service = HistoryService(sessions_dir, self.timezone_obj)
        self._initialize()

    def _get_session_path(self, session_id: str, create_dirs: bool = False) -> str:
        safe_path_parts = [part for part in session_id.split('/') if part not in ('', '.', '..')]
        final_path = os.path.join(self.sessions_dir, *safe_path_parts)
        
        if create_dirs:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            
        return f"{final_path}.json"

    def _get_session_lock_path(self, session_id: str) -> str:
        return f"{self._get_session_path(session_id)}.lock"

    def _initialize(self):
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)
        if not os.path.exists(self.index_path):
            locked_json_write(self._index_lock_path, self.index_path, {"sessions": {}})

    def _save_session(self, session: Session):
        session_path = self._get_session_path(session.session_id)
        session_lock_path = self._get_session_lock_path(session.session_id)
        json_string = session.model_dump_json(indent=2)
        
        with FileLock(session_lock_path):
            with open(session_path, 'w', encoding='utf-8') as f:
                f.write(json_string)

    def create_new_session(self, purpose: str, background: str, roles: list, multi_step_reasoning_enabled: bool = False, token_count: int = 0, hyperparameters: dict = None, parent_id: str = None) -> str:
        if parent_id:
            parent_session_path = self._get_session_path(parent_id)
            parent_dir_path = os.path.join(self.sessions_dir, *[part for part in parent_id.split('/') if part not in ('', '.', '..')])
            if not os.path.exists(parent_session_path) and not os.path.isdir(parent_dir_path):
                raise FileNotFoundError(f"Parent session with ID '{parent_id}' not found.")

        timestamp = get_current_timestamp(self.timezone_obj)
        identity_str = json.dumps({"purpose": purpose, "background": background, "roles": roles, "multi_step_reasoning_enabled": multi_step_reasoning_enabled, "timestamp": timestamp}, sort_keys=True)
        session_hash = self._generate_hash(identity_str)
        
        session_id = f"{parent_id}/{session_hash}" if parent_id else session_hash
        
        session = Session(
            session_id=session_id,
            created_at=timestamp,
            purpose=purpose,
            background=background,
            roles=roles,
            multi_step_reasoning_enabled=multi_step_reasoning_enabled,
            token_count=token_count,
            hyperparameters=hyperparameters if hyperparameters is not None else self.default_hyperparameters,
            references=[],
            turns=[],
            pools=[]
        )

        self._save_session(session)
        self._update_index(session_id, purpose, timestamp)
        return session_id

    def get_or_create_session_data(
        self,
        session_id: Optional[str],
        purpose: Optional[str],
        background: Optional[str],
        roles: Optional[list[str]],
        multi_step_reasoning_enabled: bool,
        instruction: Optional[str],
    ) -> Session | Dict:
        if session_id:
            session = self.get_session(session_id)
            if not session:
                raise ValueError(f"Session ID '{session_id}' not found.")
            session.multi_step_reasoning_enabled = multi_step_reasoning_enabled
            if instruction:
                session.turns.append(UserTaskTurn(type="user_task", instruction=instruction, timestamp=get_current_timestamp(self.timezone_obj)))
            return session
        else:
            if not all([purpose, background]):
                raise ValueError("A new session requires purpose and background.")
            
            turns = []
            if instruction:
                turns.append({"type": "user_task", "instruction": instruction, "timestamp": get_current_timestamp(self.timezone_obj)})

            return {
                "purpose": purpose,
                "background": background,
                "roles": roles if roles is not None else [],
                "multi_step_reasoning_enabled": multi_step_reasoning_enabled,
                "turns": turns
            }

    def get_session(self, session_id: str) -> Optional[Session]:
        session_path = self._get_session_path(session_id)
        session_lock_path = self._get_session_lock_path(session_id)
        
        with FileLock(session_lock_path):
            if not os.path.exists(session_path):
                return None
            with open(session_path, 'r', encoding='utf-8') as f:
                json_string = f.read()
                return Session.model_validate_json(json_string)

    def list_sessions(self) -> dict:
        return locked_json_read(self._index_lock_path, self.index_path, default_data={}).get("sessions", {})

    def edit_session_meta(self, session_id: str, new_meta_data: dict):
        self.backup_session(session_id)
        session = self.get_session(session_id)
        if not session:
            return

        if "purpose" in new_meta_data:
            session.purpose = new_meta_data["purpose"]
        if "background" in new_meta_data:
            session.background = new_meta_data["background"]
        if "multi_step_reasoning_enabled" in new_meta_data:
            session.multi_step_reasoning_enabled = new_meta_data["multi_step_reasoning_enabled"]
        if "token_count" in new_meta_data:
            session.token_count = new_meta_data["token_count"]
        if "hyperparameters" in new_meta_data:
            session.hyperparameters = new_meta_data["hyperparameters"]

        self._save_session(session)
        self._update_index(session_id, purpose=session.purpose)

    def update_references(self, session_id: str, references: List[Reference]):
        session = self.get_session(session_id)
        if session:
            session.references = references
            self._save_session(session)

    def add_references(self, session_id: str, file_paths: list[str]):
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session ID '{session_id}' not found.")

        existing_paths = {ref.path for ref in session.references}
        added_count = 0
        for file_path in file_paths:
            abs_path = os.path.abspath(file_path)
            if not os.path.isfile(abs_path):
                print(f"Warning: Path is not a file, skipping: {abs_path}", file=sys.stderr)
                continue

            if abs_path not in existing_paths:
                session.references.append(Reference(path=abs_path, disabled=False))
                existing_paths.add(abs_path)
                added_count += 1

        if added_count > 0:
            self._save_session(session)

    def update_todos(self, session_id: str, todos: list):
        session = self.get_session(session_id)
        if session:
            session.todos = todos
            self._save_session(session)

    def delete_todos(self, session_id: str):
        session = self.get_session(session_id)
        if session:
            session.todos = None
            self._save_session(session)

    def add_to_pool(self, session_id: str, pool_data: Turn):
        session = self.get_session(session_id)
        if session:
            session.pools.append(pool_data)
            self._save_session(session)

    def get_pool(self, session_id: str) -> List[Turn]:
        session = self.get_session(session_id)
        return session.pools if session else []

    def get_and_clear_pool(self, session_id: str) -> List[Turn]:
        session = self.get_session(session_id)
        if not session:
            return []
        
        pools_to_return = session.pools.copy()
        session.pools = []
        self._save_session(session)
        return pools_to_return

    def backup_session(self, session_id: str):
        session_path = self._get_session_path(session_id)
        if not os.path.exists(session_path):
            return

        session_hash = hashlib.sha256(session_id.encode('utf-8')).hexdigest()
        timestamp = datetime.now(self.timezone_obj).strftime('%Y%m%d%H%M%S')
        backup_filename = f"{session_hash}-{timestamp}.json"
        backup_path = os.path.join(self.backups_dir, backup_filename)
        
        shutil.copy2(session_path, backup_path)

    def delete_session(self, session_id: str):
        session_path = self._get_session_path(session_id)
        session_dir = os.path.join(self.sessions_dir, session_id)
        session_lock_path = self._get_session_lock_path(session_id)
        
        with FileLock(session_lock_path):
            if os.path.isdir(session_dir):
                shutil.rmtree(session_dir)
            if os.path.exists(session_path):
                os.remove(session_path)

        for filename in os.listdir(self.backups_dir):
            if fnmatch.fnmatch(filename, f"{session_id.replace('/', '__')}-*.json"):
                os.remove(os.path.join(self.backups_dir, filename))

        def modifier(data):
            sessions_to_delete = [sid for sid in data.get("sessions", {}) if sid == session_id or sid.startswith(f"{session_id}/")]
            for sid in sessions_to_delete:
                if sid in data["sessions"]:
                    del data["sessions"][sid]
        
        locked_json_read_modify_write(self._index_lock_path, self.index_path, modifier, default_data={"sessions": {}})

    def _update_index(self, session_id: str, purpose: str = None, created_at: str = None):
        def modifier(data):
            if session_id not in data["sessions"]:
                data["sessions"][session_id] = {}
            data["sessions"][session_id]['last_updated'] = get_current_timestamp(self.timezone_obj)
            if created_at:
                data["sessions"][session_id]['created_at'] = created_at
            if purpose:
                data["sessions"][session_id]['purpose'] = purpose
        
        locked_json_read_modify_write(self._index_lock_path, self.index_path, modifier, default_data={"sessions": {}})

    def _generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def fork_session(self, session_id: str, fork_index: int) -> Optional[str]:
        self.backup_session(session_id)
        original_session = self.get_session(session_id)
        if not original_session:
            raise FileNotFoundError(f"Original session file for ID '{session_id}' not found.")

        forked_purpose = f"Fork of: {original_session.purpose}"
        timestamp = get_current_timestamp(self.timezone_obj)
        
        if not (0 <= fork_index < len(original_session.turns)):
            raise IndexError("fork_index is out of range.")
        
        fork_turn = original_session.turns[fork_index]
        if fork_turn.type != "model_response":
            raise ValueError(f"Forking is only allowed from a 'model_response' turn. Turn {fork_index + 1} is of type '{fork_turn.type}'.")

        forked_turns = original_session.turns[:fork_index + 1]

        identity_str = json.dumps({
            "purpose": forked_purpose, 
            "original_id": session_id,
            "fork_at_turn": fork_index,
            "timestamp": timestamp
        }, sort_keys=True)
        new_session_id_suffix = self._generate_hash(identity_str)

        parent_path = None
        if '/' in session_id:
            parent_path = session_id.rsplit('/', 1)[0]
        
        new_session_id = f"{parent_path}/{new_session_id_suffix}" if parent_path else new_session_id_suffix

        new_session = Session(
            session_id=new_session_id,
            created_at=timestamp,
            purpose=forked_purpose,
            background=original_session.background,
            roles=original_session.roles,
            multi_step_reasoning_enabled=original_session.multi_step_reasoning_enabled,
            token_count=0,
            hyperparameters=original_session.hyperparameters if original_session.hyperparameters else self.default_hyperparameters,
            references=original_session.references,
            turns=forked_turns
        )

        self._save_session(new_session)
        self._update_index(new_session_id, forked_purpose, timestamp)
        return new_session_id

    def add_turn_to_session(self, session_id: str, turn_data: Turn):
        session = self.get_session(session_id)
        if session:
            session.turns.append(turn_data)
            self._save_session(session)
            self._update_index(session_id)

    def update_token_count(self, session_id: str, token_count: int):
        session = self.get_session(session_id)
        if session:
            session.token_count = token_count
            self._save_session(session)
            self._update_index(session_id)
