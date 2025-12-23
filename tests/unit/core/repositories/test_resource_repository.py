from pathlib import Path
from unittest.mock import patch

import pytest
from pipe.core.repositories.resource_repository import ResourceRepository


@pytest.fixture
def repository(tmp_path):
    """Create a ResourceRepository instance with a temporary project root."""
    return ResourceRepository(project_root=str(tmp_path))


@pytest.fixture
def test_file(tmp_path):
    """Create a test file within the temporary project root."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world", encoding="utf-8")
    return file_path


class TestResourceRepositoryReadText:
    """Test cases for ResourceRepository.read_text method."""

    def test_read_text_success(self, repository, test_file):
        """Test reading an existing file successfully."""
        content = repository.read_text(str(test_file))
        assert content == "hello world"

    def test_read_text_with_custom_allowed_root(self, tmp_path):
        """Test reading a file with a custom allowed root."""
        custom_root = tmp_path / "custom"
        custom_root.mkdir()
        file_path = custom_root / "custom.txt"
        file_path.write_text("custom content", encoding="utf-8")

        # Repository project_root is tmp_path, but we specify custom_root
        repo = ResourceRepository(project_root=str(tmp_path))
        content = repo.read_text(str(file_path), allowed_root=str(custom_root))
        assert content == "custom content"

    def test_read_text_outside_root(self, repository, tmp_path):
        """Test that reading a file outside the allowed root raises ValueError."""
        outside_dir = tmp_path.parent / "outside"
        outside_dir.mkdir(exist_ok=True)
        outside_file = outside_dir / "secret.txt"
        outside_file.write_text("secret", encoding="utf-8")

        with pytest.raises(ValueError, match="Access denied"):
            repository.read_text(str(outside_file))

    def test_read_text_file_not_found(self, repository, tmp_path):
        """Test that reading a non-existent file raises FileNotFoundError."""
        non_existent = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError, match="File not found"):
            repository.read_text(str(non_existent))

    def test_read_text_is_directory(self, repository, tmp_path):
        """Test that attempting to read a directory raises ValueError."""
        dir_path = tmp_path / "sub_dir"
        dir_path.mkdir()
        with pytest.raises(ValueError, match="Path is not a file"):
            repository.read_text(str(dir_path))

    def test_read_text_os_error(self, repository, test_file):
        """Test that reading a file that raises OSError is handled."""
        with patch("builtins.open", side_effect=OSError("Read error")):
            with pytest.raises(OSError, match="Failed to read file"):
                repository.read_text(str(test_file))


class TestResourceRepositoryExists:
    """Test cases for ResourceRepository.exists method."""

    def test_exists_true(self, repository, test_file):
        """Test that an existing file within root returns True."""
        assert repository.exists(str(test_file)) is True

    def test_exists_false_not_found(self, repository, tmp_path):
        """Test that a non-existent file returns False."""
        non_existent = tmp_path / "missing.txt"
        assert repository.exists(str(non_existent)) is False

    def test_exists_false_outside_root(self, repository, tmp_path):
        """Test that a file outside the allowed root returns False."""
        outside_dir = tmp_path.parent / "outside_exists"
        outside_dir.mkdir(exist_ok=True)
        outside_file = outside_dir / "exists.txt"
        outside_file.write_text("exists", encoding="utf-8")

        assert repository.exists(str(outside_file)) is False

    def test_exists_false_is_directory(self, repository, tmp_path):
        """Test that a directory returns False."""
        dir_path = tmp_path / "a_directory"
        dir_path.mkdir()
        assert repository.exists(str(dir_path)) is False


class TestResourceRepositoryValidatePath:
    """Test cases for ResourceRepository.validate_path method."""

    def test_validate_path_valid(self, repository, tmp_path):
        """Test that a path within root is validated successfully."""
        valid_path = tmp_path / "valid.txt"
        assert repository.validate_path(str(valid_path)) is True

    def test_validate_path_invalid_outside_root(self, repository, tmp_path):
        """Test that a path outside root fails validation."""
        outside_path = tmp_path.parent / "outside.txt"
        assert repository.validate_path(str(outside_path)) is False

    def test_validate_path_absolute_within_root(self, repository, tmp_path):
        """Test that an absolute path within root is validated successfully."""
        abs_path = (tmp_path / "abs.txt").resolve()
        assert repository.validate_path(str(abs_path)) is True


class TestResourceRepositoryGetAbsolutePath:
    """Test cases for ResourceRepository.get_absolute_path method."""

    def test_get_absolute_path_success(self, repository, tmp_path):
        """Test getting absolute path for a valid file path."""
        file_path = str(tmp_path / "some/file.txt")
        expected = str(Path(file_path).resolve())
        assert repository.get_absolute_path(file_path) == expected

    def test_get_absolute_path_outside_root(self, repository, tmp_path):
        """Test that getting absolute path outside root raises ValueError."""
        outside_path = str(tmp_path.parent / "outside.txt")
        with pytest.raises(ValueError, match="Access denied"):
            repository.get_absolute_path(outside_path)
