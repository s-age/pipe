"""Unit tests for file_exists validator rules."""

from unittest.mock import patch

import pytest
from pipe.web.validators.rules.file_exists import (
    validate_comma_separated_files,
    validate_file_exists,
    validate_list_of_files_exist,
    validate_space_separated_files,
)


class TestValidateFileExists:
    """Tests for validate_file_exists function."""

    @patch("os.path.exists")
    def test_file_exists_success(self, mock_exists):
        """Test that no exception is raised when file exists."""
        mock_exists.return_value = True
        validate_file_exists("existing_file.txt")
        mock_exists.assert_called_once_with("existing_file.txt")

    @patch("os.path.exists")
    def test_file_not_found_raises_value_error(self, mock_exists):
        """Test that ValueError is raised when file does not exist."""
        mock_exists.return_value = False
        with pytest.raises(ValueError, match="File not found: 'non_existent.txt'"):
            validate_file_exists("non_existent.txt")

    @patch("os.path.exists")
    def test_strips_quotes_and_whitespace(self, mock_exists):
        """Test that quotes and whitespace are stripped from the path."""
        mock_exists.return_value = True
        validate_file_exists("  'path/to/file.txt'  ")
        mock_exists.assert_called_once_with("path/to/file.txt")

    @patch("os.path.exists")
    def test_strips_double_quotes(self, mock_exists):
        """Test that double quotes are stripped from the path."""
        mock_exists.return_value = True
        validate_file_exists('"path/to/file.txt"')
        mock_exists.assert_called_once_with("path/to/file.txt")


class TestValidateCommaSeparatedFiles:
    """Tests for validate_comma_separated_files function."""

    def test_empty_string_does_nothing(self):
        """Test that empty string does not trigger validation."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_comma_separated_files("")
            mock_validate.assert_not_called()

    def test_none_does_nothing(self):
        """Test that None does not trigger validation."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_comma_separated_files(None)  # type: ignore
            mock_validate.assert_not_called()

    def test_validates_multiple_files(self):
        """Test that multiple comma-separated files are validated."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_comma_separated_files("file1.txt, file2.txt ,file3.txt")
            assert mock_validate.call_count == 3
            mock_validate.assert_any_call("file1.txt")
            mock_validate.assert_any_call("file2.txt")
            mock_validate.assert_any_call("file3.txt")


class TestValidateSpaceSeparatedFiles:
    """Tests for validate_space_separated_files function."""

    def test_empty_string_does_nothing(self):
        """Test that empty string does not trigger validation."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_space_separated_files("")
            mock_validate.assert_not_called()

    def test_none_does_nothing(self):
        """Test that None does not trigger validation."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_space_separated_files(None)  # type: ignore
            mock_validate.assert_not_called()

    def test_validates_multiple_files_with_spaces(self):
        """Test that multiple space-separated files are validated."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_space_separated_files("file1.txt  file2.txt")
            assert mock_validate.call_count == 2
            mock_validate.assert_any_call("file1.txt")
            mock_validate.assert_any_call("file2.txt")

    def test_respects_quoted_paths_with_spaces(self):
        """Test that quoted paths containing spaces are handled correctly."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_space_separated_files(
                'file1.txt "path with spaces/file2.txt" file3.txt'
            )
            assert mock_validate.call_count == 3
            mock_validate.assert_any_call("file1.txt")
            mock_validate.assert_any_call('"path with spaces/file2.txt"')
            mock_validate.assert_any_call("file3.txt")


class TestValidateListOfFilesExist:
    """Tests for validate_list_of_files_exist function."""

    def test_empty_list_does_nothing(self):
        """Test that empty list does not trigger validation."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_list_of_files_exist([])
            mock_validate.assert_not_called()

    def test_none_does_nothing(self):
        """Test that None does not trigger validation."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_list_of_files_exist(None)  # type: ignore
            mock_validate.assert_not_called()

    def test_validates_list_of_paths(self):
        """Test that all paths in the list are validated."""
        with patch(
            "pipe.web.validators.rules.file_exists.validate_file_exists"
        ) as mock_validate:
            validate_list_of_files_exist(["file1.txt", "  file2.txt  "])
            assert mock_validate.call_count == 2
            mock_validate.assert_any_call("file1.txt")
            mock_validate.assert_any_call("file2.txt")
