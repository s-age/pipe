"""Unit tests for the glob tool."""

from unittest.mock import MagicMock, patch

from pipe.core.models.results.glob_result import GlobResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.glob import glob


class TestGlobTool:
    """Tests for the glob function."""

    @patch("pipe.core.tools.glob.FileRepositoryFactory.create")
    @patch("pipe.core.tools.glob.get_project_root")
    def test_glob_success(
        self, mock_get_root: MagicMock, mock_repo_factory: MagicMock
    ) -> None:
        """Test successful glob execution with default parameters."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.glob.return_value = [
            "/project/root/file1.py",
            "/project/root/dir/file2.py",
        ]

        # Execute
        result = glob(pattern="**/*.py")

        # Verify
        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, GlobResult)
        assert result.data is not None
        # Relative paths: file1.py, dir/file2.py
        # Sorted descending: file1.py, dir/file2.py
        assert result.data.content == "file1.py\ndir/file2.py"

        mock_repo.glob.assert_called_once_with(
            "**/*.py",
            search_path="/project/root",
            recursive=True,
            respect_gitignore=True,
        )

    @patch("pipe.core.tools.glob.FileRepositoryFactory.create")
    @patch("pipe.core.tools.glob.get_project_root")
    def test_glob_with_custom_path(
        self, mock_get_root: MagicMock, mock_repo_factory: MagicMock
    ) -> None:
        """Test glob with a custom search path."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.glob.return_value = ["/project/root/src/main.py"]

        # Execute
        result = glob(pattern="*.py", path="/project/root/src")

        # Verify
        assert result.is_success
        assert result.data is not None
        assert result.data.content == "src/main.py"
        mock_repo.glob.assert_called_once_with(
            "*.py",
            search_path="/project/root/src",
            recursive=True,
            respect_gitignore=True,
        )

    @patch("pipe.core.tools.glob.FileRepositoryFactory.create")
    @patch("pipe.core.tools.glob.get_project_root")
    def test_glob_non_recursive(
        self, mock_get_root: MagicMock, mock_repo_factory: MagicMock
    ) -> None:
        """Test glob with recursive=False."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.glob.return_value = []

        # Execute
        result = glob(pattern="*.py", recursive=False)

        # Verify
        assert result.is_success
        mock_repo.glob.assert_called_once_with(
            "*.py",
            search_path="/project/root",
            recursive=False,
            respect_gitignore=True,
        )

    @patch("pipe.core.tools.glob.FileRepositoryFactory.create")
    @patch("pipe.core.tools.glob.get_project_root")
    def test_glob_sorting(
        self, mock_get_root: MagicMock, mock_repo_factory: MagicMock
    ) -> None:
        """Test that results are sorted descending by name."""
        # Setup
        mock_get_root.return_value = "/project/root"
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.glob.return_value = [
            "/project/root/a.py",
            "/project/root/c.py",
            "/project/root/b.py",
        ]

        # Execute
        result = glob(pattern="*.py")

        # Verify
        # Relative paths: a.py, c.py, b.py
        # Sorted descending: c.py, b.py, a.py
        assert result.data is not None
        assert result.data.content == "c.py\nb.py\na.py"

    @patch("pipe.core.tools.glob.FileRepositoryFactory.create")
    @patch("pipe.core.tools.glob.get_project_root")
    def test_glob_exception_handling(
        self, mock_get_root: MagicMock, mock_repo_factory: MagicMock
    ) -> None:
        """Test exception handling in glob tool."""
        # Setup
        mock_get_root.side_effect = Exception("Unexpected error")

        # Execute
        result = glob(pattern="*.py")

        # Verify
        assert not result.is_success
        assert result.error is not None
        assert "Error inside glob tool: Unexpected error" in result.error
