"""Unit tests for ReferenceToggleDisabledAction."""

from unittest.mock import MagicMock, patch

from pipe.web.action_responses import ReferenceToggleResponse
from pipe.web.actions.reference.reference_toggle_disabled_action import (
    ReferenceToggleDisabledAction,
)

from tests.factories.models.reference_factory import ReferenceFactory
from tests.factories.models.session_factory import SessionFactory


class TestReferenceToggleDisabledAction:
    """Unit tests for ReferenceToggleDisabledAction."""

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.web.service_container.get_session_reference_service")
    def test_execute_success(self, mock_get_ref_service, mock_get_session_service):
        """Test successful execution of toggle disabled action."""
        # Setup
        mock_ref_service = MagicMock()
        mock_get_ref_service.return_value = mock_ref_service
        mock_ref_service.toggle_reference_disabled_by_index.return_value = True

        mock_session_service = MagicMock()
        mock_get_session_service.return_value = mock_session_service

        references = [ReferenceFactory.create(path="test.py", disabled=False)]
        session = SessionFactory.create(references=references)
        mock_session_service.get_session.return_value = session

        mock_request = MagicMock()
        mock_request.session_id = "test-session"
        mock_request.reference_index = 0

        action = ReferenceToggleDisabledAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Assert
        assert isinstance(result, ReferenceToggleResponse)
        assert result.path == "test.py"
        assert result.disabled is True
        assert result.message == "Reference disabled status toggled"

        mock_ref_service.toggle_reference_disabled_by_index.assert_called_once_with(
            "test-session", 0
        )
        mock_session_service.get_session.assert_called_once_with("test-session")

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.web.service_container.get_session_reference_service")
    def test_execute_session_not_found(
        self, mock_get_ref_service, mock_get_session_service
    ):
        """Test execution when session is not found."""
        # Setup
        mock_ref_service = MagicMock()
        mock_get_ref_service.return_value = mock_ref_service
        mock_ref_service.toggle_reference_disabled_by_index.return_value = False

        mock_session_service = MagicMock()
        mock_get_session_service.return_value = mock_session_service
        mock_session_service.get_session.return_value = None

        mock_request = MagicMock()
        mock_request.session_id = "missing-session"
        mock_request.reference_index = 0

        action = ReferenceToggleDisabledAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Assert
        assert result.path == ""
        assert result.disabled is False

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.web.service_container.get_session_reference_service")
    def test_execute_index_out_of_range(
        self, mock_get_ref_service, mock_get_session_service
    ):
        """Test execution when index is out of range."""
        # Setup
        mock_ref_service = MagicMock()
        mock_get_ref_service.return_value = mock_ref_service
        mock_ref_service.toggle_reference_disabled_by_index.return_value = True

        mock_session_service = MagicMock()
        mock_get_session_service.return_value = mock_session_service

        session = SessionFactory.create(references=[])
        mock_session_service.get_session.return_value = session

        mock_request = MagicMock()
        mock_request.session_id = "test-session"
        mock_request.reference_index = 5

        action = ReferenceToggleDisabledAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Assert
        assert result.path == ""
        assert result.disabled is True
