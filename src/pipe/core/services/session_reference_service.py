"""Service for managing session references."""

import os
import sys

from pipe.core.collections.references import ReferenceCollection
from pipe.core.domains.references import (
    add_reference,
    decrement_all_references_ttl,
    toggle_reference_disabled,
    update_reference_persist,
    update_reference_ttl,
)
from pipe.core.models.reference import Reference
from pipe.core.services.session_service import SessionService


class SessionReferenceService:
    """Handles all reference-related operations for sessions."""

    def __init__(self, project_root: str, session_service: SessionService):
        self.project_root = project_root
        self.session_service = session_service

    def update_references(self, session_id: str, references: list[Reference]):
        """Updates session references with typed Reference objects."""
        session = self.session_service._fetch_session(session_id)
        if session:
            session.references = ReferenceCollection(references)
            self.session_service._save_session(session)

    def add_reference_to_session(self, session_id: str, file_path: str):
        session = self.session_service._fetch_session(session_id)
        if not session:
            return

        abs_path = os.path.abspath(os.path.join(self.project_root, file_path))
        if not os.path.isfile(abs_path):
            print(f"Warning: Path is not a file, skipping: {abs_path}", file=sys.stderr)
            return

        add_reference(session.references, file_path, session.references.default_ttl)
        self.session_service._save_session(session)

    def update_reference_ttl_in_session(
        self, session_id: str, file_path: str, new_ttl: int
    ):
        session = self.session_service._fetch_session(session_id)
        if not session:
            return

        update_reference_ttl(session.references, file_path, new_ttl)
        self.session_service._save_session(session)

    def update_reference_ttl_by_index(
        self, session_id: str, reference_index: int, new_ttl: int
    ):
        """Update reference TTL by index with validation.

        Args:
            session_id: Session ID
            reference_index: Zero-based reference index
            new_ttl: New TTL value

        Raises:
            FileNotFoundError: If session not found
            IndexError: If reference index out of range
        """
        session = self.session_service._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session {session_id} not found.")

        # Delegate validation and operation to ReferenceCollection
        session.references.update_ttl_by_index(reference_index, new_ttl)
        self.session_service._save_session(session)

    def update_reference_persist_in_session(
        self, session_id: str, file_path: str, new_persist_state: bool
    ):
        session = self.session_service._fetch_session(session_id)
        if not session:
            return

        update_reference_persist(session.references, file_path, new_persist_state)
        self.session_service._save_session(session)

    def update_reference_persist_by_index(
        self, session_id: str, reference_index: int, new_persist_state: bool
    ):
        """Update reference persist state by index with validation.

        Args:
            session_id: Session ID
            reference_index: Zero-based reference index
            new_persist_state: New persist state

        Raises:
            FileNotFoundError: If session not found
            IndexError: If reference index out of range
        """
        session = self.session_service._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session {session_id} not found.")

        # Delegate validation and operation to ReferenceCollection
        session.references.update_persist_by_index(reference_index, new_persist_state)
        self.session_service._save_session(session)

    def toggle_reference_disabled_in_session(self, session_id: str, file_path: str):
        session = self.session_service._fetch_session(session_id)
        if not session:
            return

        toggle_reference_disabled(session.references, file_path)
        self.session_service._save_session(session)

    def toggle_reference_disabled_by_index(
        self, session_id: str, reference_index: int
    ) -> bool:
        """Toggle reference disabled state by index with validation.

        Args:
            session_id: Session ID
            reference_index: Zero-based reference index

        Returns:
            New disabled state after toggle

        Raises:
            FileNotFoundError: If session not found
            IndexError: If reference index out of range
        """
        session = self.session_service._fetch_session(session_id)
        if not session:
            raise FileNotFoundError(f"Session {session_id} not found.")

        # Delegate validation and operation to ReferenceCollection
        new_disabled_state = session.references.toggle_disabled_by_index(
            reference_index
        )
        self.session_service._save_session(session)
        return new_disabled_state

    def decrement_all_references_ttl_in_session(self, session_id: str):
        session = self.session_service._fetch_session(session_id)
        if not session:
            return

        decrement_all_references_ttl(session.references)
        self.session_service._save_session(session)

    def add_multiple_references(self, session_id: str, file_paths: list[str]):
        session = self.session_service._fetch_session(session_id)
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
        self.session_service._save_session(session)
