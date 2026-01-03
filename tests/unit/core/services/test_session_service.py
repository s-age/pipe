"""Unit tests for SessionService."""

from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from pipe.core.models.args import TaktArgs
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_service import SessionService

from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.settings_factory import create_test_settings


@pytest.fixture
def mock_repository():
    """Create a mock SessionRepository."""
    return MagicMock(spec=SessionRepository)


@pytest.fixture
def mock_settings():
    """Create test settings."""
    return create_test_settings(timezone="Asia/Tokyo", reference_ttl=3)


@pytest.fixture
def mock_file_indexer():
    """Create a mock FileIndexerService."""
    return MagicMock()


@pytest.fixture
def service(mock_settings, mock_repository, mock_file_indexer):
    """Create a SessionService instance."""
    return SessionService(
        project_root="/mock/root",
        settings=mock_settings,
        repository=mock_repository,
        file_indexer_service=mock_file_indexer,
    )


class TestSessionServiceInit:
    """Tests for SessionService.__init__."""

    def test_init_valid_timezone(self, mock_settings, mock_repository):
        """Test initialization with a valid timezone."""
        service = SessionService("/root", mock_settings, mock_repository)
        assert service.timezone_obj.key == "Asia/Tokyo"

    def test_init_invalid_timezone(self, mock_repository, capsys):
        """Test initialization with an invalid timezone falls back to UTC."""
        settings = create_test_settings(timezone="Invalid/Timezone")
        service = SessionService("/root", settings, mock_repository)
        assert service.timezone_obj.key == "UTC"
        captured = capsys.readouterr()
        assert (
            "Warning: Timezone 'Invalid/Timezone' not found. Using UTC." in captured.err
        )


class TestSessionServiceHistoryManager:
    """Tests for SessionService.set_history_manager."""

    def test_set_history_manager(self, service):
        """Test setting the history manager."""
        mock_manager = MagicMock()
        service.set_history_manager(mock_manager)
        assert service.history_manager == mock_manager


class TestSessionServiceGetters:
    """Tests for SessionService getter methods."""

    def test_get_session(self, service, mock_repository):
        """Test get_session calls repository.find."""
        expected_session = SessionFactory.create()
        mock_repository.find.return_value = expected_session

        result = service.get_session("test-id")

        assert result == expected_session
        mock_repository.find.assert_called_once_with("test-id")

    def test_list_sessions(self, service, mock_repository):
        """Test list_sessions calls repository.load_index."""
        mock_index = MagicMock()
        mock_repository.load_index.return_value = mock_index

        result = service.list_sessions()

        assert result == mock_index
        mock_repository.load_index.assert_called_once()

    def test_get_session_path(self, service, mock_repository):
        """Test _get_session_path calls repository._get_path_for_id."""
        mock_repository._get_path_for_id.return_value = "/path/to/session"

        result = service._get_session_path("test-id")

        assert result == "/path/to/session"
        mock_repository._get_path_for_id.assert_called_once_with("test-id")


class TestSessionServicePrepare:
    """Tests for SessionService.prepare."""

    def test_prepare_existing_session(self, service, mock_repository):
        """Test prepare with an existing session ID."""
        existing_session = SessionFactory.create(session_id="existing-id")
        mock_repository.find.return_value = existing_session
        args = TaktArgs(session="existing-id", instruction="test instruction")

        service.prepare(args)

        assert service.current_session == existing_session
        assert service.current_session_id == "existing-id"
        assert service.current_instruction == "test instruction"
        mock_repository.find.assert_called_once_with("existing-id")
        mock_repository.save.assert_called_once_with(existing_session)

    def test_prepare_nonexistent_session_raises_error(self, service, mock_repository):
        """Test prepare raises FileNotFoundError for non-existent session."""
        mock_repository.find.return_value = None
        args = TaktArgs(session="nonexistent")

        with pytest.raises(
            FileNotFoundError, match="Session with ID 'nonexistent' not found"
        ):
            service.prepare(args)

    @freeze_time("2025-01-01 12:00:00")
    def test_prepare_new_session(self, service, mock_repository):
        """Test prepare creates a new session when no ID is provided."""
        args = TaktArgs(
            purpose="New Purpose",
            background="New Background",
            instruction="First instruction",
        )

        service.prepare(args)

        assert service.current_session is not None
        assert service.current_session.purpose == "New Purpose"
        assert service.current_session.background == "New Background"
        assert service.current_instruction == "First instruction"
        mock_repository.save.assert_called_once()

    def test_prepare_new_session_missing_args_raises_error(self, service):
        """Test prepare raises ValueError when purpose/background are missing for new session."""
        args = TaktArgs(instruction="test")

        with pytest.raises(
            ValueError, match="A new session requires --purpose and --background"
        ):
            service.prepare(args)

    @patch("pipe.core.domains.references.add_reference")
    def test_prepare_with_references(self, mock_add_ref, service, mock_repository):
        """Test prepare handles references and persistent references."""
        args = TaktArgs(
            purpose="P",
            background="B",
            references=["file1.py", "file2.py"],
            references_persist=["file1.py", "file3.py"],
        )

        service.prepare(args)

        # all_references | persistent_references = {file1.py, file2.py, file3.py}
        assert mock_add_ref.call_count == 3

        # Verify calls (order might vary due to set)
        paths_called = [call.args[1] for call in mock_add_ref.call_args_list]
        assert set(paths_called) == {"file1.py", "file2.py", "file3.py"}

        # Verify persistence for file1.py
        file1_call = next(
            c for c in mock_add_ref.call_args_list if c.args[1] == "file1.py"
        )
        assert file1_call.kwargs["persist"] is True

    def test_prepare_dry_run(self, service, mock_repository):
        """Test prepare does not save session in dry run mode."""
        args = TaktArgs(purpose="P", background="B")

        service.prepare(args, is_dry_run=True)

        mock_repository.save.assert_not_called()


class TestSessionServiceCreateNewSession:
    """Tests for SessionService.create_new_session."""

    @freeze_time("2025-01-01 12:00:00")
    def test_create_new_session_success(
        self, service, mock_repository, mock_file_indexer
    ):
        """Test successful creation of a new session."""
        session = service.create_new_session(
            purpose="Test Purpose",
            background="Test Background",
            roles=["Role1"],
        )

        assert session.purpose == "Test Purpose"
        assert session.background == "Test Background"
        assert session.roles == ["Role1"]
        mock_repository.save.assert_called_once_with(session)
        mock_file_indexer.create_index.assert_called_once()

    def test_create_new_session_index_failure_handled(
        self, service, mock_file_indexer, capsys
    ):
        """Test that index rebuild failure is handled gracefully."""
        mock_file_indexer.create_index.side_effect = Exception("Index error")

        service.create_new_session(purpose="P", background="B", roles=[])

        captured = capsys.readouterr()
        assert "Warning: Failed to rebuild Whoosh index: Index error" in captured.err


class TestSessionServiceDelete:
    """Tests for SessionService deletion methods."""

    def test_delete_session(self, service, mock_repository):
        """Test delete_session calls repository.delete."""
        service.delete_session("test-id")
        mock_repository.delete.assert_called_once_with("test-id")

    def test_delete_sessions_bulk(self, service, mock_repository):
        """Test bulk deletion of sessions."""
        mock_repository.delete.side_effect = [None, Exception("Fail"), None]

        count = service.delete_sessions(["id1", "id2", "id3"])

        assert count == 2
        assert mock_repository.delete.call_count == 3


class TestSessionServiceInternal:
    """Tests for internal methods of SessionService."""

    def test_generate_hash(self, service):
        """Test _generate_hash produces consistent SHA256 hash."""
        content = "test content"
        expected_hash = (
            "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
        )
        assert service._generate_hash(content) == expected_hash

    @freeze_time("2025-01-01 12:00:00")
    def test_create_session_object_with_parent(self, service, mock_repository):
        """Test _create_session_object with a parent session."""
        parent_session = SessionFactory.create(session_id="parent-id")
        mock_repository.find.return_value = parent_session

        session = service._create_session_object(
            purpose="Child Purpose",
            background="Child Background",
            roles=[],
            parent_id="parent-id",
        )

        assert session.session_id.startswith("parent-id/")
        mock_repository.find.assert_called_once_with("parent-id")

    def test_create_session_object_parent_not_found(self, service, mock_repository):
        """Test _create_session_object raises FileNotFoundError if parent not found."""
        mock_repository.find.return_value = None

        with pytest.raises(
            FileNotFoundError, match="Parent session with ID 'nonexistent' not found"
        ):
            service._create_session_object(
                purpose="P", background="B", roles=[], parent_id="nonexistent"
            )

    @freeze_time("2025-01-01 12:00:00")
    def test_create_session_object_default_hyperparameters(
        self, service, mock_settings
    ):
        """Test _create_session_object uses default hyperparameters from settings."""
        session = service._create_session_object(purpose="P", background="B", roles=[])

        assert (
            session.hyperparameters.temperature
            == mock_settings.parameters.temperature.value
        )
        assert session.hyperparameters.top_p == mock_settings.parameters.top_p.value
        assert session.hyperparameters.top_k == mock_settings.parameters.top_k.value

    @freeze_time("2025-01-01 12:00:00")
    def test_create_session_object_custom_hyperparameters(self, service):
        """Test _create_session_object uses provided custom hyperparameters."""
        custom_hp = Hyperparameters(temperature=0.9, top_p=0.8, top_k=50)

        session = service._create_session_object(
            purpose="P", background="B", roles=[], hyperparameters=custom_hp
        )

        assert session.hyperparameters == custom_hp
