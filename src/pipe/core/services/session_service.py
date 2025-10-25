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

from pipe.core.models.session import Session
from pipe.core.models.reference import Reference
from pipe.core.models.turn import Turn, UserTaskTurn
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.services.history_service import HistoryService
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import FileLock, locked_json_read_modify_write, locked_json_write, locked_json_read
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings
from pipe.core.collections.sessions import SessionCollection
from pipe.core.collections.turns import TurnCollection

class SessionService:
    def __init__(self, project_root: str, settings: Settings):
        self.project_root = project_root
        self.settings = settings
        self.current_session: Optional[Session] = None
        self.current_session_id: Optional[str] = None

        tz_name = settings.timezone
        try:
            self.timezone_obj = zoneinfo.ZoneInfo(tz_name)
        except zoneinfo.ZoneInfoNotFoundError:
            print(f"Warning: Timezone '{tz_name}' not found. Using UTC.", file=sys.stderr)
            self.timezone_obj = timezone.utc

        self.sessions_dir = os.path.join(project_root, 'sessions')
        self.backups_dir = os.path.join(self.sessions_dir, 'backups')
        self.index_path = os.path.join(self.sessions_dir, "index.json")
        
        default_hyperparameters_dict = {
            "temperature": self.settings.parameters.temperature.model_dump(),
            "top_p": self.settings.parameters.top_p.model_dump(),
            "top_k": self.settings.parameters.top_k.model_dump()
        }
        self.default_hyperparameters = Hyperparameters(**default_hyperparameters_dict)

        self._index_lock_path = os.path.join(self.sessions_dir, "index.json.lock")
        
        self.history_service = HistoryService(self.sessions_dir, self.timezone_obj)
        self._initialize()
        
        # Load all sessions into the collection
        all_sessions = self._load_all_sessions()
        self.session_collection = SessionCollection(all_sessions, self.timezone_obj)

    def reload_collection(self):
        """Reloads all sessions from disk into the session collection."""
        all_sessions = self._load_all_sessions()
        self.session_collection = SessionCollection(all_sessions, self.timezone_obj)

    def _load_all_sessions(self) -> Dict[str, Session]:
        """Loads all sessions from their JSON files based on the index."""
        sessions = {}
        index_data = locked_json_read(self._index_lock_path, self.index_path, default_data={"sessions": {}})
        for session_id in index_data.get("sessions", {}):
            session = self._load_session_from_file(session_id)
            if session:
                sessions[session_id] = session
        return sessions

    def _load_session_from_file(self, session_id: str) -> Optional[Session]:
        """Loads a single session from its JSON file, applying data migrations if necessary."""
        session_path = self._get_session_path(session_id)
        if not os.path.exists(session_path):
            return None
        
        with open(session_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # --- Data Migration ---
        # Ensure all turns in 'turns' and 'pools' have a timestamp.
        session_creation_time = data.get('created_at', get_current_timestamp(self.timezone_obj))
        for turn_list_key in ['turns', 'pools']:
            if turn_list_key in data and isinstance(data[turn_list_key], list):
                for turn_data in data[turn_list_key]:
                    if isinstance(turn_data, dict):
                        # Migrate missing timestamps
                        if 'timestamp' not in turn_data:
                            turn_data['timestamp'] = session_creation_time
                        # Migrate missing original_turns_range for compressed_history
                        if turn_data.get('type') == 'compressed_history' and 'original_turns_range' not in turn_data:
                            turn_data['original_turns_range'] = [0, 0]
        # --- End of Data Migration ---

        return Session.model_validate(data)

    def prepare_session_for_takt(self, args: TaktArgs):
        session_id = args.session
        if session_id:
            session_id = session_id.strip().rstrip('.')
        
        session = None
        if session_id:
            session = self.get_session(session_id)
            if not session:
                raise FileNotFoundError(f"Session with ID '{session_id}' not found.")
        
        if not session:  # New session
            if not all([args.purpose, args.background]):
                raise ValueError("A new session requires --purpose and --background for the first instruction.")
            
            session_id = self.create_new_session(
                purpose=args.purpose,
                background=args.background,
                roles=args.roles,
                multi_step_reasoning_enabled=args.multi_step_reasoning,
                parent_id=args.parent
            )
            
            first_turn = UserTaskTurn(type="user_task", instruction=args.instruction, timestamp=get_current_timestamp(self.timezone_obj))
            self.add_turn_to_session(session_id, first_turn)
            
            print(f"Conductor Agent: Creating new session...\nNew session created: {session_id}", file=sys.stderr)
            session = self.get_session(session_id)
        
        else:  # Existing session
            new_turn = UserTaskTurn(type="user_task", instruction=args.instruction, timestamp=get_current_timestamp(self.timezone_obj))
            self.add_turn_to_session(session_id, new_turn)
            print(f"Conductor Agent: Continuing session: {session_id}", file=sys.stderr)
            session = self.get_session(session_id)

        if args.references:
            references = [Reference(path=ref.strip(), disabled=False) for ref in args.references if ref.strip()]
            existing_paths = {ref.path for ref in session.references}
            new_references = [ref for ref in references if ref.path not in existing_paths]
            
            if new_references:
                self.add_references(session_id, [ref.path for ref in new_references])
                session.references.extend(new_references)
                print(f"Added {len(new_references)} new references to session {session_id}.", file=sys.stderr)

        self.current_session = session
        self.current_session_id = session_id

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
        session_path = self._get_session_path(session.session_id, create_dirs=True)
        session_lock_path = self._get_session_lock_path(session.session_id)
        json_string = session.model_dump_json(indent=2)
        
        with FileLock(session_lock_path):
            with open(session_path, 'w', encoding='utf-8') as f:
                f.write(json_string)

    def create_new_session(self, purpose: str, background: str, roles: list, multi_step_reasoning_enabled: bool = False, token_count: int = 0, hyperparameters: dict = None, parent_id: str = None) -> str:
        if parent_id:
            parent_session = self.session_collection.find(parent_id)
            if not parent_session:
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
            hyperparameters=hyperparameters if hyperparameters is not None else self.default_hyperparameters
        )

        self.session_collection.add(session)
        self._save_session(session)
        self._update_index(session_id, purpose, timestamp)
        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.session_collection.find(session_id)

    def list_sessions(self) -> dict:
        # This now just returns the data from the index file for compatibility with web UI
        # A better approach would be to have the web UI consume a list of Session objects
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
        # Backup before deleting
        self.backup_session(session_id)
        
        # Get all child session IDs before deleting from collection
        child_ids = [sid for sid in self.session_collection.list_all() if sid.startswith(f"{session_id}/")]
        all_ids_to_delete = [session_id] + child_ids

        # Delete from collection
        if self.session_collection.delete(session_id):
            # Delete files and update index
            for sid in all_ids_to_delete:
                session_path = self._get_session_path(sid)
                session_lock_path = self._get_session_lock_path(sid)
                with FileLock(session_lock_path):
                    if os.path.exists(session_path):
                        os.remove(session_path)

            def modifier(data):
                for sid in all_ids_to_delete:
                    if sid in data.get("sessions", {}):
                        del data["sessions"][sid]
            
            locked_json_read_modify_write(self._index_lock_path, self.index_path, modifier, default_data={"sessions": {}})

    def _update_index(self, session_id: str, purpose: str = None, created_at: str = None):
        def modifier(data):
            if "sessions" not in data:
                data["sessions"] = {}
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
        
        new_session = self.session_collection.fork(session_id, fork_index, self.default_hyperparameters)
        
        self.session_collection.add(new_session)
        self._save_session(new_session)
        self._update_index(new_session.session_id, new_session.purpose, new_session.created_at)
        
        return new_session.session_id

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
