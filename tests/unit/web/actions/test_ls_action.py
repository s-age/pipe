"""Unit tests for LsAction."""

from unittest.mock import MagicMock

import pytest
from pipe.core.models.file_search import LsEntry
from pipe.web.action_responses import LsResponse
from pipe.web.actions.fs.ls_action import LsAction
from pipe.web.requests.fs.ls_request import LsRequest


class TestLsAction:
    """Tests for LsAction class."""

    @pytest.fixture
    def mock_file_indexer_service(self) -> MagicMock:
        """Create a mock FileIndexerService."""
        return MagicMock()

    @pytest.fixture
    def valid_ls_request(self) -> LsRequest:
        """Create a valid LsRequest."""
        return LsRequest(final_path_list=["src", "pipe"])

    def test_init(
        self, mock_file_indexer_service: MagicMock, valid_ls_request: LsRequest
    ):
        """Test that LsAction is initialized correctly."""
        action = LsAction(
            file_indexer_service=mock_file_indexer_service,
            validated_request=valid_ls_request,
        )

        assert action.file_indexer_service == mock_file_indexer_service
        assert action.validated_request == valid_ls_request

    def test_execute_success(
        self, mock_file_indexer_service: MagicMock, valid_ls_request: LsRequest
    ):
        """Test successful execution of LsAction."""
        # Setup mock data
        mock_entries = [
            LsEntry(
                name="file1.py",
                path="src/pipe/file1.py",
                is_dir=False,
                size=100,
                mtime=1234567890.0,
            ),
            LsEntry(
                name="dir1",
                path="src/pipe/dir1",
                is_dir=True,
                size=0,
                mtime=1234567890.0,
            ),
        ]
        mock_file_indexer_service.get_ls_data.return_value = mock_entries

        action = LsAction(
            file_indexer_service=mock_file_indexer_service,
            validated_request=valid_ls_request,
        )

        # Execute
        response = action.execute()

        # Verify
        assert isinstance(response, LsResponse)
        assert response.entries == mock_entries
        mock_file_indexer_service.get_ls_data.assert_called_once_with(["src", "pipe"])

    def test_execute_raises_value_error_when_request_missing(
        self, mock_file_indexer_service: MagicMock
    ):
        """Test that execute raises ValueError when validated_request is None."""
        action = LsAction(
            file_indexer_service=mock_file_indexer_service,
            validated_request=None,
        )

        with pytest.raises(ValueError, match="Request is required"):
            action.execute()
