"""Unit tests for SessionArtifactService."""

import os
from unittest.mock import MagicMock

import pytest
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_artifact_service import SessionArtifactService

from tests.factories.models.artifact_factory import ArtifactFactory
from tests.factories.models.session_factory import SessionFactory


@pytest.fixture
def mock_repository() -> MagicMock:
    """Create a mock SessionRepository."""
    return MagicMock(spec=SessionRepository)


@pytest.fixture
def service(
    tmp_path: os.PathLike, mock_repository: MagicMock
) -> SessionArtifactService:
    """Create a SessionArtifactService instance with a temporary project root."""
    return SessionArtifactService(
        project_root=str(tmp_path), repository=mock_repository
    )


class TestSessionArtifactService:
    """Tests for SessionArtifactService."""

    def test_init(self, tmp_path: os.PathLike, mock_repository: MagicMock) -> None:
        """Test initialization of SessionArtifactService."""
        project_root = str(tmp_path)
        service = SessionArtifactService(
            project_root=project_root, repository=mock_repository
        )
        assert service.project_root == project_root
        assert service.repository == mock_repository

    def test_update_artifacts_session_not_found(
        self, service: SessionArtifactService, mock_repository: MagicMock
    ) -> None:
        """Test update_artifacts when the session is not found."""
        session_id = "non-existent"
        mock_repository.find.return_value = None
        artifacts = ArtifactFactory.create_batch(2)

        service.update_artifacts(session_id, artifacts)

        mock_repository.find.assert_called_once_with(session_id)
        mock_repository.save.assert_not_called()

    def test_update_artifacts_with_contents(
        self,
        service: SessionArtifactService,
        mock_repository: MagicMock,
        tmp_path: os.PathLike,
    ) -> None:
        """Test update_artifacts when artifacts have contents."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session

        artifacts = [
            ArtifactFactory.create(path="dir1/file1.txt", contents="content1"),
            ArtifactFactory.create(path="file2.txt", contents="content2"),
        ]

        service.update_artifacts(session_id, artifacts)

        # Verify files were created
        file1_path = os.path.join(str(tmp_path), "dir1/file1.txt")
        file2_path = os.path.join(str(tmp_path), "file2.txt")

        assert os.path.exists(file1_path)
        assert os.path.exists(file2_path)

        with open(file1_path, encoding="utf-8") as f:
            assert f.read() == "content1"
        with open(file2_path, encoding="utf-8") as f:
            assert f.read() == "content2"

        # Verify session was updated and saved
        assert session.artifacts == ["dir1/file1.txt", "file2.txt"]
        mock_repository.save.assert_called_once_with(session)

    def test_update_artifacts_without_contents(
        self,
        service: SessionArtifactService,
        mock_repository: MagicMock,
        tmp_path: os.PathLike,
    ) -> None:
        """Test update_artifacts when artifacts do not have contents."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session

        # Artifacts with None contents
        artifacts = [
            ArtifactFactory.create(path="existing_file.txt", contents=None),
        ]

        service.update_artifacts(session_id, artifacts)

        # Verify no file was created/overwritten (though it shouldn't be if contents is None)
        file_path = os.path.join(str(tmp_path), "existing_file.txt")
        assert not os.path.exists(file_path)

        # Verify session was updated and saved
        assert session.artifacts == ["existing_file.txt"]
        mock_repository.save.assert_called_once_with(session)

    def test_update_artifacts_mixed(
        self,
        service: SessionArtifactService,
        mock_repository: MagicMock,
        tmp_path: os.PathLike,
    ) -> None:
        """Test update_artifacts with a mix of artifacts with and without contents."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session

        artifacts = [
            ArtifactFactory.create(path="new_file.txt", contents="new content"),
            ArtifactFactory.create(path="reference_only.txt", contents=None),
        ]

        service.update_artifacts(session_id, artifacts)

        # Verify only the one with contents was created
        new_file_path = os.path.join(str(tmp_path), "new_file.txt")
        ref_file_path = os.path.join(str(tmp_path), "reference_only.txt")

        assert os.path.exists(new_file_path)
        assert not os.path.exists(ref_file_path)

        # Verify session was updated with both paths
        assert session.artifacts == ["new_file.txt", "reference_only.txt"]
        mock_repository.save.assert_called_once_with(session)
