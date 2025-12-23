import os

import pytest
from pipe.core.repositories.sandbox_file_repository import SandboxFileRepository


@pytest.fixture
def repository(tmp_path):
    """Create a SandboxFileRepository with a temporary project root."""
    return SandboxFileRepository(project_root=str(tmp_path))


class TestSandboxFileRepositoryInit:
    """Test initialization of SandboxFileRepository."""

    def test_init_sets_absolute_project_root(self, tmp_path):
        """Test that project_root is converted to an absolute path."""
        # Using relative path for init
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            repo = SandboxFileRepository(project_root=".")
            assert repo.project_root == str(tmp_path.resolve())
        finally:
            os.chdir(original_cwd)

    def test_blocked_paths_initialization(self, repository, tmp_path):
        """Test that blocked_paths are correctly initialized."""
        expected_blocked = [
            os.path.join(str(tmp_path), ".git"),
            os.path.join(str(tmp_path), ".env"),
            os.path.join(str(tmp_path), "setting.yml"),
            os.path.join(str(tmp_path), "__pycache__"),
            os.path.join(str(tmp_path), "roles"),
            os.path.join(str(tmp_path), "rules"),
            os.path.join(str(tmp_path), "sessions"),
            os.path.join(str(tmp_path), "venv"),
        ]
        for path in expected_blocked:
            assert path in repository.blocked_paths


class TestSandboxFileRepositoryValidation:
    """Test path validation logic."""

    def test_validate_path_within_root(self, repository, tmp_path):
        """Test validation of a valid path within project root."""
        test_path = os.path.join(str(tmp_path), "test.txt")
        assert repository._validate_path_for_write(test_path) == os.path.abspath(
            test_path
        )

    def test_validate_path_outside_root(self, repository):
        """Test validation of a path outside project root."""
        with pytest.raises(
            ValueError, match="Running commands outside project root is not allowed"
        ):
            repository._validate_path_for_write("/tmp/outside.txt")

    def test_validate_blocked_path(self, repository, tmp_path):
        """Test validation of a blocked path within project root."""
        blocked_path = os.path.join(str(tmp_path), ".git")
        with pytest.raises(
            ValueError, match="Access denied: Writing to .* is not allowed."
        ):
            repository._validate_path_for_write(blocked_path)

    def test_validate_blocked_subpath(self, repository, tmp_path):
        """Test validation of a subpath of a blocked path."""
        blocked_subpath = os.path.join(str(tmp_path), ".git", "config")
        with pytest.raises(
            ValueError, match="Access denied: Writing to .* is not allowed."
        ):
            repository._validate_path_for_write(blocked_subpath)

    def test_get_absolute_path_read(self, repository):
        """Test getting absolute path for reading (no restriction)."""
        # Read operations should not be restricted to project root
        outside_path = "/tmp/outside.txt"
        assert repository.get_absolute_path(
            outside_path, allow_write=False
        ) == os.path.abspath(outside_path)

    def test_get_absolute_path_write(self, repository, tmp_path):
        """Test getting absolute path for writing (restricted)."""
        valid_path = os.path.join(str(tmp_path), "valid.txt")
        assert repository.get_absolute_path(
            valid_path, allow_write=True
        ) == os.path.abspath(valid_path)

        with pytest.raises(
            ValueError, match="Running commands outside project root is not allowed"
        ):
            repository.get_absolute_path("/tmp/outside.txt", allow_write=True)


class TestSandboxFileRepositoryReadText:
    """Test read_text method."""

    def test_read_text_success(self, repository, tmp_path):
        """Test reading a file successfully."""
        file_path = tmp_path / "read_test.txt"
        content = "Hello, World!"
        file_path.write_text(content, encoding="utf-8")

        assert repository.read_text(str(file_path)) == content

    def test_read_text_with_limit_and_offset(self, repository, tmp_path):
        """Test reading a file with limit and offset."""
        file_path = tmp_path / "limit_test.txt"
        lines = ["Line 1\n", "Line 2\n", "Line 3\n", "Line 4\n"]
        file_path.write_text("".join(lines), encoding="utf-8")

        # Read 2 lines starting from offset 1 (Line 2 and Line 3)
        result = repository.read_text(str(file_path), limit=2, offset=1)
        assert result == "Line 2\nLine 3\n"

    def test_read_text_file_not_found(self, repository):
        """Test reading a non-existent file."""
        with pytest.raises(FileNotFoundError):
            repository.read_text("nonexistent.txt")

    def test_read_text_is_directory(self, repository, tmp_path):
        """Test reading a directory as a file."""
        dir_path = tmp_path / "test_dir"
        dir_path.mkdir()
        with pytest.raises(ValueError, match="Path is not a file"):
            repository.read_text(str(dir_path))


class TestSandboxFileRepositoryWriteText:
    """Test write_text method."""

    def test_write_text_success(self, repository, tmp_path):
        """Test writing text to a file."""
        file_path = os.path.join(str(tmp_path), "write_test.txt")
        content = "Sample content"
        repository.write_text(file_path, content)

        with open(file_path, encoding="utf-8") as f:
            assert f.read() == content

    def test_write_text_creates_directories(self, repository, tmp_path):
        """Test that write_text creates parent directories automatically."""
        nested_path = os.path.join(str(tmp_path), "a", "b", "c", "test.txt")
        content = "Nested content"
        repository.write_text(nested_path, content)

        assert os.path.exists(nested_path)
        with open(nested_path, encoding="utf-8") as f:
            assert f.read() == content

    def test_write_text_restricted(self, repository):
        """Test writing text to a restricted location."""
        with pytest.raises(
            ValueError, match="Running commands outside project root is not allowed"
        ):
            repository.write_text("/tmp/restricted.txt", "content")


class TestSandboxFileRepositoryChecks:
    """Test existence and type check methods."""

    def test_exists(self, repository, tmp_path):
        """Test exists method."""
        file_path = tmp_path / "exists.txt"
        file_path.touch()
        assert repository.exists(str(file_path)) is True
        assert repository.exists(str(tmp_path / "missing.txt")) is False

    def test_is_file(self, repository, tmp_path):
        """Test is_file method."""
        file_path = tmp_path / "file.txt"
        file_path.touch()
        dir_path = tmp_path / "dir"
        dir_path.mkdir()

        assert repository.is_file(str(file_path)) is True
        assert repository.is_file(str(dir_path)) is False

    def test_is_dir(self, repository, tmp_path):
        """Test is_dir method."""
        file_path = tmp_path / "file.txt"
        file_path.touch()
        dir_path = tmp_path / "dir"
        dir_path.mkdir()

        assert repository.is_dir(str(dir_path)) is True
        assert repository.is_dir(str(file_path)) is False


class TestSandboxFileRepositoryListDirectory:
    """Test list_directory method."""

    def test_list_directory_success(self, repository, tmp_path):
        """Test listing directory contents."""
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        (tmp_path / "subdir").mkdir()

        files, dirs = repository.list_directory(str(tmp_path))
        assert files == ["file1.txt", "file2.txt"]
        assert dirs == ["subdir"]

    def test_list_directory_with_ignore(self, repository, tmp_path):
        """Test listing directory contents with ignore patterns."""
        (tmp_path / "file1.txt").touch()
        (tmp_path / "temp_file.tmp").touch()
        (tmp_path / "node_modules").mkdir()

        files, dirs = repository.list_directory(
            str(tmp_path), ignore=["*.tmp", "node_modules"]
        )
        assert files == ["file1.txt"]
        assert dirs == []

    def test_list_directory_not_a_directory(self, repository, tmp_path):
        """Test listing contents of something that is not a directory."""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.touch()
        with pytest.raises(ValueError, match="Path is not a directory"):
            repository.list_directory(str(file_path))


class TestSandboxFileRepositoryGlob:
    """Test glob method."""

    def test_glob_basic(self, repository, tmp_path):
        """Test basic glob matching."""
        (tmp_path / "test1.py").touch()
        (tmp_path / "test2.txt").touch()
        (tmp_path / "other.py").touch()

        results = repository.glob("*.py", search_path=str(tmp_path))
        assert len(results) == 2
        assert any(r.endswith("test1.py") for r in results)
        assert any(r.endswith("other.py") for r in results)

    def test_glob_recursive(self, repository, tmp_path):
        """Test recursive glob matching."""
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "top.py").touch()
        (sub / "bottom.py").touch()

        results = repository.glob("**/*.py", search_path=str(tmp_path), recursive=True)
        assert len(results) == 2
        assert any(r.endswith("top.py") for r in results)
        assert any(r.endswith("bottom.py") for r in results)

    def test_glob_git_failure_handling(self, repository, tmp_path):
        """Test that glob handles git command failure gracefully."""
        import subprocess
        from unittest.mock import patch

        (tmp_path / "test.py").touch()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")
            # Should not raise exception and return results
            results = repository.glob("*.py", search_path=str(tmp_path))
            assert len(results) == 1
            assert results[0].endswith("test.py")

    def test_glob_with_git_ignored_files(self, repository, tmp_path):
        """Test that glob respects git ignored files when they are returned by git."""
        from unittest.mock import MagicMock, patch

        (tmp_path / "normal.py").touch()
        (tmp_path / "ignored.py").touch()

        with patch("subprocess.run") as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "ignored.py"
            mock_run.return_value = mock_process

            results = repository.glob("*.py", search_path=str(tmp_path))
            assert len(results) == 1
            assert results[0].endswith("normal.py")
            assert not any(r.endswith("ignored.py") for r in results)
