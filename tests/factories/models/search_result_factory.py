"""Factory for creating SearchResult test fixtures."""

from pipe.core.models.search_result import SessionSearchResult


class SearchResultFactory:
    """Helper class for creating SearchResult objects in tests."""

    @staticmethod
    def create_session_search_result(
        session_id: str = "test-session-123",
        title: str = "Test Session Title",
        path: str | None = "/path/to/session.json",
        **kwargs,
    ) -> SessionSearchResult:
        """Create a SessionSearchResult object with default test values."""
        return SessionSearchResult(
            session_id=session_id,
            title=title,
            path=path,
            **kwargs,
        )
