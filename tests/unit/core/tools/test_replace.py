from unittest.mock import MagicMock, patch

from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.replace import replace


class TestReplace:
    """Tests for the replace tool."""

    @patch("pipe.core.tools.replace.FileRepositoryFactory.create")
    def test_replace_success(self, mock_repo_factory):
        """Test successful text replacement."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo

        file_path = "test.txt"
        old_content = "line1\nline2\nline3"
        old_string = "line2"
        new_string = "new_line2"

        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = old_content

        result = replace(file_path, "instruction", old_string, new_string)

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert result.data is not None
        assert result.data.status == "success"
        assert "Text replaced successfully" in result.data.message
        assert result.data.diff is not None
        assert "line2" in result.data.diff
        assert "new_line2" in result.data.diff

        mock_repo.write_text.assert_called_once_with(
            file_path, "line1\nnew_line2\nline3"
        )

    @patch("pipe.core.tools.replace.FileRepositoryFactory.create")
    def test_replace_no_change(self, mock_repo_factory):
        """Test replacement when old and new strings are identical."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo

        file_path = "test.txt"
        content = "line1\nline2\nline3"

        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = content

        result = replace(file_path, "instruction", "line2", "line2")

        assert result.is_success
        assert result.data is not None
        assert result.data.status == "success"
        assert result.data.diff is None
        mock_repo.write_text.assert_called_once_with(file_path, content)

    @patch("pipe.core.tools.replace.FileRepositoryFactory.create")
    def test_replace_file_not_found(self, mock_repo_factory):
        """Test error when file does not exist."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = False

        result = replace("missing.txt", "instruction", "old", "new")

        assert not result.is_success
        assert result.error is not None
        assert "File not found" in result.error

    @patch("pipe.core.tools.replace.FileRepositoryFactory.create")
    def test_replace_not_a_file(self, mock_repo_factory):
        """Test error when path is not a file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = False

        result = replace("dir/", "instruction", "old", "new")

        assert not result.is_success
        assert result.error is not None
        assert "Path is not a file" in result.error

    @patch("pipe.core.tools.replace.FileRepositoryFactory.create")
    def test_replace_old_string_not_found(self, mock_repo_factory):
        """Test error when old string is not found in file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "content"

        result = replace("test.txt", "instruction", "missing", "new")

        assert not result.is_success
        assert result.error is not None
        assert "Old string not found" in result.error

    @patch("pipe.core.tools.replace.FileRepositoryFactory.create")
    def test_replace_first_occurrence_only(self, mock_repo_factory):
        """Test that only the first occurrence is replaced."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo

        file_path = "test.txt"
        content = "target target target"

        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = content

        result = replace(file_path, "instruction", "target", "replacement")

        assert result.is_success
        mock_repo.write_text.assert_called_once_with(
            file_path, "replacement target target"
        )

    @patch("pipe.core.tools.replace.FileRepositoryFactory.create")
    def test_replace_exception(self, mock_repo_factory):
        """Test exception handling during replacement."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.side_effect = Exception("Read error")

        result = replace("test.txt", "instruction", "old", "new")

        assert not result.is_success
        assert result.error is not None
        assert "Failed to replace text" in result.error
        assert "Read error" in result.error
