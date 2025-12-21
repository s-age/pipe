"""Service for managing session artifacts."""

import os

from pipe.core.models.artifact import Artifact
from pipe.core.repositories.session_repository import SessionRepository


class SessionArtifactService:
    """Handles all artifact-related operations for sessions."""

    def __init__(self, project_root: str, repository: SessionRepository):
        self.project_root = project_root
        self.repository = repository

    def update_artifacts(self, session_id: str, artifacts: list[Artifact]):
        """Updates session artifacts with typed Artifact objects.

        For each artifact:
        - If contents is provided, writes it to the file at the specified path
        - Updates the session's artifacts list with the paths

        Args:
            session_id: Session ID to update
            artifacts: List of Artifact objects with path and optional contents
        """
        session = self.repository.find(session_id)
        if not session:
            return

        # Write artifact contents to files if provided
        for artifact in artifacts:
            if artifact.contents is not None:
                abs_path = os.path.abspath(
                    os.path.join(self.project_root, artifact.path)
                )
                # Ensure directory exists
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                # Write contents to file
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(artifact.contents)

        # Update session's artifacts list with paths
        session.artifacts = [artifact.path for artifact in artifacts]
        self.repository.save(session)
