"""Unit tests for dry_run_delegate."""

import json
from unittest.mock import MagicMock

import pytest
from pipe.core.delegates import dry_run_delegate


class TestDryRunDelegate:
    """Tests for dry_run_delegate.run function."""

    @pytest.fixture
    def mock_session_service(self) -> MagicMock:
        """Create a mock SessionService."""
        service = MagicMock()
        service.settings = MagicMock()
        return service

    @pytest.fixture
    def mock_prompt_service(self) -> MagicMock:
        """Create a mock PromptService."""
        service = MagicMock()
        service.jinja_env = MagicMock()
        return service

    def test_run_gemini_api_mode(
        self,
        mock_session_service: MagicMock,
        mock_prompt_service: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test run() with gemini-api mode."""
        # Setup
        mock_session_service.settings.api_mode = "gemini-api"
        prompt_model = MagicMock()
        mock_prompt_service.build_prompt.return_value = prompt_model

        mock_template = MagicMock()
        mock_template.render.return_value = '{"test": "api"}'
        mock_prompt_service.jinja_env.get_template.return_value = mock_template

        # Execute
        dry_run_delegate.run(mock_session_service, mock_prompt_service)

        # Verify
        mock_prompt_service.build_prompt.assert_called_once_with(mock_session_service)
        mock_prompt_service.jinja_env.get_template.assert_called_once_with(
            "gemini_api_prompt.j2"
        )
        mock_template.render.assert_called_once_with(session=prompt_model)

        captured = capsys.readouterr()
        assert json.loads(captured.out) == {"test": "api"}

    def test_run_gemini_cli_mode(
        self,
        mock_session_service: MagicMock,
        mock_prompt_service: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test run() with gemini-cli mode."""
        # Setup
        mock_session_service.settings.api_mode = "gemini-cli"
        prompt_model = MagicMock()
        mock_prompt_service.build_prompt.return_value = prompt_model

        mock_template = MagicMock()
        mock_template.render.return_value = '{"test": "cli"}'
        mock_prompt_service.jinja_env.get_template.return_value = mock_template

        # Execute
        dry_run_delegate.run(mock_session_service, mock_prompt_service)

        # Verify
        mock_prompt_service.jinja_env.get_template.assert_called_once_with(
            "gemini_cli_prompt.j2"
        )

        captured = capsys.readouterr()
        assert json.loads(captured.out) == {"test": "cli"}

    def test_run_invalid_json_rendered(
        self, mock_session_service: MagicMock, mock_prompt_service: MagicMock
    ) -> None:
        """Test run() when template renders invalid JSON."""
        # Setup
        mock_session_service.settings.api_mode = "gemini-api"
        mock_template = MagicMock()
        mock_template.render.return_value = "invalid json"
        mock_prompt_service.jinja_env.get_template.return_value = mock_template

        # Execute and Verify
        with pytest.raises(json.JSONDecodeError):
            dry_run_delegate.run(mock_session_service, mock_prompt_service)
