from unittest.mock import MagicMock, patch

import pytest
from jinja2 import Environment
from pipe.core.models.prompt import Prompt
from pipe.core.repositories.resource_repository import ResourceRepository
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService

from tests.factories.models import SessionFactory, create_test_settings


@pytest.fixture
def mock_settings():
    return create_test_settings()


@pytest.fixture
def mock_jinja_env():
    return MagicMock(spec=Environment)


@pytest.fixture
def mock_resource_repository():
    return MagicMock(spec=ResourceRepository)


@pytest.fixture
def project_root():
    return "/mock/project/root"


@pytest.fixture
def service(project_root, mock_jinja_env, mock_resource_repository):
    return PromptService(
        project_root=project_root,
        jinja_env=mock_jinja_env,
        resource_repository=mock_resource_repository,
    )


class TestPromptServiceInit:
    """Tests for PromptService.__init__."""

    def test_init(self, project_root, mock_jinja_env, mock_resource_repository):
        """Test that PromptService is initialized correctly."""
        with patch(
            "pipe.core.services.prompt_service.PromptFactory"
        ) as MockPromptFactory:
            service = PromptService(
                project_root=project_root,
                jinja_env=mock_jinja_env,
                resource_repository=mock_resource_repository,
            )
            assert service.project_root == project_root
            assert service.jinja_env == mock_jinja_env
            assert service.resource_repository == mock_resource_repository
            MockPromptFactory.assert_called_once_with(
                project_root, mock_resource_repository
            )
            assert service.prompt_factory == MockPromptFactory.return_value


class TestPromptServiceBuildPrompt:
    """Tests for PromptService.build_prompt."""

    def test_build_prompt_no_session(self, service, mock_settings):
        """Test that build_prompt raises ValueError when no session is present."""
        mock_session_service = MagicMock(spec=SessionService)
        mock_session_service.current_session = None
        mock_session_service.settings = mock_settings

        with pytest.raises(
            ValueError, match="Cannot build prompt without a current session."
        ):
            service.build_prompt(mock_session_service)

    def test_build_prompt_success_no_artifacts(self, service, mock_settings):
        """Test build_prompt successfully without artifacts."""
        mock_session = SessionFactory.create(artifacts=[])
        mock_session_service = MagicMock(spec=SessionService)
        mock_session_service.current_session = mock_session
        mock_session_service.settings = mock_settings
        mock_session_service.current_instruction = "Test instruction"

        expected_prompt = MagicMock(spec=Prompt)
        service.prompt_factory.create = MagicMock(return_value=expected_prompt)

        result = service.build_prompt(mock_session_service)

        assert result == expected_prompt
        service.prompt_factory.create.assert_called_once_with(
            session=mock_session,
            settings=mock_settings,
            artifacts=None,
            current_instruction="Test instruction",
        )

    @patch("pipe.core.services.prompt_service.os.path.abspath")
    @patch("pipe.core.services.prompt_service.os.path.join")
    @patch("pipe.core.services.prompt_service.build_artifacts_from_data")
    def test_build_prompt_with_artifacts(
        self,
        mock_build_artifacts,
        mock_join,
        mock_abspath,
        service,
        mock_resource_repository,
        project_root,
        mock_settings,
    ):
        """Test build_prompt with artifacts."""
        artifact_paths = ["art1.txt", "art2.txt"]
        mock_session = SessionFactory.create(artifacts=artifact_paths)
        mock_session_service = MagicMock(spec=SessionService)
        mock_session_service.current_session = mock_session
        mock_session_service.settings = mock_settings
        mock_session_service.current_instruction = "Test instruction"

        # Mock os.path calls
        mock_join.side_effect = lambda *args: "/".join(args)
        mock_abspath.side_effect = lambda x: x

        # Mock resource repository
        mock_resource_repository.exists.side_effect = [True, False]
        mock_resource_repository.read_text.return_value = "content1"

        # Mock artifact transformation
        processed_artifacts = [MagicMock(), MagicMock()]
        mock_build_artifacts.return_value = processed_artifacts

        expected_prompt = MagicMock(spec=Prompt)
        service.prompt_factory.create = MagicMock(return_value=expected_prompt)

        result = service.build_prompt(mock_session_service)

        assert result == expected_prompt

        # Verify repository calls
        assert mock_resource_repository.exists.call_count == 2
        mock_resource_repository.exists.assert_any_call(
            f"{project_root}/art1.txt", allowed_root=project_root
        )
        mock_resource_repository.exists.assert_any_call(
            f"{project_root}/art2.txt", allowed_root=project_root
        )

        mock_resource_repository.read_text.assert_called_once_with(
            f"{project_root}/art1.txt", allowed_root=project_root
        )

        # Verify build_artifacts_from_data call
        mock_build_artifacts.assert_called_once_with(
            [("art1.txt", "content1"), ("art2.txt", None)]
        )

        # Verify prompt factory call
        service.prompt_factory.create.assert_called_once_with(
            session=mock_session,
            settings=mock_settings,
            artifacts=processed_artifacts,
            current_instruction="Test instruction",
        )
