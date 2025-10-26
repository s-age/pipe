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
        self.current_instruction: Optional[str] = None

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
        
        self._initialize()

    def _fetch_session(self, session_id: str) -> Optional[Session]:
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

    def get_session(self, session_id: str) -> Optional[Session]:
        """Loads a specific session."""
        return self._fetch_session(session_id)

    def list_sessions(self) -> SessionCollection:
        """Loads and returns the latest session collection from disk."""
        return SessionCollection(self.index_path, self.timezone_obj)

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
        self.current_instruction = args.instruction

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

    def _save_session(self, session: Session):
        session_path = self._get_session_path(session.session_id)
        session_lock_path = self._get_session_lock_path(session.session_id)
        session.save(session_path, session_lock_path)

    def create_new_session(self, purpose: str, background: str, roles: list, multi_step_reasoning_enabled: bool = False, token_count: int = 0, hyperparameters: dict = None, parent_id: str = None) -> str:
        if parent_id:
            parent_session = self._fetch_session(parent_id)
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

        self._save_session(session)
        
        collection = self.list_sessions()
        collection.update(session_id, purpose, timestamp)
        collection.save()
        
        return session_id

    def edit_session_meta(self, session_id: str, new_meta_data: dict):
        self.backup_session(session_id)
        session = self._fetch_session(session_id)
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

        collection = self.list_sessions()
        collection.update(session_id, purpose=session.purpose)
        collection.save()

    def update_references(self, session_id: str, references: list):
        session = self._fetch_session(session_id)
        if session:
            # Handle both dicts and Reference objects
            session.references = [Reference(**r) if isinstance(r, dict) else r for r in references]
            self._save_session(session)

    def add_references(self, session_id: str, file_paths: list[str]):
        session = self._fetch_session(session_id)
        if not session:
            raise ValueError(f"Session ID '{session_id}' not found.")

        existing_paths = {ref.path for ref in session.references}
        added_count = 0
        for file_path in file_paths:
            # Resolve the path relative to the project root
            abs_path = os.path.abspath(os.path.join(self.project_root, file_path))
            if not os.path.isfile(abs_path):
                print(f"Warning: Path is not a file, skipping: {abs_path}", file=sys.stderr)
                continue

            # Store the original, relative path in the reference object
            if file_path not in existing_paths:
                session.references.append(Reference(path=file_path, disabled=False))
                existing_paths.add(file_path)
                added_count += 1

        if added_count > 0:
            self._save_session(session)

    def update_todos(self, session_id: str, todos: list):
        session = self._fetch_session(session_id)
        if session:
            from pipe.core.models.todo import TodoItem
            # Handle both dicts and TodoItem objects
            session.todos = [TodoItem(**t) if isinstance(t, dict) else t for t in todos]
            self._save_session(session)

    def delete_todos(self, session_id: str):
        session = self._fetch_session(session_id)
        if session:
            session.todos = None
            self._save_session(session)

    def add_to_pool(self, session_id: str, pool_data: Turn):
        session = self._fetch_session(session_id)
        if session:
            session.pools.append(pool_data)
            self._save_session(session)

    def get_pool(self, session_id: str) -> List[Turn]:
        session = self._fetch_session(session_id)
        return session.pools if session else []

    def get_and_clear_pool(self, session_id: str) -> List[Turn]:
        session = self._fetch_session(session_id)
        if not session:
            return []
        
        pools_to_return = session.pools.copy()
        session.pools = TurnCollection()
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
        
        collection = self.list_sessions()
        child_ids = [sid for sid in collection if sid.startswith(f"{session_id}/")]
        all_ids_to_delete = [session_id] + child_ids

        # Delete session files
        for sid in all_ids_to_delete:
            session_path = self._get_session_path(sid)
            session_lock_path = self._get_session_lock_path(sid)
            with FileLock(session_lock_path):
                if os.path.exists(session_path):
                    os.remove(session_path)

        # Update and save the index
        collection.delete(session_id)
        collection.save()

    def delete_turn(self, session_id: str, turn_index: int):
        """Deletes a specific turn from a session."""
        session = self._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")
        
        if not (0 <= turn_index < len(session.turns)):
            raise IndexError("Turn index out of range.")
            
        del session.turns[turn_index]
        self._save_session(session)
        
        # Update the index to reflect the change
        collection = self.list_sessions()
        collection.update(session_id)
        collection.save()

    def edit_turn(self, session_id: str, turn_index: int, new_data: dict):
        """Edits a specific turn in a session."""
        session = self._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        if not (0 <= turn_index < len(session.turns)):
            raise IndexError("Turn index out of range.")

        original_turn = session.turns[turn_index]
        if original_turn.type not in ["user_task", "model_response"]:
            raise ValueError(f"Editing turns of type '{original_turn.type}' is not allowed.")

        turn_as_dict = original_turn.model_dump()
        turn_as_dict.update(new_data)
        
        if original_turn.type == "user_task":
            session.turns[turn_index] = UserTaskTurn(**turn_as_dict)
        elif original_turn.type == "model_response":
            from pipe.core.models.turn import ModelResponseTurn
            session.turns[turn_index] = ModelResponseTurn(**turn_as_dict)

        self._save_session(session)

        # Update the index to reflect the change
        collection = self.list_sessions()
        collection.update(session_id)
        collection.save()


    def _generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def fork_session(self, session_id: str, fork_index: int) -> Optional[str]:
        self.backup_session(session_id)
        
        original_session = self._fetch_session(session_id)
        if not original_session:
            raise FileNotFoundError(f"Original session with ID '{original_session_id}' not found.")

        if not (0 <= fork_index < len(original_session.turns)):
            raise IndexError("fork_index is out of range.")
        
        fork_turn = original_session.turns[fork_index]
        if fork_turn.type != "model_response":
            raise ValueError(f"Forking is only allowed from a 'model_response' turn. Turn {fork_index + 1} is of type '{fork_turn.type}'.")

        timestamp = get_current_timestamp(self.timezone_obj)
        forked_purpose = f"Fork of: {original_session.purpose}"
        forked_turns = original_session.turns[:fork_index + 1]

        identity_str = json.dumps({
            "purpose": forked_purpose, 
            "original_id": session_id,
            "fork_at_turn": fork_index,
            "timestamp": timestamp
        }, sort_keys=True)
        new_session_id_suffix = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

        parent_path = session_id.rsplit('/', 1)[0] if '/' in session_id else None
        new_session_id = f"{parent_path}/{new_session_id_suffix}" if parent_path else new_session_id_suffix

        new_session = Session(
            session_id=new_session_id,
            created_at=timestamp,
            purpose=forked_purpose,
            background=original_session.background,
            roles=original_session.roles,
            multi_step_reasoning_enabled=original_session.multi_step_reasoning_enabled,
            hyperparameters=original_session.hyperparameters or self.default_hyperparameters,
            references=original_session.references,
            turns=forked_turns
        )
        
        self._save_session(new_session)
        
        collection = self.list_sessions()
        collection.update(new_session.session_id, new_session.purpose, new_session.created_at)
        collection.save()
        
        return new_session.session_id

    def add_turn_to_session(self, session_id: str, turn_data: Turn):
        session = self._fetch_session(session_id)
        if session:
            # Merge pooled turns before adding the new turn
            if session.pools:
                session.turns.extend(session.pools)
                session.pools = TurnCollection()  # Clear the pool

            session.turns.append(turn_data)
            self._save_session(session)
            
            collection = self.list_sessions()
            collection.update(session_id)
            collection.save()

    def update_token_count(self, session_id: str, token_count: int):
        session = self._fetch_session(session_id)
        if session:
            session.token_count = token_count
            self._save_session(session)

            collection = self.list_sessions()
            collection.update(session_id)
            collection.save()
