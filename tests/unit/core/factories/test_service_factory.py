"""Unit tests for ServiceFactory."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings

from tests.factories.models import create_test_settings


@pytest.fixture
def mock_settings() -> Settings:
    """Create a test Settings object."""
    settings = create_test_settings(
        timezone="UTC",
        sessions_path="sessions",
    )
    return settings


@pytest.fixture
def factory(mock_settings: Settings) -> ServiceFactory:
    """Create a ServiceFactory instance."""
    return ServiceFactory(project_root="/mock/root", settings=mock_settings)


class TestServiceFactory:
    """Tests for ServiceFactory class."""

    def test_init(self, mock_settings: Settings):
        """Test initialization of ServiceFactory."""
        with (
            patch(
                "pipe.core.factories.service_factory.FileSystemLoader"
            ) as mock_loader,
            patch("pipe.core.factories.service_factory.Environment") as mock_env,
        ):
            factory = ServiceFactory(project_root="/mock/root", settings=mock_settings)
            assert factory.project_root == "/mock/root"
            assert factory.settings == mock_settings
            assert factory._session_service_instance is None
            assert factory._session_optimization_service_instance is None
            mock_loader.assert_called_once()
            mock_env.assert_called_once()

    def test_create_jinja_environment(self, factory: ServiceFactory):
        """Test _create_jinja_environment method."""
        env = factory.jinja_env
        assert "tojson" in env.filters
        assert "pydantic_dump" in env.filters

        # Test tojson filter
        tojson = env.filters["tojson"]
        assert tojson({"key": "value"}) == '{"key": "value"}'
        assert tojson({"key": "日本語"}) == '{"key": "日本語"}'

        # Test pydantic_dump filter
        pydantic_dump = env.filters["pydantic_dump"]
        mock_model = MagicMock()
        mock_model.model_dump.return_value = {"dumped": True}
        assert pydantic_dump(mock_model) == {"dumped": True}
        assert pydantic_dump("not a model") == "not a model"

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionService")
    def test_create_session_service(
        self,
        mock_session_service_class,
        mock_session_repo_class,
        factory: ServiceFactory,
    ):
        """Test create_session_service method."""
        # Mock create_file_indexer_service and create_session_optimization_service
        # to avoid deep nesting of mocks
        with (
            patch.object(factory, "create_file_indexer_service") as mock_create_indexer,
            patch.object(
                factory, "create_session_optimization_service"
            ) as mock_create_opt,
        ):
            service = factory.create_session_service()

            assert factory._session_service_instance == service
            mock_session_repo_class.assert_called_once_with(
                factory.project_root, factory.settings
            )
            mock_create_indexer.assert_called_once()
            mock_session_service_class.assert_called_once()
            mock_create_opt.assert_called_once()

            # Test singleton behavior
            service2 = factory.create_session_service()
            assert service2 == service
            assert mock_session_service_class.call_count == 1

    @patch("pipe.core.factories.service_factory.ResourceRepository")
    @patch("pipe.core.factories.service_factory.PromptService")
    def test_create_prompt_service(
        self,
        mock_prompt_service_class,
        mock_resource_repo_class,
        factory: ServiceFactory,
    ):
        """Test create_prompt_service method."""
        service = factory.create_prompt_service()
        mock_resource_repo_class.assert_called_once_with(factory.project_root)
        mock_prompt_service_class.assert_called_once()
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.FileIndexRepository")
    @patch("pipe.core.factories.service_factory.FileIndexerService")
    def test_create_file_indexer_service(
        self, mock_indexer_service_class, mock_index_repo_class, factory: ServiceFactory
    ):
        """Test create_file_indexer_service method."""
        service = factory.create_file_indexer_service()
        mock_index_repo_class.assert_called_once_with(base_path=factory.project_root)
        mock_indexer_service_class.assert_called_once()
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.FileSystemRepository")
    def test_create_filesystem_repository(
        self, mock_fs_repo_class, factory: ServiceFactory
    ):
        """Test create_filesystem_repository method."""
        repo = factory.create_filesystem_repository()
        mock_fs_repo_class.assert_called_once_with(factory.project_root)
        assert isinstance(repo, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionManagementService")
    def test_create_session_management_service(
        self, mock_mgmt_service_class, mock_session_repo_class, factory: ServiceFactory
    ):
        """Test create_session_management_service method."""
        service = factory.create_session_management_service()
        mock_session_repo_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        mock_mgmt_service_class.assert_called_once_with(
            mock_session_repo_class.return_value
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.ProcedureRepository")
    @patch("pipe.core.factories.service_factory.ProcedureService")
    def test_create_procedure_service(
        self, mock_proc_service_class, mock_proc_repo_class, factory: ServiceFactory
    ):
        """Test create_procedure_service method."""
        service = factory.create_procedure_service()
        mock_proc_repo_class.assert_called_once()
        mock_proc_service_class.assert_called_once_with(
            mock_proc_repo_class.return_value
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.RoleRepository")
    @patch("pipe.core.factories.service_factory.RoleService")
    def test_create_role_service(
        self, mock_role_service_class, mock_role_repo_class, factory: ServiceFactory
    ):
        """Test create_role_service method."""
        service = factory.create_role_service()
        mock_role_repo_class.assert_called_once()
        mock_role_service_class.assert_called_once_with(
            mock_role_repo_class.return_value
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionTreeService")
    def test_create_session_tree_service(
        self, mock_tree_service_class, mock_session_repo_class, factory: ServiceFactory
    ):
        """Test create_session_tree_service method."""
        service = factory.create_session_tree_service()
        mock_session_repo_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        mock_tree_service_class.assert_called_once_with(
            mock_session_repo_class.return_value, factory.settings
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionWorkflowService")
    def test_create_session_workflow_service(
        self,
        mock_workflow_service_class,
        mock_session_repo_class,
        factory: ServiceFactory,
    ):
        """Test create_session_workflow_service method."""
        with patch.object(
            factory, "create_session_optimization_service"
        ) as mock_create_opt:
            service = factory.create_session_workflow_service()
            mock_create_opt.assert_called_once()
            mock_session_repo_class.assert_called_once_with(
                factory.project_root, factory.settings
            )
            mock_workflow_service_class.assert_called_once_with(
                mock_create_opt.return_value,
                mock_session_repo_class.return_value,
                factory.settings,
                factory.project_root,
            )
            assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.agents.takt_agent.TaktAgent")
    @patch("pipe.core.factories.service_factory.SessionOptimizationService")
    def test_create_session_optimization_service(
        self,
        mock_opt_service_class,
        mock_takt_agent_class,
        mock_session_repo_class,
        factory: ServiceFactory,
    ):
        """Test create_session_optimization_service method."""
        with patch.object(
            factory, "create_session_service"
        ) as mock_create_session_service:
            mock_session_service = mock_create_session_service.return_value

            service = factory.create_session_optimization_service()

            assert factory._session_optimization_service_instance == service
            mock_create_session_service.assert_called_once()
            mock_session_repo_class.assert_called_once_with(
                factory.project_root, factory.settings
            )
            mock_takt_agent_class.assert_called_once_with(
                factory.project_root, factory.settings
            )
            mock_opt_service_class.assert_called_once_with(
                factory.project_root,
                mock_takt_agent_class.return_value,
                mock_session_repo_class.return_value,
            )
            mock_session_service.set_history_manager.assert_called_once_with(service)

            # Test singleton behavior
            service2 = factory.create_session_optimization_service()
            assert service2 == service
            assert mock_opt_service_class.call_count == 1

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionReferenceService")
    def test_create_session_reference_service(
        self, mock_ref_service_class, mock_session_repo_class, factory: ServiceFactory
    ):
        """Test create_session_reference_service method."""
        service = factory.create_session_reference_service()
        mock_session_repo_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        mock_ref_service_class.assert_called_once_with(
            factory.project_root, mock_session_repo_class.return_value
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionArtifactService")
    def test_create_session_artifact_service(
        self, mock_art_service_class, mock_session_repo_class, factory: ServiceFactory
    ):
        """Test create_session_artifact_service method."""
        service = factory.create_session_artifact_service()
        mock_session_repo_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        mock_art_service_class.assert_called_once_with(
            factory.project_root, mock_session_repo_class.return_value
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionTurnService")
    def test_create_session_turn_service(
        self, mock_turn_service_class, mock_session_repo_class, factory: ServiceFactory
    ):
        """Test create_session_turn_service method."""
        service = factory.create_session_turn_service()
        mock_session_repo_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        mock_turn_service_class.assert_called_once_with(
            factory.settings, mock_session_repo_class.return_value
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionMetaService")
    def test_create_session_meta_service_no_gemini(
        self, mock_meta_service_class, mock_session_repo_class, factory: ServiceFactory
    ):
        """Test create_session_meta_service method when agent is not gemini-api."""
        # Use a mock for settings to allow arbitrary attributes like 'agent'
        mock_settings = MagicMock()
        mock_settings.agent = "other-agent"
        factory.settings = mock_settings

        service = factory.create_session_meta_service()
        mock_session_repo_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        mock_meta_service_class.assert_called_once_with(
            mock_session_repo_class.return_value, None
        )
        assert isinstance(service, MagicMock)

    @patch("google.genai.Client")
    @patch("pipe.core.domains.gemini_cache_manager.GeminiCacheManager")
    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionMetaService")
    def test_create_session_meta_service_with_gemini(
        self,
        mock_meta_service_class,
        mock_session_repo_class,
        mock_cache_mgr_class,
        mock_client_class,
        factory: ServiceFactory,
    ):
        """Test create_session_meta_service method when agent is gemini-api."""
        # Use a mock for settings to allow arbitrary attributes like 'agent'
        mock_settings = MagicMock()
        mock_settings.agent = "gemini-api"
        mock_settings.gemini_api_key = "test-key"
        mock_settings.model.name = "gemini-test"
        mock_settings.model.cache_update_threshold = 20000
        factory.settings = mock_settings

        service = factory.create_session_meta_service()

        mock_client_class.assert_called_once_with(api_key="test-key")
        mock_cache_mgr_class.assert_called_once_with(
            client=mock_client_class.return_value,
            project_root=factory.project_root,
            model_name=factory.settings.model.name,
            cache_update_threshold=factory.settings.model.cache_update_threshold,
            settings=factory.settings,
        )
        mock_meta_service_class.assert_called_once_with(
            mock_session_repo_class.return_value, mock_cache_mgr_class.return_value
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionRepository")
    @patch("pipe.core.factories.service_factory.SessionTodoService")
    def test_create_session_todo_service(
        self, mock_todo_service_class, mock_session_repo_class, factory: ServiceFactory
    ):
        """Test create_session_todo_service method."""
        service = factory.create_session_todo_service()
        mock_session_repo_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        mock_todo_service_class.assert_called_once_with(
            mock_session_repo_class.return_value
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.SearchSessionsService")
    def test_create_search_sessions_service(
        self, mock_search_service_class, factory: ServiceFactory
    ):
        """Test create_search_sessions_service method."""
        service = factory.create_search_sessions_service()
        expected_path = "/mock/root/sessions"
        mock_search_service_class.assert_called_once_with(expected_path)
        assert isinstance(service, MagicMock)

    @patch("pipe.core.agents.takt_agent.TaktAgent")
    @patch("pipe.core.services.verification_service.VerificationService")
    def test_create_verification_service(
        self, mock_verif_service_class, mock_takt_agent_class, factory: ServiceFactory
    ):
        """Test create_verification_service method."""
        with (
            patch.object(factory, "create_session_service") as mock_create_session,
            patch.object(factory, "create_session_turn_service") as mock_create_turn,
        ):
            service = factory.create_verification_service()

            mock_create_session.assert_called_once()
            mock_create_turn.assert_called_once()
            mock_takt_agent_class.assert_called_once_with(
                factory.project_root, factory.settings
            )
            mock_verif_service_class.assert_called_once_with(
                mock_create_session.return_value,
                mock_create_turn.return_value,
                mock_takt_agent_class.return_value,
            )
            assert isinstance(service, MagicMock)

    @patch("pipe.core.factories.service_factory.StreamingLogRepository")
    @patch("pipe.core.factories.service_factory.StreamingLoggerService")
    def test_create_streaming_logger_service(
        self, mock_logger_service_class, mock_log_repo_class, factory: ServiceFactory
    ):
        """Test create_streaming_logger_service method."""
        service = factory.create_streaming_logger_service("test-session")
        mock_log_repo_class.assert_called_once_with(
            factory.project_root, "test-session", factory.settings
        )
        mock_logger_service_class.assert_called_once_with(
            mock_log_repo_class.return_value, factory.settings
        )
        assert isinstance(service, MagicMock)

    @patch("pipe.core.agents.takt_agent.TaktAgent")
    def test_create_takt_agent(self, mock_takt_agent_class, factory: ServiceFactory):
        """Test create_takt_agent method."""
        agent = factory.create_takt_agent()
        mock_takt_agent_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        assert isinstance(agent, MagicMock)

    @patch("pipe.core.factories.service_factory.SessionInstructionService")
    def test_create_session_instruction_service(
        self, mock_instr_service_class, factory: ServiceFactory
    ):
        """Test create_session_instruction_service method."""
        service = factory.create_session_instruction_service()
        mock_instr_service_class.assert_called_once_with(
            factory.project_root, factory.settings
        )
        assert isinstance(service, MagicMock)
