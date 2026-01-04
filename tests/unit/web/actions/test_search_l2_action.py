"""Unit tests for SearchL2Action."""

from unittest.mock import MagicMock

import pytest
from pipe.core.models.file_search import SearchL2Response
from pipe.web.actions.fs.search_l2_action import SearchL2Action
from pipe.web.requests.fs.search_l2_request import SearchL2Request


class TestSearchL2Action:
    """Tests for SearchL2Action class."""

    @pytest.fixture
    def mock_file_indexer_service(self) -> MagicMock:
        """Fixture for mocked FileIndexerService."""
        return MagicMock()

    @pytest.fixture
    def valid_request(self) -> SearchL2Request:
        """Fixture for a valid SearchL2Request."""
        return SearchL2Request(
            current_path_list=["src", "components"],
            query="test_query",
        )

    def test_init(
        self, mock_file_indexer_service: MagicMock, valid_request: SearchL2Request
    ) -> None:
        """Test that SearchL2Action initializes correctly."""
        params = {"some": "param"}
        request_data = MagicMock()

        action = SearchL2Action(
            file_indexer_service=mock_file_indexer_service,
            validated_request=valid_request,
            params=params,
            request_data=request_data,
        )

        assert action.file_indexer_service == mock_file_indexer_service
        assert action.validated_request == valid_request
        assert action.params == params
        assert action.request_data == request_data

    def test_execute_success(
        self, mock_file_indexer_service: MagicMock, valid_request: SearchL2Request
    ) -> None:
        """Test successful execution of SearchL2Action."""
        # Setup mock response
        mock_response = MagicMock(spec=SearchL2Response)
        mock_file_indexer_service.search_l2_data.return_value = mock_response

        action = SearchL2Action(
            file_indexer_service=mock_file_indexer_service,
            validated_request=valid_request,
        )

        result = action.execute()

        # Verify service call
        mock_file_indexer_service.search_l2_data.assert_called_once_with(
            valid_request.current_path_list, valid_request.query
        )
        assert result == mock_response

    def test_execute_missing_request(
        self, mock_file_indexer_service: MagicMock
    ) -> None:
        """Test that execute raises ValueError when validated_request is missing."""
        action = SearchL2Action(
            file_indexer_service=mock_file_indexer_service,
            validated_request=None,
        )

        with pytest.raises(ValueError, match="Request is required"):
            action.execute()
