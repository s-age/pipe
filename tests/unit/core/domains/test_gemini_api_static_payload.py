"""Unit tests for gemini_api_static_payload module."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from google.genai import types
from pipe.core.domains import gemini_api_static_payload
from pipe.core.factories.prompt_factory import PromptFactory
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn


@pytest.fixture
def mock_session():
    """Create a mock session with required attributes."""
    session = MagicMock(spec=Session)
    session.session_id = "test-session-123"
    session.created_at = "2025-01-01T00:00:00Z"
    session.purpose = "Test purpose"
    session.background = "Test background"
    session.roles = ["developer", "tester"]
    session.multi_step_reasoning_enabled = True
    session.procedure = "Test procedure"
    session.artifacts = []
    return session


@pytest.fixture
def mock_prompt_factory():
    """Create a mock PromptFactory."""
    mock_factory = Mock(spec=PromptFactory)
    # Create a mock prompt object with required attributes
    mock_prompt = {
        "session_id": "test-session-123",
        "created_at": "2025-01-01T00:00:00Z",
        "purpose": "Test purpose",
        "background": "Test background",
        "roles": ["developer", "tester"],
        "multi_step_reasoning_enabled": True,
        "procedure": "Test procedure",
        "cached_history": [],
    }
    mock_factory.create.return_value = mock_prompt
    return mock_factory


@pytest.fixture
def mock_settings():
    """Create a mock Settings object."""
    return Mock(spec=Settings)


@pytest.fixture
def mock_turns():
    """Create a list of mock turns."""
    return [
        UserTaskTurn(
            type="user_task",
            instruction="First instruction",
            timestamp="2025-01-01T00:00:01Z",
        ),
        ModelResponseTurn(
            type="model_response",
            content="First response",
            timestamp="2025-01-01T00:00:02Z",
        ),
        UserTaskTurn(
            type="user_task",
            instruction="Second instruction",
            timestamp="2025-01-01T00:00:03Z",
        ),
        ModelResponseTurn(
            type="model_response",
            content="Second response",
            timestamp="2025-01-01T00:00:04Z",
        ),
    ]


class TestBuild:
    """Test cases for the build function."""

    def test_build_returns_content_list(
        self, mock_session, mock_turns, mock_prompt_factory, mock_settings
    ):
        """Test that build returns a list of Content objects."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = '{"test": "data"}'
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            result = gemini_api_static_payload.build(
                session=mock_session,
                full_history=mock_turns,
                cached_turn_count=2,
                project_root="/test/project",
                prompt_factory=mock_prompt_factory,
                settings=mock_settings,
            )

            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], types.Content)

    def test_build_slices_history_correctly(
        self, mock_session, mock_turns, mock_prompt_factory, mock_settings
    ):
        """Test that build correctly slices the history based on cached_turn_count."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = '{"test": "data"}'
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            gemini_api_static_payload.build(
                session=mock_session,
                full_history=mock_turns,
                cached_turn_count=2,
                project_root="/test/project",
                prompt_factory=mock_prompt_factory,
                settings=mock_settings,
            )

            # Verify template was called with correct cached_history
            render_call_args = mock_template.render.call_args
            assert "cached_history" in render_call_args.kwargs
            assert len(render_call_args.kwargs["cached_history"]) == 2
            assert render_call_args.kwargs["cached_history"] == mock_turns[:2]

    def test_build_creates_jinja_environment_correctly(
        self, mock_session, mock_turns, mock_prompt_factory, mock_settings
    ):
        """Test that build creates Jinja environment with correct settings."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            with patch(
                "pipe.core.domains.gemini_api_static_payload.FileSystemLoader"
            ) as mock_loader:
                mock_env = MagicMock()
                mock_template = MagicMock()
                mock_template.render.return_value = '{"test": "data"}'
                mock_env.get_template.return_value = mock_template
                mock_env_class.return_value = mock_env

                gemini_api_static_payload.build(
                    session=mock_session,
                    full_history=mock_turns,
                    cached_turn_count=2,
                    project_root="/test/project",
                    prompt_factory=mock_prompt_factory,
                    settings=mock_settings,
                )

                # Verify FileSystemLoader was called with correct path
                mock_loader.assert_called_once_with("/test/project/templates/prompt")

                # Verify Environment was created with correct settings
                mock_env_class.assert_called_once()
                call_kwargs = mock_env_class.call_args.kwargs
                assert call_kwargs["trim_blocks"] is True
                assert call_kwargs["lstrip_blocks"] is True

    def test_build_loads_correct_template(
        self, mock_session, mock_turns, mock_prompt_factory, mock_settings
    ):
        """Test that build loads the gemini_static_prompt.j2 template."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = '{"test": "data"}'
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            gemini_api_static_payload.build(
                session=mock_session,
                full_history=mock_turns,
                cached_turn_count=2,
                project_root="/test/project",
                prompt_factory=mock_prompt_factory,
                settings=mock_settings,
            )

            mock_env.get_template.assert_called_once_with("gemini_static_prompt.j2")

    def test_build_passes_correct_context_to_template(
        self, mock_session, mock_turns, mock_prompt_factory, mock_settings
    ):
        """Test that build passes all required session fields to template."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = '{"test": "data"}'
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            gemini_api_static_payload.build(
                session=mock_session,
                full_history=mock_turns,
                cached_turn_count=2,
                project_root="/test/project",
                prompt_factory=mock_prompt_factory,
                settings=mock_settings,
            )

            render_call_args = mock_template.render.call_args
            context = render_call_args.kwargs["session"]

            assert context["session_id"] == "test-session-123"
            assert context["created_at"] == "2025-01-01T00:00:00Z"
            assert context["purpose"] == "Test purpose"
            assert context["background"] == "Test background"
            assert context["roles"] == ["developer", "tester"]
            assert context["multi_step_reasoning_enabled"] is True
            assert context["procedure"] == "Test procedure"

    def test_build_content_has_correct_structure(
        self, mock_session, mock_turns, mock_prompt_factory, mock_settings
    ):
        """Test that the returned Content object has correct role and parts."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            rendered_text = '{"cached": "content"}'
            mock_template.render.return_value = rendered_text
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            result = gemini_api_static_payload.build(
                session=mock_session,
                full_history=mock_turns,
                cached_turn_count=2,
                project_root="/test/project",
                prompt_factory=mock_prompt_factory,
                settings=mock_settings,
            )

            content = result[0]
            assert content.role == "user"
            assert len(content.parts) == 1
            assert isinstance(content.parts[0], types.Part)
            assert content.parts[0].text == rendered_text

    def test_build_with_zero_cached_turns(
        self, mock_session, mock_turns, mock_prompt_factory, mock_settings
    ):
        """Test that build works with cached_turn_count=0."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = '{"test": "data"}'
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            gemini_api_static_payload.build(
                session=mock_session,
                full_history=mock_turns,
                cached_turn_count=0,
                project_root="/test/project",
                prompt_factory=mock_prompt_factory,
                settings=mock_settings,
            )

            render_call_args = mock_template.render.call_args
            assert "cached_history" in render_call_args.kwargs
            assert len(render_call_args.kwargs["cached_history"]) == 0

    def test_build_with_all_turns_cached(
        self, mock_session, mock_turns, mock_prompt_factory, mock_settings
    ):
        """Test that build works when all turns are cached."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = '{"test": "data"}'
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            gemini_api_static_payload.build(
                session=mock_session,
                full_history=mock_turns,
                cached_turn_count=len(mock_turns),
                project_root="/test/project",
                prompt_factory=mock_prompt_factory,
                settings=mock_settings,
            )

            render_call_args = mock_template.render.call_args
            assert "cached_history" in render_call_args.kwargs
            assert len(render_call_args.kwargs["cached_history"]) == len(mock_turns)
            assert render_call_args.kwargs["cached_history"] == mock_turns

    def test_build_with_empty_history(
        self, mock_session, mock_prompt_factory, mock_settings
    ):
        """Test that build works with empty history."""
        with patch(
            "pipe.core.domains.gemini_api_static_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = '{"test": "data"}'
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            result = gemini_api_static_payload.build(
                session=mock_session,
                full_history=[],
                cached_turn_count=0,
                project_root="/test/project",
                prompt_factory=mock_prompt_factory,
                settings=mock_settings,
            )

            assert isinstance(result, list)
            assert len(result) == 1
            render_call_args = mock_template.render.call_args
            assert "cached_history" in render_call_args.kwargs
            assert len(render_call_args.kwargs["cached_history"]) == 0
