"""
Unit tests for fork_delegate.
"""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.delegates import fork_delegate
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings


@pytest.fixture
def mock_settings() -> MagicMock:
    """Create a mock Settings object."""
    return MagicMock(spec=Settings)


@pytest.fixture
def mock_workflow_service() -> MagicMock:
    """Create a mock SessionWorkflowService."""
    service = MagicMock()
    service.fork_session = MagicMock()
    return service


class TestForkDelegate:
    """Tests for the fork_delegate.run function."""

    @patch("pipe.core.delegates.fork_delegate.ServiceFactory")
    def test_run_success(
        self,
        mock_service_factory_class: MagicMock,
        mock_settings: MagicMock,
        mock_workflow_service: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test successful session fork."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory.create_session_workflow_service.return_value = (
            mock_workflow_service
        )
        mock_service_factory_class.return_value = mock_factory

        args = TaktArgs(fork="source-session", at_turn=5)
        project_root = "/mock/project"

        # Execute
        fork_delegate.run(args, project_root, mock_settings)

        # Verify
        mock_service_factory_class.assert_called_once_with(project_root, mock_settings)
        mock_workflow_service.fork_session.assert_called_once_with("source-session", 4)

        captured = capsys.readouterr()
        assert "Successfully forked session source-session at turn 5." in captured.out

    def test_run_missing_at_turn(self, mock_settings: MagicMock) -> None:
        """Test that ValueError is raised when at_turn is missing."""
        args = TaktArgs(fork="source-session", at_turn=None)
        project_root = "/mock/project"

        with pytest.raises(ValueError, match="--at-turn is required"):
            fork_delegate.run(args, project_root, mock_settings)

    @patch("pipe.core.delegates.fork_delegate.ServiceFactory")
    def test_run_file_not_found(
        self,
        mock_service_factory_class: MagicMock,
        mock_settings: MagicMock,
        mock_workflow_service: MagicMock,
    ) -> None:
        """Test handling of FileNotFoundError from workflow service."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory.create_session_workflow_service.return_value = (
            mock_workflow_service
        )
        mock_service_factory_class.return_value = mock_factory

        mock_workflow_service.fork_session.side_effect = FileNotFoundError(
            "Session not found"
        )

        args = TaktArgs(fork="invalid-session", at_turn=1)
        project_root = "/mock/project"

        with pytest.raises(ValueError, match="Session not found"):
            fork_delegate.run(args, project_root, mock_settings)

    @patch("pipe.core.delegates.fork_delegate.ServiceFactory")
    def test_run_index_error(
        self,
        mock_service_factory_class: MagicMock,
        mock_settings: MagicMock,
        mock_workflow_service: MagicMock,
    ) -> None:
        """Test handling of IndexError from workflow service."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory.create_session_workflow_service.return_value = (
            mock_workflow_service
        )
        mock_service_factory_class.return_value = mock_factory

        mock_workflow_service.fork_session.side_effect = IndexError(
            "Turn index out of range"
        )

        args = TaktArgs(fork="source-session", at_turn=999)
        project_root = "/mock/project"

        with pytest.raises(ValueError, match="Turn index out of range"):
            fork_delegate.run(args, project_root, mock_settings)
