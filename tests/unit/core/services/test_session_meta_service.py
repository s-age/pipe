"""Unit tests for SessionMetaService."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.domains.gemini_cache_manager import GeminiCacheManager
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import SessionMetaUpdate
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_meta_service import SessionMetaService

from tests.factories.models.session_factory import SessionFactory


@pytest.fixture
def mock_repository():
    """Create a mock SessionRepository."""
    return MagicMock(spec=SessionRepository)


@pytest.fixture
def mock_cache_manager():
    """Create a mock GeminiCacheManager."""
    return MagicMock(spec=GeminiCacheManager)


@pytest.fixture
def service(mock_repository):
    """Create a SessionMetaService instance with mocked repository."""
    return SessionMetaService(repository=mock_repository)


class TestSessionMetaServiceEditSessionMeta:
    """Tests for edit_session_meta method."""

    def test_edit_session_meta_success(self, service, mock_repository):
        """Test editing session metadata successfully."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id, purpose="Old Purpose")
        mock_repository.find.return_value = session

        update_data = SessionMetaUpdate(
            purpose="New Purpose", background="New Background"
        )
        service.edit_session_meta(session_id, update_data)

        assert session.purpose == "New Purpose"
        assert session.background == "New Background"
        mock_repository.backup.assert_called_once_with(session)
        mock_repository.save.assert_called_once_with(session)

    def test_edit_session_meta_with_cache_manager(
        self, mock_repository, mock_cache_manager
    ):
        """Test editing session metadata with cache manager present."""
        service = SessionMetaService(
            repository=mock_repository, cache_manager=mock_cache_manager
        )
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id, cached_turn_count=5)
        mock_repository.find.return_value = session

        update_data = SessionMetaUpdate(purpose="New Purpose")
        service.edit_session_meta(session_id, update_data)

        assert session.purpose == "New Purpose"
        assert session.cached_turn_count == 0
        mock_cache_manager.delete_cache_by_session_id.assert_called_once_with(
            session_id
        )
        # save is called twice: once after meta update, once after cached_turn_count reset
        assert mock_repository.save.call_count == 2

    def test_edit_session_meta_not_found(self, service, mock_repository):
        """Test editing session metadata when session is not found."""
        session_id = "non-existent"
        mock_repository.find.return_value = None

        update_data = SessionMetaUpdate(purpose="New Purpose")
        service.edit_session_meta(session_id, update_data)

        mock_repository.backup.assert_not_called()
        mock_repository.save.assert_not_called()


class TestSessionMetaServiceUpdateHyperparameters:
    """Tests for update_hyperparameters method."""

    @patch("pipe.core.services.session_meta_service.merge_hyperparameters")
    def test_update_hyperparameters_success(self, mock_merge, service, mock_repository):
        """Test updating hyperparameters successfully."""
        session_id = "test-session"
        initial_params = Hyperparameters(temperature=0.5)
        session = SessionFactory.create(
            session_id=session_id, hyperparameters=initial_params
        )
        mock_repository.find.return_value = session

        new_params = Hyperparameters(temperature=0.7)
        merged_params = Hyperparameters(temperature=0.7, top_p=0.9)
        mock_merge.return_value = merged_params

        result = service.update_hyperparameters(session_id, new_params)

        assert result.hyperparameters == merged_params
        mock_merge.assert_called_once_with(initial_params, new_params)
        mock_repository.save.assert_called_once_with(session)

    def test_update_hyperparameters_not_found(self, service, mock_repository):
        """Test updating hyperparameters when session is not found."""
        session_id = "non-existent"
        mock_repository.find.return_value = None

        new_params = Hyperparameters(temperature=0.7)
        with pytest.raises(FileNotFoundError, match=f"Session {session_id} not found"):
            service.update_hyperparameters(session_id, new_params)


class TestSessionMetaServiceUpdateTokenCount:
    """Tests for update_token_count method."""

    def test_update_token_count_success(self, service, mock_repository):
        """Test updating token count successfully."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id, token_count=100)
        mock_repository.find.return_value = session

        service.update_token_count(session_id, 200)

        assert session.token_count == 200
        mock_repository.save.assert_called_once_with(session)

    def test_update_token_count_not_found(self, service, mock_repository):
        """Test updating token count when session is not found."""
        session_id = "non-existent"
        mock_repository.find.return_value = None

        service.update_token_count(session_id, 200)
        mock_repository.save.assert_not_called()


class TestSessionMetaServiceUpdateCachedContentTokenCount:
    """Tests for update_cached_content_token_count method."""

    def test_update_cached_content_token_count_success(self, service, mock_repository):
        """Test updating cached content token count successfully."""
        session_id = "test-session"
        session = SessionFactory.create(
            session_id=session_id, cached_content_token_count=50
        )
        mock_repository.find.return_value = session

        service.update_cached_content_token_count(session_id, 150)

        assert session.cached_content_token_count == 150
        mock_repository.save.assert_called_once_with(session)

    def test_update_cached_content_token_count_not_found(
        self, service, mock_repository
    ):
        """Test updating cached content token count when session is not found."""
        session_id = "non-existent"
        mock_repository.find.return_value = None

        service.update_cached_content_token_count(session_id, 150)
        mock_repository.save.assert_not_called()


class TestSessionMetaServiceUpdateCachedTurnCount:
    """Tests for update_cached_turn_count method."""

    def test_update_cached_turn_count_success(self, service, mock_repository):
        """Test updating cached turn count successfully."""
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id, cached_turn_count=2)
        mock_repository.find.return_value = session

        service.update_cached_turn_count(session_id, 4)

        assert session.cached_turn_count == 4
        mock_repository.save.assert_called_once_with(session)

    def test_update_cached_turn_count_not_found(self, service, mock_repository):
        """Test updating cached turn count when session is not found."""
        session_id = "non-existent"
        mock_repository.find.return_value = None

        service.update_cached_turn_count(session_id, 4)
        mock_repository.save.assert_not_called()
