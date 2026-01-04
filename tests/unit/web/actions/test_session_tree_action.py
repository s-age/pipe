"""Unit tests for SessionTreeAction."""

from unittest.mock import MagicMock, patch

from pipe.web.action_responses import SessionTreeResponse
from pipe.web.actions.session_tree.session_tree_action import SessionTreeAction


class TestSessionTreeAction:
    """Tests for SessionTreeAction."""

    @patch("pipe.web.service_container.get_session_tree_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of SessionTreeAction."""
        # Setup mocks
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Mock the result from the service
        mock_result = MagicMock()
        mock_data = {
            "sessions": {
                "session-1": {
                    "session_id": "session-1",
                    "purpose": "test purpose",
                    "created_at": "2026-01-01T00:00:00Z",
                }
            },
            "session_tree": [
                {
                    "session_id": "session-1",
                    "overview": {
                        "session_id": "session-1",
                        "purpose": "test purpose",
                        "created_at": "2026-01-01T00:00:00Z",
                    },
                    "children": [],
                }
            ],
        }
        mock_result.model_dump.return_value = mock_data
        mock_service.get_session_tree.return_value = mock_result

        # Execute
        action = SessionTreeAction()
        response = action.execute()

        # Verify
        mock_get_service.assert_called_once()
        mock_service.get_session_tree.assert_called_once()
        mock_result.model_dump.assert_called_once()

        assert isinstance(response, SessionTreeResponse)
        assert response.sessions["session-1"].session_id == "session-1"
        assert response.sessions["session-1"].purpose == "test purpose"
        assert len(response.session_tree) == 1
        assert response.session_tree[0].session_id == "session-1"
