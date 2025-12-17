"""
Manages the overall session, excluding conversation_history.
"""

import hashlib
import json
import sys
import zoneinfo
from typing import TYPE_CHECKING

from pipe.core.models.args import TaktArgs
from pipe.core.models.artifact import Artifact
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import Session
from pipe.core.models.session_index import SessionIndex
from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.utils.datetime import get_current_timestamp

if TYPE_CHECKING:
    from pipe.core.services.file_indexer_service import FileIndexerService


class SessionService:
    def __init__(
        self,
        project_root: str,
        settings: Settings,
        repository: SessionRepository,
        file_indexer_service: "FileIndexerService | None" = None,
    ):
        self.project_root = project_root
        self.settings = settings
        self.repository = repository
        self.file_indexer_service = file_indexer_service
        self.current_session: Session | None = None
        self.current_session_id: str | None = None
        self.current_instruction: str | None = None

        self.history_manager = None  # Will be set by ServiceFactory

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

    def set_history_manager(self, history_manager):
        """Set the history manager for tool compatibility."""
        self.history_manager = history_manager

    def get_session(self, session_id: str) -> Session | None:
        """Loads a specific session."""
        return self.repository.find(session_id)

    def list_sessions(self) -> SessionIndex:
        """Loads and returns the latest session index from the repository."""
        return self.repository.load_index()

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

            # Note: user_task turn will be added by start_transaction() in dispatcher
            # Do not add it here to avoid duplication
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

            # Note: first user_task turn will be added by start_transaction()
            # in dispatcher. Do not add it here to avoid duplication

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

        if not is_dry_run:
            self.repository.save(session)

        self.current_session = session
        self.current_session_id = session.session_id
        self.current_instruction = args.instruction

    def _get_session_path(self, session_id: str) -> str:
        # This logic is now in the repository
        return self.repository._get_path_for_id(session_id)

    def _get_session_lock_path(self, session_id: str) -> str:
        return f"{self._get_session_path(session_id)}.lock"

    def create_new_session(
        self,
        purpose: str,
        background: str,
        roles: list[str],
        multi_step_reasoning_enabled: bool = False,
        token_count: int = 0,
        hyperparameters: Hyperparameters | None = None,
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

        # Rebuild Whoosh index when creating new session
        if self.file_indexer_service:
            try:
                self.file_indexer_service.create_index()
            except Exception as e:
                print(f"Warning: Failed to rebuild Whoosh index: {e}", file=sys.stderr)

        return session

    def delete_session(self, session_id: str):
        """Delete a session by ID.

        Args:
            session_id: Session ID to delete
        """
        self.repository.delete(session_id)

    def delete_sessions(self, session_ids: list[str]) -> int:
        """
        Bulk delete multiple sessions.

        Args:
            session_ids: List of session IDs to delete

        Returns:
            Number of successfully deleted sessions
        """
        deleted_count = 0
        for session_id in session_ids:
            try:
                self.repository.delete(session_id)
                deleted_count += 1
            except Exception:
                # Continue with other deletions even if one fails
                continue
        return deleted_count

    def _generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _create_session_object(
        self,
        purpose: str,
        background: str,
        roles: list[str],
        multi_step_reasoning_enabled: bool = False,
        token_count: int = 0,
        hyperparameters: Hyperparameters | None = None,
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
