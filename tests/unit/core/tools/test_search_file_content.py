"""Unit tests for search_file_content tool."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.search_file_content_result import (
    FileMatchItem,
    SearchFileContentResult,
)
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.search_file_content import search_file_content


class TestSearchFileContent:
    """Tests for search_file_content function."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture for a mocked repository."""
        repo = MagicMock()
        repo.exists.return_value = True
        repo.is_dir.return_value = True
        return repo

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_success(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test successful search with matches."""
        mock_get_root.return_value = "/project/root"
        mock_repo_create.return_value = mock_repo

        # Setup mock files and content
        mock_repo.glob.return_value = [
            "/project/root/file1.txt",
            "/project/root/file2.txt",
        ]
        mock_repo.is_file.side_effect = lambda p: True
        mock_repo.read_text.side_effect = [
            "line1\npattern here\nline3",
            "no match here\nanother line",
        ]

        result = search_file_content(pattern="pattern", path="/project/root")

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, SearchFileContentResult)
        assert isinstance(result.data.content, list)
        assert len(result.data.content) == 1

        match = result.data.content[0]
        assert isinstance(match, FileMatchItem)
        assert match.file_path == "file1.txt"
        assert match.line_number == 2
        assert match.line_content == "pattern here"

        mock_repo.exists.assert_called_once_with("/project/root")
        mock_repo.glob.assert_called_once_with(
            "**/*", search_path="/project/root", recursive=True, respect_gitignore=True
        )

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_no_matches(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test search with no matches found."""
        mock_get_root.return_value = "/project/root"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = ["/project/root/file1.txt"]
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "no match here"

        result = search_file_content(pattern="pattern", path="/project/root")

        assert result.is_success
        assert result.data.content == "No matches found."

    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_invalid_regex(self, mock_repo_create):
        """Test handling of invalid regex pattern."""
        result = search_file_content(pattern="[")  # Invalid regex

        assert not result.is_success
        assert "Invalid regex pattern" in result.error

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_path_not_found(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test when search path does not exist."""
        mock_repo_create.return_value = mock_repo
        mock_repo.exists.return_value = False

        result = search_file_content(pattern="pattern", path="/invalid/path")

        assert not result.is_success
        assert "Search path '/invalid/path' not found" in result.error

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_path_not_dir(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test when search path is not a directory."""
        mock_repo_create.return_value = mock_repo
        mock_repo.is_dir.return_value = False

        result = search_file_content(pattern="pattern", path="/some/file.txt")

        assert not result.is_success
        assert "Search path '/some/file.txt' is not a directory" in result.error

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_skip_binary(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test skipping binary files (UnicodeDecodeError)."""
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = [
            "/project/root/binary.bin",
            "/project/root/text.txt",
        ]
        mock_repo.is_file.return_value = True
        mock_repo.read_text.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, ""),
            "pattern here",
        ]

        result = search_file_content(pattern="pattern", path="/project/root")

        assert result.is_success
        assert len(result.data.content) == 1
        assert result.data.content[0].file_path == "text.txt"

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_file_read_error(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test handling of general file read errors."""
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = ["/project/root/error.txt"]
        mock_repo.is_file.return_value = True
        mock_repo.read_text.side_effect = Exception("Read error")

        result = search_file_content(pattern="pattern", path="/project/root")

        assert result.is_success
        assert len(result.data.content) == 1
        assert "Error reading file" in result.data.content[0].error
        assert "Read error" in result.data.content[0].error

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_custom_include(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test using a custom include pattern."""
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = []

        search_file_content(pattern="pattern", include="*.py", path="/project/root")

        mock_repo.glob.assert_called_once_with(
            "*.py", search_path="/project/root", recursive=True, respect_gitignore=True
        )

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_default_path(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test using default path (project root)."""
        mock_get_root.return_value = "/default/root"
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = []

        search_file_content(pattern="pattern")

        mock_get_root.assert_called_once()
        mock_repo.exists.assert_called_once_with("/default/root")
        mock_repo.glob.assert_called_once_with(
            "**/*", search_path="/default/root", recursive=True, respect_gitignore=True
        )

    @patch("pipe.core.tools.search_file_content.get_project_root")
    @patch("pipe.core.tools.search_file_content.FileRepositoryFactory.create")
    def test_search_file_content_skips_non_file(
        self, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test that non-file paths returned by glob are skipped."""
        mock_get_root.return_value = "/project/root"
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = ["/project/root/dir"]
        mock_repo.is_file.return_value = False

        result = search_file_content(pattern="pattern")

        assert result.is_success
        assert result.data.content == "No matches found."
        mock_repo.read_text.assert_not_called()

    @patch("pipe.core.tools.search_file_content.get_project_root")
    def test_search_file_content_general_exception(self, mock_get_root):
        """Test handling of unexpected exceptions."""
        mock_get_root.side_effect = Exception("Unexpected error")

        result = search_file_content(pattern="pattern")

        assert not result.is_success
        assert "Error inside search_file_content tool" in result.error
        assert "Unexpected error" in result.error
