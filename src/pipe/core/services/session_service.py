"""
Manages the overall session, excluding conversation_history.
"""

import hashlib
import os
import sys
import zoneinfo

from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.sessions import SessionCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.args import TaktArgs
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.models.turn import Turn, UserTaskTurn
from pipe.core.utils.datetime import get_current_timestamp


class SessionService:
    def __init__(self, project_root: str, settings: Settings):
        self.project_root = project_root
        self.settings = settings
        self.current_session: Session | None = None
        self.current_session_id: str | None = None
        self.current_instruction: str | None = None

        tz_name = settings.timezone
        try:
            self.timezone_obj = zoneinfo.ZoneInfo(tz_name)
        except zoneinfo.ZoneInfoNotFoundError:
            print(
                f"Warning: Timezone '{tz_name}' not found. Using UTC.", file=sys.stderr
            )
            self.timezone_obj = zoneinfo.ZoneInfo("UTC")

        self.sessions_dir = os.path.join(project_root, "sessions")
        self.backups_dir = os.path.join(self.sessions_dir, "backups")
        self.index_path = os.path.join(self.sessions_dir, "index.json")

        default_hyperparameters_dict = {
            "temperature": self.settings.parameters.temperature.model_dump(),
            "top_p": self.settings.parameters.top_p.model_dump(),
            "top_k": self.settings.parameters.top_k.model_dump(),
        }
        self.default_hyperparameters = Hyperparameters(**default_hyperparameters_dict)

        # --- Setup the Session class (Active Record style) ---
        Session.setup(
            sessions_dir=self.sessions_dir,
            backups_dir=self.backups_dir,
            timezone_name=self.settings.timezone,
            default_hyperparameters=self.default_hyperparameters,
        )
        # ----------------------------------------------------

        self._initialize()

    def _fetch_session(self, session_id: str) -> Session | None:
        """Loads a single session from its JSON file."""
        return Session.find(session_id)

    def get_session(self, session_id: str) -> Session | None:
        """Loads a specific session."""
        return self._fetch_session(session_id)

    def list_sessions(self) -> SessionCollection:
        """Loads and returns the latest session collection from disk."""
        return SessionCollection(self.index_path, self.settings.timezone)

    def prepare_session_for_takt(self, args: TaktArgs, is_dry_run: bool = False):
        session_id = args.session
        if session_id:
            session_id = session_id.strip().rstrip(".")

        session = None
        if session_id:
            session = self.get_session(session_id)
            if not session:
                raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        if not session:  # New session
            if not all([args.purpose, args.background]):
                raise ValueError(
                    "A new session requires --purpose and --background for the first "
                    "instruction."
                )

            session = self.create_new_session(
                purpose=args.purpose,
                background=args.background,
                roles=args.roles,
                multi_step_reasoning_enabled=args.multi_step_reasoning,
                parent_id=args.parent,
            )
            session_id = session.session_id

            if not is_dry_run:
                first_turn = UserTaskTurn(
                    type="user_task",
                    instruction=args.instruction,
                    timestamp=get_current_timestamp(self.timezone_obj),
                )
                self.add_turn_to_session(session_id, first_turn)

            print(
                "Conductor Agent: Creating new session...\n"
                f"New session created: {session_id}",
                file=sys.stderr,
            )
            session = self.get_session(session_id)

        else:  # Existing session
            if not is_dry_run:
                new_turn = UserTaskTurn(
                    type="user_task",
                    instruction=args.instruction,
                    timestamp=get_current_timestamp(self.timezone_obj),
                )
                self.add_turn_to_session(session_id, new_turn)
            print(f"Conductor Agent: Continuing session: {session_id}", file=sys.stderr)
            session = self.get_session(session_id)

        if args.references:
            for ref_path in args.references:
                if ref_path.strip():
                    self.add_reference_to_session(session_id, ref_path.strip())
            session = self.get_session(
                session_id
            )  # Re-fetch session to get updated references

        self.current_session = session
        self.current_session_id = session_id
        self.current_instruction = args.instruction

    def _get_session_path(self, session_id: str) -> str:
        safe_path_parts = [
            part for part in session_id.split("/") if part not in ("", ".", "..")
        ]
        final_path = os.path.join(self.sessions_dir, *safe_path_parts)

        return f"{final_path}.json"

    def _get_session_lock_path(self, session_id: str) -> str:
        return f"{self._get_session_path(session_id)}.lock"

    def _initialize(self):
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)

    def _save_session(self, session: Session):
        session.save()

    def create_new_session(
        self,
        purpose: str,
        background: str,
        roles: list,
        multi_step_reasoning_enabled: bool = False,
        token_count: int = 0,
        hyperparameters: dict | None = None,
        parent_id: str | None = None,
    ) -> Session:
        session = Session.create(
            purpose=purpose,
            background=background,
            roles=roles,
            multi_step_reasoning_enabled=multi_step_reasoning_enabled,
            token_count=token_count,
            hyperparameters=hyperparameters,
            parent_id=parent_id,
        )

        collection = self.list_sessions()
        collection.update(session.session_id, session.purpose, session.created_at)
        collection.save()

        return session

    def edit_session_meta(self, session_id: str, new_meta_data: dict):
        session = self._fetch_session(session_id)
        if not session:
            return

        session.backup()
        session.edit_meta(new_meta_data)

        collection = self.list_sessions()
        collection.update(session_id, purpose=session.purpose)
        collection.save()

    def update_references(self, session_id: str, references: list):
        session = self._fetch_session(session_id)
        if session:
            session.references = ReferenceCollection(references)
            self._save_session(session)

    def add_reference_to_session(self, session_id: str, file_path: str):
        session = self._fetch_session(session_id)
        if not session:
            return

        abs_path = os.path.abspath(os.path.join(self.project_root, file_path))
        if not os.path.isfile(abs_path):
            print(f"Warning: Path is not a file, skipping: {abs_path}", file=sys.stderr)
            return

        session.references.add(file_path)
        self._save_session(session)

    def update_reference_ttl_in_session(
        self, session_id: str, file_path: str, new_ttl: int
    ):
        session = self._fetch_session(session_id)
        if not session:
            return

        session.references.update_ttl(file_path, new_ttl)
        self._save_session(session)

    def decrement_all_references_ttl_in_session(self, session_id: str):
        session = self._fetch_session(session_id)
        if not session:
            return

        session.references.decrement_all_ttl()
        self._save_session(session)

    def update_todos(self, session_id: str, todos: list):
        session = self._fetch_session(session_id)
        if session:
            from pipe.core.collections.todos import TodoCollection

            TodoCollection.update_in_session(session, todos)
            self._save_session(session)

    def delete_todos(self, session_id: str):
        session = self._fetch_session(session_id)
        if session:
            from pipe.core.collections.todos import TodoCollection

            TodoCollection.delete_in_session(session)
            self._save_session(session)

    def add_to_pool(self, session_id: str, pool_data: Turn):
        session = self._fetch_session(session_id)
        if session:
            from pipe.core.collections.pools import PoolCollection

            PoolCollection.add(session, pool_data)
            self._save_session(session)

    def get_pool(self, session_id: str) -> list[Turn]:
        session = self._fetch_session(session_id)
        return session.pools if session else []

    def get_and_clear_pool(self, session_id: str) -> list[Turn]:
        session = self._fetch_session(session_id)
        if not session:
            return []

        from pipe.core.collections.pools import PoolCollection

        pools_to_return = PoolCollection.get_and_clear(session)
        self._save_session(session)
        return pools_to_return

    def delete_session(self, session_id: str):
        collection = self.list_sessions()
        child_ids = [sid for sid in collection if sid.startswith(f"{session_id}/")]
        all_ids_to_delete = [session_id] + child_ids

        for sid in all_ids_to_delete:
            session = self._fetch_session(sid)
            if session:
                session.backup()
                session.destroy()

        # Update and save the index
        collection.delete(session_id)
        collection.save()

    def delete_turn(self, session_id: str, turn_index: int):
        """Deletes a specific turn from a session."""
        session = self._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        collection = self.list_sessions()
        collection.delete_turn(session, turn_index)

    def edit_turn(self, session_id: str, turn_index: int, new_data: dict):
        """Edits a specific turn in a session."""
        session = self._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        collection = self.list_sessions()
        collection.edit_turn(session, turn_index, new_data)

    def _generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def fork_session(self, session_id: str, fork_index: int) -> str | None:
        original_session = self._fetch_session(session_id)
        if not original_session:
            raise FileNotFoundError(
                f"Original session with ID '{session_id}' not found."
            )

        collection = self.list_sessions()
        new_session = collection.fork(original_session, fork_index)
        return new_session.session_id

    def add_turn_to_session(self, session_id: str, turn_data: Turn):
        session = self._fetch_session(session_id)
        if session:
            collection = self.list_sessions()
            collection.add_turn(session, turn_data)

    def merge_pool_into_turns(self, session_id: str):
        """Merges all turns from the pool into the main turns list and clears the
        pool."""
        session = self._fetch_session(session_id)
        if session:
            collection = self.list_sessions()
            collection.merge_pool(session)

    def update_token_count(self, session_id: str, token_count: int):
        session = self._fetch_session(session_id)
        if session:
            session.token_count = token_count
            self._save_session(session)

            collection = self.list_sessions()
            collection.update(session_id)
            collection.save()

    def expire_old_tool_responses(self, session_id: str):
        """
        Expires the message content of old tool_response turns to save tokens.
        """
        session = self._fetch_session(session_id)
        if session:
            if TurnCollection.expire_old_tool_responses(session):
                self._save_session(session)
