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
from pipe.core.domains.references import add_reference
from pipe.core.models.args import TaktArgs
from pipe.core.models.artifact import Artifact
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.models.turn import Turn, UserTaskTurn
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.utils.datetime import get_current_timestamp


class SessionService:
    def __init__(
        self,
        project_root: str,
        settings: Settings,
        repository: SessionRepository,
    ):
        self.project_root = project_root
        self.settings = settings
        self.repository = repository
        self.current_session: Session | None = None
        self.current_session_id: str | None = None
        self.current_instruction: str | None = None

        self.history_manager = self  # For compatibility with tools

        tz_name = settings.timezone
        try:
            self.timezone_obj = zoneinfo.ZoneInfo(tz_name)
        except zoneinfo.ZoneInfoNotFoundError:
            print(
                f"Warning: Timezone '{tz_name}' not found. Using UTC.", file=sys.stderr
            )
            self.timezone_obj = zoneinfo.ZoneInfo("UTC")

        # The repository now handles initialization of directories.
        # self._initialize()

    def _fetch_session(self, session_id: str) -> Session | None:
        """Loads a single session using the repository."""
        return self.repository.find(session_id)

    def get_session(self, session_id: str) -> Session | None:
        """Loads a specific session."""
        return self._fetch_session(session_id)

    def list_sessions(self) -> SessionCollection:
        """Loads and returns the latest session collection from the repository."""
        index_data = self.repository.get_index()
        return SessionCollection(index_data, self.settings.timezone)

    def prepare(self, args: TaktArgs, is_dry_run: bool = False):
        """
        Finds an existing session based on args or creates a new one,
        then applies initial turns and references from args.
        """

        session_id = args.session.strip().rstrip(".") if args.session else None

        if session_id:
            session = self.repository.find(session_id)
            if not session:
                raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

            if not is_dry_run and args.instruction:
                new_turn = UserTaskTurn(
                    type="user_task",
                    instruction=args.instruction,
                    timestamp=get_current_timestamp(self.timezone_obj),
                )
                session.add_turn(new_turn)
            print(f"Continuing session: {session.session_id}", file=sys.stderr)
        else:
            if not all([args.purpose, args.background]):
                raise ValueError(
                    "A new session requires --purpose and --background for the first "
                    "instruction."
                )

            session = self._create_session_object(
                purpose=args.purpose,
                background=args.background,
                roles=args.roles or [],
                multi_step_reasoning_enabled=args.multi_step_reasoning,
                artifacts=args.artifacts or [],
                procedure=args.procedure,
                parent_id=args.parent,
            )

            if not is_dry_run and args.instruction:
                first_turn = UserTaskTurn(
                    type="user_task",
                    instruction=args.instruction,
                    timestamp=get_current_timestamp(self.timezone_obj),
                )
                session.add_turn(first_turn)
            print(f"New session created: {session.session_id}", file=sys.stderr)

        if args.references:
            from pipe.core.domains.references import add_reference

            persistent_references = set(args.references_persist)

            for ref_path in args.references:
                if ref_path.strip():
                    is_persistent = ref_path.strip() in persistent_references
                    add_reference(
                        session.references,
                        ref_path.strip(),
                        session.references.default_ttl,
                        persist=is_persistent,
                    )

        self.repository.save(session)

        self.current_session = session
        self.current_session_id = session.session_id
        self.current_instruction = args.instruction

    def _get_session_path(self, session_id: str) -> str:
        # This logic is now in the repository
        return self.repository._get_path_for_id(session_id)

    def _get_session_lock_path(self, session_id: str) -> str:
        return f"{self._get_session_path(session_id)}.lock"

    def _initialize(self):
        # This logic is now in the repository
        pass

    def _save_session(self, session: Session):
        self.repository.save(session)

    def create_new_session(
        self,
        purpose: str,
        background: str,
        roles: list,
        multi_step_reasoning_enabled: bool = False,
        token_count: int = 0,
        hyperparameters: dict | None = None,
        parent_id: str | None = None,
        artifacts: list[str] | None = None,
        procedure: str | None = None,
    ) -> Session:
        session = self._create_session_object(
            purpose=purpose,
            background=background,
            roles=roles,
            multi_step_reasoning_enabled=multi_step_reasoning_enabled,
            token_count=token_count,
            hyperparameters=hyperparameters,
            parent_id=parent_id,
            artifacts=artifacts,
            procedure=procedure,
        )

        self.repository.save(session)

        return session

    def edit_session_meta(self, session_id: str, new_meta_data: dict):
        session = self._fetch_session(session_id)
        if not session:
            return

        self.repository.backup(session)
        session.edit_meta(new_meta_data)
        self.repository.save(session)

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

        add_reference(session.references, file_path, session.references.default_ttl)
        self._save_session(session)

    def update_reference_ttl_in_session(
        self, session_id: str, file_path: str, new_ttl: int
    ):
        session = self._fetch_session(session_id)
        if not session:
            return

        from pipe.core.domains.references import update_reference_ttl

        update_reference_ttl(session.references, file_path, new_ttl)
        self._save_session(session)

    def update_reference_persist_in_session(
        self, session_id: str, file_path: str, new_persist_state: bool
    ):
        session = self._fetch_session(session_id)
        if not session:
            return

        from pipe.core.domains.references import update_reference_persist

        update_reference_persist(session.references, file_path, new_persist_state)
        self._save_session(session)

    def toggle_reference_disabled_in_session(self, session_id: str, file_path: str):
        session = self._fetch_session(session_id)
        if not session:
            return

        from pipe.core.domains.references import toggle_reference_disabled

        toggle_reference_disabled(session.references, file_path)
        self._save_session(session)

    def decrement_all_references_ttl_in_session(self, session_id: str):
        session = self._fetch_session(session_id)
        if not session:
            return

        from pipe.core.domains.references import decrement_all_references_ttl

        decrement_all_references_ttl(session.references)
        self._save_session(session)

    def add_multiple_references(self, session_id: str, file_paths: list[str]):
        session = self._fetch_session(session_id)
        if not session:
            return

        for file_path in file_paths:
            abs_path = os.path.abspath(os.path.join(self.project_root, file_path))
            if not os.path.isfile(abs_path):
                print(
                    f"Warning: Path is not a file, skipping: {abs_path}",
                    file=sys.stderr,
                )
                continue
            add_reference(session.references, file_path, session.references.default_ttl)
        self._save_session(session)

    def update_todos(self, session_id: str, todos: list):
        session = self._fetch_session(session_id)
        if session:
            from pipe.core.domains.todos import update_todos_in_session

            update_todos_in_session(session, todos)
            self._save_session(session)

    def delete_todos(self, session_id: str):
        session = self._fetch_session(session_id)
        if session:
            from pipe.core.domains.todos import delete_todos_in_session

            delete_todos_in_session(session)
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
        self.repository.delete(session_id)

    def delete_turn(self, session_id: str, turn_index: int):
        """Deletes a specific turn from a session."""
        session = self._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        session.delete_turn(turn_index)
        self.repository.save(session)

    def edit_turn(self, session_id: str, turn_index: int, new_data: dict):
        """Edits a specific turn in a session."""
        session = self._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        session.edit_turn(turn_index, new_data)
        self.repository.save(session)

    def _generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def fork_session(self, session_id: str, fork_index: int) -> str | None:
        """Forks a session at a specific turn index."""
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

        # This logic should be part of a pure domain object method
        new_session = original_session.fork(fork_index, self.timezone_obj)

        self.repository.save(new_session)

        return new_session.session_id

    def add_turn_to_session(self, session_id: str, turn_data: Turn):
        session = self._fetch_session(session_id)
        if session:
            session.add_turn(turn_data)
            self.repository.save(session)

    def merge_pool_into_turns(self, session_id: str):
        """Merges all turns from the pool into the main turns list and clears the
        pool."""
        session = self._fetch_session(session_id)
        if session:
            session.merge_pool()
            self.repository.save(session)

    def _create_session_object(
        self,
        purpose: str,
        background: str,
        roles: list,
        multi_step_reasoning_enabled: bool = False,
        token_count: int = 0,
        hyperparameters: dict | None = None,
        parent_id: str | None = None,
        artifacts: list[Artifact] | None = None,  # Changed type to list[Artifact]
        procedure: str | None = None,
    ) -> Session:
        if parent_id:
            parent_session = self.repository.find(parent_id)
            if not parent_session:
                raise FileNotFoundError(
                    f"Parent session with ID '{parent_id}' not found."
                )

        timestamp = get_current_timestamp(self.timezone_obj)
        identity_str = json.dumps(
            {
                "purpose": purpose,
                "background": background,
                "roles": roles,
                "multi_step_reasoning_enabled": multi_step_reasoning_enabled,
                "artifacts": artifacts,
                "procedure": procedure,
                "timestamp": timestamp,
            },
            sort_keys=True,
        )
        session_hash = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

        session_id = f"{parent_id}/{session_hash}" if parent_id else session_hash

        # TODO: Default hyperparameters should be handled more cleanly
        print(
            f"DEBUG: type of self.settings.parameters.temperature: "
            f"{type(self.settings.parameters.temperature)}",
            file=sys.stderr,
        )
        print(
            f"DEBUG: self.settings.parameters.temperature: "
            f"{self.settings.parameters.temperature}",
            file=sys.stderr,
        )
        default_hyperparameters = Hyperparameters(
            temperature=self.settings.parameters.temperature.value,
            top_p=self.settings.parameters.top_p.value,
            top_k=self.settings.parameters.top_k.value,
        )

        session = Session(
            session_id=session_id,
            created_at=timestamp,
            purpose=purpose,
            background=background,
            roles=roles,
            multi_step_reasoning_enabled=multi_step_reasoning_enabled,
            token_count=token_count,
            hyperparameters=(
                hyperparameters
                if hyperparameters is not None
                else default_hyperparameters
            ),
            artifacts=artifacts or [],
            procedure=procedure,
        )

        return session

    def update_token_count(self, session_id: str, token_count: int):
        session = self._fetch_session(session_id)
        if session:
            session.token_count = token_count
            self.repository.save(session)

    def expire_old_tool_responses(self, session_id: str):
        """
        Expires the message content of old tool_responses to save tokens.
        """
        session = self._fetch_session(session_id)
        if session:
            from pipe.core.domains.turns import expire_old_tool_responses

            if expire_old_tool_responses(
                session.turns, self.settings.tool_response_expiration
            ):
                self._save_session(session)

    def build_compressor_instruction(
        self,
        session_id: str,
        policy: str,
        target_length: int,
        start_turn: int,
        end_turn: int,
    ) -> str:
        """Build the instruction for compressor session."""
        return (
            f"Compress session {session_id} from turn {start_turn} to {end_turn} "
            f"with policy '{policy}' and target length {target_length}"
        )

    def run_takt_for_compression(
        self,
        session_id: str,
        policy: str,
        target_length: int,
        start_turn: int,
        end_turn: int,
    ) -> dict[str, str]:
        """Create compressor session and run initial takt command."""
        import re
        import subprocess
        import sys

        # Build instruction
        instruction = self.build_compressor_instruction(
            session_id, policy, target_length, start_turn, end_turn
        )

        # Execute takt command
        command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--purpose",
            "Act as a compression agent to summarize the target session "
            "according to the specified request",
            "--background",
            "Responsible for compressing conversation history and creating "
            "summaries based on the specified policy and target length",
            "--roles",
            "roles/compressor.md",
            "--instruction",
            instruction,
        ]

        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.join(self.project_root, "src")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            env=env,
        )

        # Extract session ID from stderr
        match = re.search(r"New session created: (.+)", result.stderr)
        if match:
            compressor_session_id = match.group(1)
        else:
            raise RuntimeError("Failed to extract session ID from takt output")

        # Reload the session to get the summary
        session = self.get_session(compressor_session_id)
        if not session or not session.turns:
            raise ValueError("Session or turns not found after creation")

        # Find the last model_response
        last_model_response = None
        for turn in reversed(session.turns):
            if turn.type == "model_response":
                last_model_response = turn
                break

        summary = ""
        verifier_session_id = None
        if last_model_response:
            content = last_model_response.content
            # Extract summary after ## SUMMARY CONTENTS
            summary_start = content.find("## SUMMARY CONTENTS")
            if summary_start != -1:
                summary = content[summary_start + len("## SUMMARY CONTENTS") :].strip()

                # Extract Verifier Session ID
                verifier_id_start = summary.find("Verifier Session ID: ")
                if verifier_id_start == -1:
                    verifier_id_start = summary.find("検証セッションID: ")
                if verifier_id_start != -1:
                    verifier_line = summary[verifier_id_start:]
                    if "`" in verifier_line:
                        start = verifier_line.find("`") + 1
                        end = verifier_line.find("`", start)
                        verifier_session_id = verifier_line[start:end]
                    else:
                        parts = verifier_line.split()
                        if len(parts) > 3:
                            verifier_session_id = parts[3]

                    # Remove the Verifier Session ID line from summary
                    summary = summary[:verifier_id_start].strip()

        return {
            "session_id": compressor_session_id,
            "summary": summary,
            "verifier_session_id": verifier_session_id or "",
        }

    def approve_compression(self, compressor_session_id: str) -> None:
        """Approve the compression by running takt with approval instruction."""
        import subprocess
        import sys

        # Execute takt command on the compressor session with approval instruction
        approval_instruction = (
            "The user has approved the compression. "
            "Proceed with replacing the session turns using the "
            "replace_session_turns tool."
        )
        command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--session",
            compressor_session_id,
            "--instruction",
            approval_instruction,
        ]

        subprocess.run(
            command, capture_output=True, text=True, check=True, encoding="utf-8"
        )

        # The compressor agent will handle the replacement and cleanup
        # Also delete the compressor session after approval
        self.delete_session(compressor_session_id)

    def deny_compression(self, compressor_session_id: str) -> None:
        """Deny the compression and clean up the compressor session."""
        # Simply delete the compressor session
        self.delete_session(compressor_session_id)

    def replace_turn_range_with_summary(
        self, session_id: str, summary: str, start_index: int, end_index: int
    ) -> None:
        """Replace a range of turns with a summary."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if (
            start_index < 0
            or end_index >= len(session.turns)
            or start_index > end_index
        ):
            raise ValueError("Invalid turn range")

        # Create a compressed history turn
        from pipe.core.models.turn import CompressedHistoryTurn
        from pipe.core.utils.datetime import get_current_timestamp

        compressed_turn = CompressedHistoryTurn(
            type="compressed_history",
            content=summary,
            original_turns_range=[start_index + 1, end_index + 1],  # 1-based
            timestamp=get_current_timestamp(),
        )

        # Replace the range with the compressed turn
        session.turns = (
            session.turns[:start_index]
            + [compressed_turn]
            + session.turns[end_index + 1 :]
        )

        # Save the session
        self.repository.save(session)
