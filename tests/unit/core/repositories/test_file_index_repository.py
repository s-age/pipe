import os
from unittest.mock import patch

import pytest
from pipe.core.models.file_search import PrefetchResult
from pipe.core.repositories.file_index_repository import FileIndexRepository
from whoosh.index import open_dir


@pytest.fixture
def repository(tmp_path):
    """Create a FileIndexRepository with temporary directories."""
    base_path = tmp_path / "base"
    index_dir = tmp_path / "index"
    base_path.mkdir()

    # Create sample file structure
    (base_path / "file1.txt").write_text("content 1")
    (base_path / "dir1").mkdir()
    (base_path / "dir1" / "file2.py").write_text("print('hello')")
    (base_path / "dir1" / "subdir1").mkdir()
    (base_path / "dir1" / "subdir1" / "file3.md").write_text("# Markdown")
    (base_path / "dir2").mkdir()
    (base_path / "dir2" / "ignored.log").write_text("log content")

    # Create .gitignore
    (base_path / ".gitignore").write_text("*.log\ndir2/ignored.log\n")

    return FileIndexRepository(base_path=str(base_path), index_dir=str(index_dir))


class TestFileIndexRepositoryCreate:
    """Test FileIndexRepository.create_index() method."""

    def test_create_index_success(self, repository):
        """Test that create_index() correctly indexes files and directories."""
        repository.create_index()

        assert os.path.exists(repository.index_dir)

        ix = open_dir(repository.index_dir)
        with ix.searcher() as searcher:
            # Expected docs:
            # file1.txt, dir1, dir1/file2.py, dir1/subdir1, dir2, .gitignore, etc.
            # Total: 7
            assert searcher.doc_count() == 7

            # Check specific files
            assert searcher.document(filename="file1.txt") is not None
            assert searcher.document(filename="file2.py") is not None
            assert (
                searcher.document(filename="ignored.log") is None
            )  # Should be ignored

            # Check directories
            assert searcher.document(filename="dir1", is_dir=True) is not None
            assert searcher.document(filename="subdir1", is_dir=True) is not None

    def test_create_index_respects_gitignore(self, repository):
        """Test that files matching .gitignore patterns are excluded."""
        repository.create_index()

        ix = open_dir(repository.index_dir)
        with ix.searcher() as searcher:
            assert searcher.document(filename="ignored.log") is None

    def test_create_index_handles_missing_base_path(self, tmp_path):
        """Test that create_index() raises ValueError if base_path does not exist."""
        repo = FileIndexRepository(
            base_path=str(tmp_path / "nonexistent"), index_dir=str(tmp_path / "index")
        )

        with pytest.raises(ValueError, match="Base path does not exist"):
            repo.create_index()

    @patch("os.makedirs")
    def test_init_handles_index_dir_creation_failure(self, mock_makedirs, tmp_path):
        """Test that __init__ raises RuntimeError if index directory creation fails."""
        mock_makedirs.side_effect = OSError("Permission denied")

        with pytest.raises(RuntimeError, match="Failed to create index directory"):
            FileIndexRepository(
                base_path=str(tmp_path / "base"), index_dir=str(tmp_path / "index")
            )


class TestFileIndexRepositorySearchL1:
    """Test FileIndexRepository.search_l1_candidates() method."""

    def test_search_root_directory(self, repository):
        """Test searching in the root directory."""
        repository.create_index()

        # Search for "dir" in root
        candidates = repository.search_l1_candidates(repository.base_path, "dir")

        assert len(candidates) == 2
        names = [c.name for c in candidates]
        assert "dir1" in names
        assert "dir2" in names

    def test_search_partial_match(self, repository):
        """Test partial matching of filenames."""
        repository.create_index()

        # Search for "file" (should match file1.txt)
        candidates = repository.search_l1_candidates(repository.base_path, "file")

        assert len(candidates) == 1
        assert candidates[0].name == "file1.txt"

    def test_search_empty_query_returns_all(self, repository):
        """Test that empty query returns all entries in parent."""
        repository.create_index()

        candidates = repository.search_l1_candidates(repository.base_path, "")

        # Should return file1.txt, dir1, dir2, .gitignore
        assert len(candidates) == 4
        names = [c.name for c in candidates]
        assert "file1.txt" in names
        assert "dir1" in names
        assert "dir2" in names
        assert ".gitignore" in names

    def test_search_subdirectory(self, repository):
        """Test searching within a subdirectory."""
        repository.create_index()

        dir1_path = os.path.join(repository.base_path, "dir1")
        candidates = repository.search_l1_candidates(dir1_path, "sub")

        assert len(candidates) == 1
        assert candidates[0].name == "subdir1"


class TestFileIndexRepositoryL2Prefetch:
    """Test FileIndexRepository.get_l2_prefetched_data() method."""

    def test_prefetch_multiple_directories(self, repository):
        """Test prefetching data for multiple directories."""
        repository.create_index()

        result = repository.get_l2_prefetched_data(
            ["dir1", "dir2"], repository.base_path
        )

        assert isinstance(result, PrefetchResult)
        assert "dir1" in result.data
        assert "dir2" in result.data

        # Check dir1 content (file2.py, subdir1)
        dir1_items = [c.name for c in result.data["dir1"]]
        assert "file2.py" in dir1_items
        assert "subdir1" in dir1_items

        # Check dir2 content (empty because ignored.log is ignored)
        assert len(result.data["dir2"]) == 0


class TestFileIndexRepositoryLsData:
    """Test FileIndexRepository.get_ls_data() method."""

    def test_ls_directory(self, repository):
        """Test listing contents of a directory."""
        repository.create_index()

        dir1_path = os.path.join(repository.base_path, "dir1")
        entries = repository.get_ls_data(dir1_path)

        assert len(entries) == 2
        names = [e.name for e in entries]
        assert "file2.py" in names
        assert "subdir1" in names

        # Verify entry attributes
        file_entry = next(e for e in entries if e.name == "file2.py")
        assert file_entry.is_dir is False
        assert file_entry.size is not None

        dir_entry = next(e for e in entries if e.name == "subdir1")
        assert dir_entry.is_dir is True

    def test_ls_single_file(self, repository):
        """Test getting info for a single file."""
        repository.create_index()

        file_path = os.path.join(repository.base_path, "file1.txt")
        entries = repository.get_ls_data(file_path)

        assert len(entries) == 1
        entry = entries[0]
        assert entry.name == "file1.txt"
        assert entry.is_dir is False
        assert entry.path == file_path

    def test_ls_raises_if_index_missing(self, tmp_path):
        """Test that get_ls_data raises FileNotFoundError if index doesn't exist."""
        # Create repo but don't create index
        base_path = tmp_path / "base"
        base_path.mkdir()
        index_dir = tmp_path / "missing_index"
        repo = FileIndexRepository(base_path=str(base_path), index_dir=str(index_dir))
        # Remove the directory created by __init__
        index_dir.rmdir()

        with pytest.raises(FileNotFoundError, match="Index directory does not exist"):
            repo.get_ls_data(str(base_path))

    def test_ls_handles_corrupt_index(self, repository):
        """Test handling of corrupt index (runtime error)."""
        repository.create_index()

        # Corrupt the index by patching open_dir to raise Exception
        with patch(
            "pipe.core.repositories.file_index_repository.open_dir"
        ) as mock_open:
            mock_open.side_effect = Exception("Index corrupted")

            with pytest.raises(RuntimeError, match="Failed to open index"):
                repository.get_ls_data(repository.base_path)
