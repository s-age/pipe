"""Unit tests for write_file tool."""

from unittest.mock import MagicMock, patch

from pipe.core.models.results.write_file_result import WriteFileResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.write_file import write_file


class TestWriteFile:
    """Tests for write_file function."""

    @patch("pipe.core.tools.write_file.FileRepositoryFactory.create")
    def test_write_file_new_file(self, mock_repo_factory):
        """Test writing a new file (no existing file)."""
        # Setup
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = False

        file_path = "test.txt"
        content = "new content"

        # Execute
        result = write_file(file_path, content)

        # Verify
        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, WriteFileResult)
        assert result.data.status == "success"
        assert f"File written successfully: {file_path}" in result.data.message
        assert result.data.diff is None

        mock_repo.write_text.assert_called_once_with(file_path, content)
        mock_repo.read_text.assert_not_called()

    @patch("pipe.core.tools.write_file.difflib.unified_diff")
    @patch("pipe.core.tools.write_file.FileRepositoryFactory.create")
    def test_write_file_overwrite(self, mock_repo_factory, mock_diff):
        """Test overwriting an existing file with diff generation."""
        # Setup
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "old content"

        mock_diff.return_value = [
            "--- a/test.txt\n",
            "+++ b/test.txt\n",
            "-old content\n",
            "+new content\n",
        ]

        file_path = "test.txt"
        content = "new content"

        # Execute
        result = write_file(file_path, content)

        # Verify
        assert result.is_success
        assert result.data.status == "success"
        assert result.data.diff is not None
        assert "-old content" in result.data.diff
        assert "+new content" in result.data.diff
        assert "Diff:" in result.data.message

        mock_repo.read_text.assert_called_once_with(file_path)
        mock_repo.write_text.assert_called_once_with(file_path, content)
        mock_diff.assert_called_once()

    @patch("pipe.core.tools.write_file.FileRepositoryFactory.create")
    def test_write_file_with_project_root(self, mock_repo_factory):
        """Test write_file with explicit project_root."""
        # Setup
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = False

        file_path = "test.txt"
        content = "content"
        project_root = "/tmp/project"

        # Execute
        write_file(file_path, content, project_root=project_root)

        # Verify
        # project_root is normalized with abspath
        import os

        expected_root = os.path.abspath(project_root)
        mock_repo_factory.assert_called_once_with(expected_root)

    @patch("pipe.core.tools.write_file.FileRepositoryFactory.create")
    def test_write_file_exception_handling(self, mock_repo_factory):
        """Test exception handling in write_file."""
        # Setup
        mock_repo_factory.side_effect = Exception("Repository creation failed")

        file_path = "test.txt"
        content = "content"

        # Execute
        result = write_file(file_path, content)

        # Verify
        assert not result.is_success
        assert "Failed to write file" in result.error
        assert "Repository creation failed" in result.error

    @patch("pipe.core.tools.write_file.FileRepositoryFactory.create")
    def test_write_file_not_a_file(self, mock_repo_factory):
        """Test writing when path exists but is not a file (e.g., directory)."""
        # Setup
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = False

        file_path = "test_dir"
        content = "content"

        # Execute
        result = write_file(file_path, content)

        # Verify
        assert result.is_success
        assert result.data.diff is None
        mock_repo.read_text.assert_not_called()
        mock_repo.write_text.assert_called_once_with(file_path, content)
