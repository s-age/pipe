"""Unit tests for SessionWorkflowService."""

import zoneinfo
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.services.session_workflow_service import SessionWorkflowService

from tests.factories.models import SessionFactory


@pytest.fixture
def mock_optimization_service():
    """Create a mock SessionOptimizationService."""
    return MagicMock()


@pytest.fixture
def mock_repository():
    """Create a mock SessionRepository."""
    return MagicMock()


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock()
    settings.timezone = "Asia/Tokyo"
    settings.model = MagicMock()
    settings.model.name = "gemini-1.5-flash"
    settings.sessions_path = ".sessions"
    return settings


@pytest.fixture
def service(mock_optimization_service, mock_repository, mock_settings):
    """Create SessionWorkflowService with mocked dependencies."""
    return SessionWorkflowService(
        optimization_service=mock_optimization_service,
        repository=mock_repository,
        settings=mock_settings,
        project_root="/mock/root",
    )


class TestSessionWorkflowServiceInit:
    """Test SessionWorkflowService.__init__ method."""

    def test_init_with_valid_timezone(self, mock_settings):
        """Test initialization with a valid timezone."""
        service = SessionWorkflowService(settings=mock_settings)
        assert service.timezone_obj.key == "Asia/Tokyo"

    @patch("pipe.core.services.session_workflow_service.zoneinfo.ZoneInfo")
    def test_init_with_invalid_timezone(self, mock_zoneinfo, mock_settings):
        """Test initialization with an invalid timezone falls back to UTC."""
        mock_settings.timezone = "Invalid/Timezone"

        def zoneinfo_side_effect(key):
            if key == "Invalid/Timezone":
                raise zoneinfo.ZoneInfoNotFoundError
            return MagicMock(key="UTC")

        mock_zoneinfo.side_effect = zoneinfo_side_effect

        service = SessionWorkflowService(settings=mock_settings)
        assert service.timezone_obj.key == "UTC"

    def test_init_without_settings(self):
        """Test initialization without settings defaults to UTC."""
        service = SessionWorkflowService(settings=None)
        assert service.timezone_obj.key == "UTC"


class TestSessionWorkflowServiceForkSession:
    """Test SessionWorkflowService.fork_session method."""

    @patch("pipe.core.services.session_workflow_service.fork_session")
    def test_fork_session_success(self, mock_fork_domain, service, mock_repository):
        """Test successful session fork."""
        original_session = SessionFactory.create(session_id="original")
        new_session = SessionFactory.create(session_id="forked")
        mock_repository.find.return_value = original_session
        mock_fork_domain.return_value = new_session

        with patch.object(service, "_calculate_token_count", return_value=100):
            result = service.fork_session("original", 1)

            assert result == "forked"
            assert new_session.token_count == 100
            mock_repository.find.assert_called_once_with("original")
            mock_fork_domain.assert_called_once_with(
                original_session, 1, service.timezone_obj
            )
            mock_repository.save.assert_called_once_with(new_session)

    def test_fork_session_not_found(self, service, mock_repository):
        """Test fork_session raises FileNotFoundError if session not found."""
        mock_repository.find.return_value = None

        with pytest.raises(
            FileNotFoundError, match="Original session with ID 'missing' not found"
        ):
            service.fork_session("missing", 1)


class TestSessionWorkflowServiceCalculateTokenCount:
    """Test SessionWorkflowService._calculate_token_count method."""

    @patch("pipe.core.factories.service_factory.ServiceFactory")
    @patch("pipe.core.services.gemini_tool_service.GeminiToolService")
    @patch("pipe.core.domains.gemini_token_count.create_local_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.count_tokens")
    def test_calculate_token_count_success(
        self,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_tool_service_cls,
        mock_service_factory_cls,
        service,
    ):
        """Test successful token count calculation."""
        session = SessionFactory.create()

        mock_factory = MagicMock()
        mock_service_factory_cls.return_value = mock_factory

        mock_session_service = MagicMock()
        mock_prompt_service = MagicMock()
        mock_factory.create_session_service.return_value = mock_session_service
        mock_factory.create_prompt_service.return_value = mock_prompt_service

        mock_prompt_model = MagicMock()
        mock_prompt_service.build_prompt.return_value = mock_prompt_model

        mock_template = MagicMock()
        mock_prompt_service.jinja_env.get_template.return_value = mock_template
        mock_template.render.return_value = "rendered prompt"

        mock_tool_service = MagicMock()
        mock_tool_service_cls.return_value = mock_tool_service
        mock_tool_service.load_tools.return_value = ["tool1"]

        mock_create_tokenizer.return_value = MagicMock()
        mock_count_tokens.return_value = 150

        result = service._calculate_token_count(session)

        assert result == 150
        mock_service_factory_cls.assert_called_once_with(
            service.project_root, service.settings
        )
        mock_prompt_service.jinja_env.get_template.assert_called_once_with(
            "gemini_cli_prompt.j2"
        )
        mock_count_tokens.assert_called_once()

    def test_calculate_token_count_failure(self, service):
        """Test that _calculate_token_count returns 0 on failure."""
        session = SessionFactory.create()

        # Trigger an exception by mocking ServiceFactory to raise
        with patch(
            "pipe.core.factories.service_factory.ServiceFactory",
            side_effect=Exception("Error"),
        ):
            result = service._calculate_token_count(session)
            assert result == 0


class TestSessionWorkflowServiceOptimization:
    """Test optimization workflow methods."""

    def test_run_takt_for_therapist(self, service, mock_optimization_service):
        """Test run_takt_for_therapist delegation."""
        expected = MagicMock()
        mock_optimization_service.run_therapist.return_value = expected

        result = service.run_takt_for_therapist("session-1")

        assert result == expected
        mock_optimization_service.run_therapist.assert_called_once_with("session-1")

    def test_run_takt_for_doctor(self, service, mock_optimization_service):
        """Test run_takt_for_doctor delegation."""
        modifications = MagicMock()
        expected = MagicMock()
        mock_optimization_service.run_doctor.return_value = expected

        result = service.run_takt_for_doctor("session-1", modifications)

        assert result == expected
        mock_optimization_service.run_doctor.assert_called_once_with(
            "session-1", modifications
        )


class TestSessionWorkflowServiceStopSession:
    """Test SessionWorkflowService.stop_session method."""

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    @patch("pipe.core.factories.service_factory.ServiceFactory")
    @patch("logging.getLogger")
    def test_stop_session_success(
        self,
        mock_get_logger,
        mock_service_factory_cls,
        mock_pm_service_cls,
        mock_get_settings,
        service,
    ):
        """Test successful session stop workflow."""
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        mock_pm = MagicMock()
        mock_pm_service_cls.return_value = mock_pm
        mock_pm.kill_process.return_value = True

        mock_factory = MagicMock()
        mock_service_factory_cls.return_value = mock_factory
        mock_turn_service = MagicMock()
        mock_factory.create_session_turn_service.return_value = mock_turn_service

        service.stop_session("session-1", "/project/root")

        mock_pm.kill_process.assert_called_once_with("session-1")
        mock_turn_service.rollback_transaction.assert_called_once_with("session-1")
        mock_pm.cleanup_process.assert_called_once_with("session-1")

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    @patch("pipe.core.factories.service_factory.ServiceFactory")
    @patch("logging.getLogger")
    def test_stop_session_kill_failure(
        self,
        mock_get_logger,
        mock_service_factory_cls,
        mock_pm_service_cls,
        mock_get_settings,
        service,
    ):
        """Test session stop workflow when kill_process fails."""
        mock_pm = MagicMock()
        mock_pm_service_cls.return_value = mock_pm
        mock_pm.kill_process.return_value = False

        mock_factory = MagicMock()
        mock_service_factory_cls.return_value = mock_factory
        mock_turn_service = MagicMock()
        mock_factory.create_session_turn_service.return_value = mock_turn_service

        service.stop_session("session-1", "/project/root")

        # Should still continue with cleanup
        mock_turn_service.rollback_transaction.assert_called_once_with("session-1")
        mock_pm.cleanup_process.assert_called_once_with("session-1")
