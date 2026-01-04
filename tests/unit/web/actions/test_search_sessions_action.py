"""Unit tests for SearchSessionsAction."""

from unittest.mock import MagicMock

import pytest
from pipe.core.models.search_result import SessionSearchResult
from pipe.core.services.search_sessions_service import SearchSessionsService
from pipe.web.action_responses import SearchSessionsResponse
from pipe.web.actions.fs.search_sessions_action import SearchSessionsAction
from pipe.web.requests.search_sessions import SearchSessionsRequest


class TestSearchSessionsAction:
    """Tests for SearchSessionsAction."""

    @pytest.fixture
    def mock_service(self) -> MagicMock:
        """Create a mock SearchSessionsService."""
        return MagicMock(spec=SearchSessionsService)

    def test_init(self, mock_service: MagicMock):
        """Test initialization of SearchSessionsAction."""
        request = SearchSessionsRequest(query="test query")
        action = SearchSessionsAction(
            search_sessions_service=mock_service, validated_request=request
        )
        assert action.search_sessions_service == mock_service
        assert action.validated_request == request

    def test_execute_success(self, mock_service: MagicMock):
        """Test successful execution of SearchSessionsAction."""
        # Setup
        request = SearchSessionsRequest(query="test query")
        expected_results = [
            SessionSearchResult(
                session_id="session-1", title="Title 1", path="/path/1.json"
            )
        ]
        mock_service.search.return_value = expected_results
        action = SearchSessionsAction(
            search_sessions_service=mock_service, validated_request=request
        )

        # Execute
        response = action.execute()

        # Verify
        assert isinstance(response, SearchSessionsResponse)
        assert response.results == expected_results
        mock_service.search.assert_called_once_with("test query")

    def test_execute_missing_request(self, mock_service: MagicMock):
        """Test execution raises ValueError when request is missing."""
        action = SearchSessionsAction(search_sessions_service=mock_service)
        with pytest.raises(ValueError, match="Request is required"):
            action.execute()

    def test_execute_empty_results(self, mock_service: MagicMock):
        """Test execution with no search results."""
        # Setup
        request = SearchSessionsRequest(query="test query")
        mock_service.search.return_value = []
        action = SearchSessionsAction(
            search_sessions_service=mock_service, validated_request=request
        )

        # Execute
        response = action.execute()

        # Verify
        assert isinstance(response, SearchSessionsResponse)
        assert response.results == []
        mock_service.search.assert_called_once_with("test query")
