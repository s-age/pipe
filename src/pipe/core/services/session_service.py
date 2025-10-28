"""
Manages the overall session, excluding conversation_history.
"""

import hashlib
import json
import os
import sys
import zoneinfo

from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.sessions import SessionCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.args import TaktArgs
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.reference import Reference
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
            # Handle both dicts and Reference objects
            session.references = [
                Reference(**r) if isinstance(r, dict) else r for r in references
            ]
            self._save_session(session)

    def add_reference_to_session(self, session_id: str, file_path: str):
        session = self._fetch_session(session_id)
        if not session:
            return

        abs_path = os.path.abspath(os.path.join(self.project_root, file_path))
        if not os.path.isfile(abs_path):
            print(f"Warning: Path is not a file, skipping: {abs_path}", file=sys.stderr)
            return

        ref_collection = ReferenceCollection(session.references)
        ref_collection.add(file_path)
        self._save_session(session)

    def update_reference_ttl_in_session(
        self, session_id: str, file_path: str, new_ttl: int
    ):
        session = self._fetch_session(session_id)
        if not session:
            return

        ref_collection = ReferenceCollection(session.references)
        ref_collection.update_ttl(file_path, new_ttl)
        self._save_session(session)

    def decrement_all_references_ttl_in_session(self, session_id: str):
        session = self._fetch_session(session_id)
        if not session:
            return

        ref_collection = ReferenceCollection(session.references)
        ref_collection.decrement_all_ttl()
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

    def get_pool(self, session_id: str) -> list[Turn]:
        session = self._fetch_session(session_id)
        return session.pools if session else []

    def get_and_clear_pool(self, session_id: str) -> list[Turn]:
        session = self._fetch_session(session_id)
        if not session:
            return []

        pools_to_return = session.pools.copy()
        session.pools = TurnCollection()
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
            raise ValueError(
                f"Editing turns of type '{original_turn.type}' is not allowed."
            )

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

    def fork_session(self, session_id: str, fork_index: int) -> str | None:
        original_session = self._fetch_session(session_id)
        if not original_session:
            raise FileNotFoundError(
                f"Original session with ID '{session_id}' not found."
            )

        if not (0 <= fork_index < len(original_session.turns)):
            raise IndexError("fork_index is out of range.")

        fork_turn = original_session.turns[fork_index]
        if fork_turn.type != "model_response":
            raise ValueError(
                "Forking is only allowed from a 'model_response' turn. "
                f"Turn {fork_index + 1} is of type '{fork_turn.type}'."
            )

        timestamp = get_current_timestamp(self.timezone_obj)
        forked_purpose = f"Fork of: {original_session.purpose}"
        forked_turns = original_session.turns[: fork_index + 1]

        identity_str = json.dumps(
            {
                "purpose": forked_purpose,
                "original_id": session_id,
                "fork_at_turn": fork_index,
                "timestamp": timestamp,
            },
            sort_keys=True,
        )
        new_session_id_suffix = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

        parent_path = session_id.rsplit("/", 1)[0] if "/" in session_id else None
        new_session_id = (
            f"{parent_path}/{new_session_id_suffix}"
            if parent_path
            else new_session_id_suffix
        )

        new_session = Session(
            session_id=new_session_id,
            created_at=timestamp,
            purpose=forked_purpose,
            background=original_session.background,
            roles=original_session.roles,
            multi_step_reasoning_enabled=original_session.multi_step_reasoning_enabled,
            hyperparameters=original_session.hyperparameters
            or self.default_hyperparameters,
            references=original_session.references,
            turns=forked_turns,
        )

        self._save_session(new_session)

        collection = self.list_sessions()
        collection.update(
            new_session.session_id, new_session.purpose, new_session.created_at
        )
        collection.save()

        return new_session.session_id

    def add_turn_to_session(self, session_id: str, turn_data: Turn):
        session = self._fetch_session(session_id)
        if session:
            session.turns.append(turn_data)
            self._save_session(session)

            collection = self.list_sessions()
            collection.update(session_id)
            collection.save()

    def merge_pool_into_turns(self, session_id: str):
        """Merges all turns from the pool into the main turns list and clears the
        pool."""
        session = self._fetch_session(session_id)
        if session and session.pools:
            session.turns.extend(session.pools)
            session.pools = TurnCollection()  # Clear the pool immediately after merge
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

    def expire_old_tool_responses(self, session_id: str):
        """
        Expires the message content of old tool_response turns to save tokens,
        while preserving the 'succeeded' status. This uses a safe rebuild pattern.
        """
        session = self._fetch_session(session_id)
        if not session or not session.turns:
            return

        user_tasks = [turn for turn in session.turns if turn.type == "user_task"]
        if len(user_tasks) <= 3:
            return

        expiration_threshold_timestamp = user_tasks[-3].timestamp

        new_turns = []
        modified = False
        for turn in session.turns:
            # Check if the turn is a candidate for expiration
            if (
                turn.type == "tool_response"
                and turn.timestamp < expiration_threshold_timestamp
                and isinstance(turn.response, dict)
                and turn.response.get("status") == "succeeded"
            ):  # Only expire successful responses
                # Create a deep copy to modify
                modified_turn = turn.model_copy(deep=True)

                # Only change the message, keep the status
                modified_turn.response["message"] = (
                    "This tool response has expired to save tokens."
                )

                new_turns.append(modified_turn)
                modified = True
            else:
                # Add the original turn if no modification is needed
                new_turns.append(turn)

        if modified:
            session.turns = TurnCollection(new_turns)
            self._save_session(session)
