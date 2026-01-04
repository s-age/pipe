"""Unit tests for IndexFilesAction."""

from unittest.mock import MagicMock, patch

from flask import Request
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.fs.index_files_action import IndexFilesAction


class TestIndexFilesAction:
    """Tests for IndexFilesAction."""

    def test_init(self) -> None:
        """Test initialization of IndexFilesAction."""
        params = {"key": "value"}
        request_data = MagicMock(spec=Request)

        action = IndexFilesAction(params=params, request_data=request_data)

        assert action.params == params
        assert action.request_data == request_data

    @patch("pipe.web.service_container.get_file_indexer_service")
    def test_execute(self, mock_get_service: MagicMock) -> None:
        """Test execute method calls indexer service and returns success response."""
        # Setup mock service
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Initialize action
        action = IndexFilesAction()

        # Execute
        result = action.execute()

        # Verify service call
        mock_get_service.assert_called_once()
        mock_service.create_index.assert_called_once()

        # Verify response
        assert isinstance(result, SuccessMessageResponse)
        assert result.message == "Indexing started"
