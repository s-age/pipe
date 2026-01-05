"""Unit tests for GeminiCliPayloadBuilder."""

import json
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.domains.gemini_cli_payload import GeminiCliPayloadBuilder
from pipe.core.models.prompt import Prompt


class TestGeminiCliPayloadBuilder:
    """Tests for GeminiCliPayloadBuilder."""

    @pytest.fixture
    def project_root(self, tmp_path):
        """Create a temporary project root with templates."""
        template_dir = tmp_path / "templates" / "prompt"
        template_dir.mkdir(parents=True)
        (template_dir / "gemini_cli_prompt.j2").write_text(
            '{"instruction": "{{ prompt.main_instruction }}"}'
        )
        (template_dir / "gemini_api_prompt.j2").write_text(
            '{"instruction": "{{ prompt.main_instruction }}", "api": true}'
        )
        return str(tmp_path)

    @pytest.fixture
    def builder(self, project_root):
        """Create a GeminiCliPayloadBuilder instance."""
        return GeminiCliPayloadBuilder(project_root=project_root)

    @pytest.fixture
    def mock_session_service(self):
        """Create a mock SessionService."""
        service = MagicMock()
        service.current_session = MagicMock()
        service.current_session.artifacts = []
        service.settings = MagicMock()
        service.current_instruction = "Test instruction"
        return service

    def test_init(self, project_root):
        """Test initialization and Jinja2 environment setup."""
        builder = GeminiCliPayloadBuilder(
            project_root=project_root, api_mode="gemini-api"
        )
        assert builder.project_root == project_root
        assert builder.api_mode == "gemini-api"
        assert builder.jinja_env is not None
        assert "tojson" in builder.jinja_env.filters
        assert "pydantic_dump" in builder.jinja_env.filters

    def test_tojson_filter(self, builder):
        """Test the custom tojson filter."""
        tojson = builder.jinja_env.filters["tojson"]
        data = {"key": "日本語"}
        result = tojson(data)
        # ensure_ascii=False should preserve Japanese characters
        assert "日本語" in result
        assert json.loads(result) == data

    def test_pydantic_dump_filter(self, builder):
        """Test the custom pydantic_dump filter."""
        pydantic_dump = builder.jinja_env.filters["pydantic_dump"]

        # Test with object having model_dump
        mock_obj = MagicMock()
        mock_obj.model_dump.return_value = {"field": "value"}
        assert pydantic_dump(mock_obj) == {"field": "value"}
        mock_obj.model_dump.assert_called_once_with(mode="json", exclude_none=True)

        # Test with regular object
        assert pydantic_dump("string") == "string"

    @patch("pipe.core.repositories.resource_repository.ResourceRepository")
    @patch("pipe.core.factories.prompt_factory.PromptFactory")
    @patch("pipe.core.domains.artifacts.build_artifacts_from_data")
    def test_build_prompt_model_success(
        self,
        mock_build_artifacts,
        mock_prompt_factory_class,
        mock_resource_repo_class,
        builder,
        mock_session_service,
    ):
        """Test building prompt model successfully."""
        mock_session_service.current_session.artifacts = ["file1.txt"]

        mock_repo = mock_resource_repo_class.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = "content1"

        mock_factory = mock_prompt_factory_class.return_value
        expected_prompt = MagicMock(spec=Prompt)
        mock_factory.create.return_value = expected_prompt

        mock_build_artifacts.return_value = ["artifact_obj"]

        result = builder.build_prompt_model(mock_session_service)

        assert result == expected_prompt
        mock_resource_repo_class.assert_called_once_with(builder.project_root)
        mock_prompt_factory_class.assert_called_once_with(
            builder.project_root, mock_repo
        )
        mock_repo.exists.assert_called_once()
        mock_repo.read_text.assert_called_once()
        mock_build_artifacts.assert_called_once_with([("file1.txt", "content1")])
        mock_factory.create.assert_called_once_with(
            session=mock_session_service.current_session,
            settings=mock_session_service.settings,
            artifacts=["artifact_obj"],
            current_instruction=mock_session_service.current_instruction,
        )

    @patch("pipe.core.repositories.resource_repository.ResourceRepository")
    @patch("pipe.core.factories.prompt_factory.PromptFactory")
    def test_build_prompt_model_no_artifacts(
        self,
        mock_prompt_factory_class,
        mock_resource_repo_class,
        builder,
        mock_session_service,
    ):
        """Test building prompt model without artifacts."""
        mock_session_service.current_session.artifacts = None

        mock_factory = mock_prompt_factory_class.return_value
        expected_prompt = MagicMock(spec=Prompt)
        mock_factory.create.return_value = expected_prompt

        result = builder.build_prompt_model(mock_session_service)

        assert result == expected_prompt
        mock_factory.create.assert_called_once_with(
            session=mock_session_service.current_session,
            settings=mock_session_service.settings,
            artifacts=None,
            current_instruction=mock_session_service.current_instruction,
        )

    def test_build_prompt_model_no_session(self, builder, mock_session_service):
        """Test building prompt model raises ValueError if no session."""
        mock_session_service.current_session = None
        with pytest.raises(
            ValueError, match="Cannot build prompt without a current session"
        ):
            builder.build_prompt_model(mock_session_service)

    def test_render_cli_mode(self, builder):
        """Test rendering in gemini-cli mode."""
        mock_prompt = MagicMock(spec=Prompt)
        mock_prompt.main_instruction = "Hello @world"

        result = builder.render(mock_prompt)

        # Unescape for JSON parsing validation
        data = json.loads(result.replace("\\@", "@"))
        assert data["instruction"] == "Hello @world"
        assert "\\@" in result

    def test_render_api_mode(self, project_root):
        """Test rendering in gemini-api mode."""
        builder = GeminiCliPayloadBuilder(
            project_root=project_root, api_mode="gemini-api"
        )
        mock_prompt = MagicMock(spec=Prompt)
        mock_prompt.main_instruction = "API Test"

        result = builder.render(mock_prompt)

        data = json.loads(result)
        assert data["instruction"] == "API Test"
        assert data.get("api") is True

    def test_build(self, builder, mock_session_service):
        """Test the build orchestration method."""
        with patch.object(builder, "build_prompt_model") as mock_build_model:
            with patch.object(builder, "render") as mock_render:
                mock_prompt = MagicMock(spec=Prompt)
                mock_build_model.return_value = mock_prompt
                mock_render.return_value = "rendered_payload"

                result = builder.build(mock_session_service)

                assert result == "rendered_payload"
                mock_build_model.assert_called_once_with(mock_session_service)
                mock_render.assert_called_once_with(mock_prompt)
