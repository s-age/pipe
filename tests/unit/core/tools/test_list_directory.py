"""Unit tests for list_directory tool."""

from unittest.mock import MagicMock, patch

from pipe.core.models.results.list_directory_result import ListDirectoryResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.list_directory import list_directory


class TestListDirectory:
    """Tests for list_directory function."""

    @patch("pipe.core.tools.list_directory.FileRepositoryFactory.create")
    def test_list_directory_success(self, mock_create):
        """Test successful directory listing."""
        # Setup mock repository
        mock_repo = MagicMock()
        mock_repo.list_directory.return_value = (
            ["file1.txt", "file2.py"],
            ["dir1", "dir2"],
        )
        mock_create.return_value = mock_repo

        # Execute
        result = list_directory(path="some/path", ignore=["*.tmp"])

        # Verify
        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, ListDirectoryResult)
        assert result.data.files == ["file1.txt", "file2.py"]
        assert result.data.directories == ["dir1", "dir2"]
        assert result.error is None

        # Verify repository call
        mock_create.assert_called_once()
        mock_repo.list_directory.assert_called_once_with("some/path", ignore=["*.tmp"])

    @patch("pipe.core.tools.list_directory.FileRepositoryFactory.create")
    def test_list_directory_no_ignore(self, mock_create):
        """Test directory listing without ignore parameter."""
        # Setup mock repository
        mock_repo = MagicMock()
        mock_repo.list_directory.return_value = ([], [])
        mock_create.return_value = mock_repo

        # Execute
        result = list_directory(path="empty/dir")

        # Verify
        assert result.is_success
        mock_repo.list_directory.assert_called_once_with("empty/dir", ignore=None)

    @patch("pipe.core.tools.list_directory.FileRepositoryFactory.create")
    def test_list_directory_failure(self, mock_create):
        """Test directory listing failure handling."""
        # Setup mock repository to raise an exception
        mock_repo = MagicMock()
        mock_repo.list_directory.side_effect = Exception("Permission denied")
        mock_create.return_value = mock_repo

        # Execute
        result = list_directory(path="restricted/path")

        # Verify
        assert isinstance(result, ToolResult)
        assert not result.is_success
        assert result.data is None
        assert (
            "Failed to list directory restricted/path: Permission denied"
            in result.error
        )
