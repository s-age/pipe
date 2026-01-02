"""Unit tests for SessionReferenceService."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.collections.references import ReferenceCollection
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_reference_service import SessionReferenceService

from tests.factories.models.reference_factory import ReferenceFactory
from tests.factories.models.session_factory import SessionFactory


@pytest.fixture
def mock_repository():
    """Create a mock SessionRepository."""
    return MagicMock(spec=SessionRepository)


@pytest.fixture
def service(mock_repository):
    """Create a SessionReferenceService instance."""
    return SessionReferenceService(project_root="/app", repository=mock_repository)


class TestSessionReferenceServiceInit:
    """Tests for SessionReferenceService.__init__."""

    def test_init(self, mock_repository):
        """Test initialization."""
        service = SessionReferenceService(
            project_root="/app", repository=mock_repository
        )
        assert service.project_root == "/app"
        assert service.repository == mock_repository


class TestSessionReferenceServiceUpdateReferences:
    """Tests for SessionReferenceService.update_references."""

    def test_update_references_success(self, service, mock_repository):
        """Test updating references for an existing session."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session
        references = ReferenceFactory.create_batch(2)

        service.update_references(session_id, references)

        assert isinstance(session.references, ReferenceCollection)
        assert len(session.references) == 2
        mock_repository.find.assert_called_once_with(session_id)
        mock_repository.save.assert_called_once_with(session)

    def test_update_references_session_not_found(self, service, mock_repository):
        """Test updating references for a non-existent session."""
        session_id = "non-existent"
        mock_repository.find.return_value = None
        references = ReferenceFactory.create_batch(2)

        service.update_references(session_id, references)

        mock_repository.find.assert_called_once_with(session_id)
        mock_repository.save.assert_not_called()


class TestSessionReferenceServiceAddReferenceToSession:
    """Tests for SessionReferenceService.add_reference_to_session."""

    @patch("pipe.core.services.session_reference_service.os.path.isfile")
    @patch("pipe.core.services.session_reference_service.add_reference")
    def test_add_reference_success(
        self, mock_add_ref, mock_isfile, service, mock_repository
    ):
        """Test adding a reference to an existing session."""
        session_id = "test-session"
        file_path = "test.py"
        session = SessionFactory.create(session_id=session_id)
        session.references = MagicMock(spec=ReferenceCollection)
        session.references.default_ttl = 3
        mock_repository.find.return_value = session
        mock_isfile.return_value = True

        service.add_reference_to_session(session_id, file_path)

        mock_repository.find.assert_called_once_with(session_id)
        mock_isfile.assert_called_once()
        mock_add_ref.assert_called_once_with(session.references, file_path, 3)
        mock_repository.save.assert_called_once_with(session)

    def test_add_reference_session_not_found(self, service, mock_repository):
        """Test adding a reference to a non-existent session."""
        session_id = "non-existent"
        mock_repository.find.return_value = None

        service.add_reference_to_session(session_id, "test.py")

        mock_repository.find.assert_called_once_with(session_id)
        mock_repository.save.assert_not_called()

    @patch("pipe.core.services.session_reference_service.os.path.isfile")
    def test_add_reference_not_a_file(self, mock_isfile, service, mock_repository):
        """Test adding a reference that is not a file."""
        session_id = "test-session"
        file_path = "dir/"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session
        mock_isfile.return_value = False

        service.add_reference_to_session(session_id, file_path)

        mock_repository.find.assert_called_once_with(session_id)
        mock_repository.save.assert_not_called()


class TestSessionReferenceServiceUpdateReferenceTtl:
    """Tests for SessionReferenceService.update_reference_ttl_in_session."""

    @patch("pipe.core.services.session_reference_service.update_reference_ttl")
    def test_update_ttl_success(self, mock_update_ttl, service, mock_repository):
        """Test updating reference TTL."""
        session_id = "test-session"
        file_path = "test.py"
        new_ttl = 5
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session

        service.update_reference_ttl_in_session(session_id, file_path, new_ttl)

        mock_repository.find.assert_called_once_with(session_id)
        mock_update_ttl.assert_called_once_with(session.references, file_path, new_ttl)
        mock_repository.save.assert_called_once_with(session)

    def test_update_ttl_session_not_found(self, service, mock_repository):
        """Test updating TTL for a non-existent session."""
        mock_repository.find.return_value = None
        service.update_reference_ttl_in_session("non-existent", "test.py", 5)
        mock_repository.save.assert_not_called()


class TestSessionReferenceServiceUpdateReferenceTtlByIndex:
    """Tests for SessionReferenceService.update_reference_ttl_by_index."""

    def test_update_ttl_by_index_success(self, service, mock_repository):
        """Test updating reference TTL by index."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        session.references = MagicMock(spec=ReferenceCollection)
        mock_repository.find.return_value = session

        service.update_reference_ttl_by_index(session_id, 0, 5)

        mock_repository.find.assert_called_once_with(session_id)
        session.references.update_ttl_by_index.assert_called_once_with(0, 5)
        mock_repository.save.assert_called_once_with(session)

    def test_update_ttl_by_index_session_not_found(self, service, mock_repository):
        """Test updating TTL by index for a non-existent session."""
        mock_repository.find.return_value = None
        with pytest.raises(FileNotFoundError, match="Session non-existent not found"):
            service.update_reference_ttl_by_index("non-existent", 0, 5)


class TestSessionReferenceServiceUpdateReferencePersist:
    """Tests for SessionReferenceService.update_reference_persist_in_session."""

    @patch("pipe.core.services.session_reference_service.update_reference_persist")
    def test_update_persist_success(
        self, mock_update_persist, service, mock_repository
    ):
        """Test updating reference persist state."""
        session_id = "test-session"
        file_path = "test.py"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session

        service.update_reference_persist_in_session(session_id, file_path, True)

        mock_repository.find.assert_called_once_with(session_id)
        mock_update_persist.assert_called_once_with(session.references, file_path, True)
        mock_repository.save.assert_called_once_with(session)

    def test_update_persist_session_not_found(self, service, mock_repository):
        """Test updating persist for a non-existent session."""
        mock_repository.find.return_value = None
        service.update_reference_persist_in_session("non-existent", "test.py", True)
        mock_repository.save.assert_not_called()


class TestSessionReferenceServiceUpdateReferencePersistByIndex:
    """Tests for SessionReferenceService.update_reference_persist_by_index."""

    def test_update_persist_by_index_success(self, service, mock_repository):
        """Test updating reference persist state by index."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        session.references = MagicMock(spec=ReferenceCollection)
        mock_repository.find.return_value = session

        service.update_reference_persist_by_index(session_id, 0, True)

        mock_repository.find.assert_called_once_with(session_id)
        session.references.update_persist_by_index.assert_called_once_with(0, True)
        mock_repository.save.assert_called_once_with(session)

    def test_update_persist_by_index_session_not_found(self, service, mock_repository):
        """Test updating persist by index for a non-existent session."""
        mock_repository.find.return_value = None
        with pytest.raises(FileNotFoundError, match="Session non-existent not found"):
            service.update_reference_persist_by_index("non-existent", 0, True)


class TestSessionReferenceServiceToggleReferenceDisabled:
    """Tests for SessionReferenceService.toggle_reference_disabled_in_session."""

    @patch("pipe.core.services.session_reference_service.toggle_reference_disabled")
    def test_toggle_disabled_success(self, mock_toggle, service, mock_repository):
        """Test toggling reference disabled state."""
        session_id = "test-session"
        file_path = "test.py"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session

        service.toggle_reference_disabled_in_session(session_id, file_path)

        mock_repository.find.assert_called_once_with(session_id)
        mock_toggle.assert_called_once_with(session.references, file_path)
        mock_repository.save.assert_called_once_with(session)

    def test_toggle_disabled_session_not_found(self, service, mock_repository):
        """Test toggling disabled for a non-existent session."""
        mock_repository.find.return_value = None
        service.toggle_reference_disabled_in_session("non-existent", "test.py")
        mock_repository.save.assert_not_called()


class TestSessionReferenceServiceToggleReferenceDisabledByIndex:
    """Tests for SessionReferenceService.toggle_reference_disabled_by_index."""

    def test_toggle_disabled_by_index_success(self, service, mock_repository):
        """Test toggling reference disabled state by index."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        session.references = MagicMock(spec=ReferenceCollection)
        session.references.toggle_disabled_by_index.return_value = True
        mock_repository.find.return_value = session

        result = service.toggle_reference_disabled_by_index(session_id, 0)

        assert result is True
        mock_repository.find.assert_called_once_with(session_id)
        session.references.toggle_disabled_by_index.assert_called_once_with(0)
        mock_repository.save.assert_called_once_with(session)

    def test_toggle_disabled_by_index_session_not_found(self, service, mock_repository):
        """Test toggling disabled by index for a non-existent session."""
        mock_repository.find.return_value = None
        with pytest.raises(FileNotFoundError, match="Session non-existent not found"):
            service.toggle_reference_disabled_by_index("non-existent", 0)


class TestSessionReferenceServiceDecrementAllReferencesTtl:
    """Tests for SessionReferenceService.decrement_all_references_ttl_in_session."""

    @patch("pipe.core.services.session_reference_service.decrement_all_references_ttl")
    def test_decrement_all_ttl_success(self, mock_decrement, service, mock_repository):
        """Test decrementing all references TTL."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session

        service.decrement_all_references_ttl_in_session(session_id)

        mock_repository.find.assert_called_once_with(session_id)
        mock_decrement.assert_called_once_with(session.references)
        mock_repository.save.assert_called_once_with(session)

    def test_decrement_all_ttl_session_not_found(self, service, mock_repository):
        """Test decrementing all TTL for a non-existent session."""
        mock_repository.find.return_value = None
        service.decrement_all_references_ttl_in_session("non-existent")
        mock_repository.save.assert_not_called()


class TestSessionReferenceServiceAddMultipleReferences:
    """Tests for SessionReferenceService.add_multiple_references."""

    @patch("pipe.core.services.session_reference_service.os.path.isfile")
    @patch("pipe.core.services.session_reference_service.add_reference")
    def test_add_multiple_references_success(
        self, mock_add_ref, mock_isfile, service, mock_repository
    ):
        """Test adding multiple references."""
        session_id = "test-session"
        file_paths = ["test1.py", "test2.py"]
        session = SessionFactory.create(session_id=session_id)
        session.references = MagicMock(spec=ReferenceCollection)
        session.references.default_ttl = 3
        mock_repository.find.return_value = session
        mock_isfile.return_value = True

        service.add_multiple_references(session_id, file_paths)

        mock_repository.find.assert_called_once_with(session_id)
        assert mock_isfile.call_count == 2
        assert mock_add_ref.call_count == 2
        mock_add_ref.assert_any_call(session.references, "test1.py", 3)
        mock_add_ref.assert_any_call(session.references, "test2.py", 3)
        mock_repository.save.assert_called_once_with(session)

    def test_add_multiple_references_session_not_found(self, service, mock_repository):
        """Test adding multiple references to a non-existent session."""
        mock_repository.find.return_value = None
        service.add_multiple_references("non-existent", ["test.py"])
        mock_repository.save.assert_not_called()

    @patch("pipe.core.services.session_reference_service.os.path.isfile")
    @patch("pipe.core.services.session_reference_service.add_reference")
    def test_add_multiple_references_some_not_files(
        self, mock_add_ref, mock_isfile, service, mock_repository
    ):
        """Test adding multiple references where some are not files."""
        session_id = "test-session"
        file_paths = ["test1.py", "dir/"]
        session = SessionFactory.create(session_id=session_id)
        session.references = MagicMock(spec=ReferenceCollection)
        session.references.default_ttl = 3
        mock_repository.find.return_value = session
        mock_isfile.side_effect = [True, False]

        service.add_multiple_references(session_id, file_paths)

        mock_repository.find.assert_called_once_with(session_id)
        assert mock_isfile.call_count == 2
        mock_add_ref.assert_called_once_with(session.references, "test1.py", 3)
        mock_repository.save.assert_called_once_with(session)
