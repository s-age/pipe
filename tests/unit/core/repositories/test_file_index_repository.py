import os
import shutil

import pytest
from pipe.core.repositories.file_index_repository import FileIndexRepository
from whoosh.index import open_dir

# Test index directory and base path
TEST_INDEX_DIR = "./test_whoosh_index"
TEST_BASE_PATH = "./test_data_files"


@pytest.fixture(scope="module")
def setup_repository():
    # Clean up directories before tests
    if os.path.exists(TEST_INDEX_DIR):
        shutil.rmtree(TEST_INDEX_DIR)
    if os.path.exists(TEST_BASE_PATH):
        shutil.rmtree(TEST_BASE_PATH)

    os.makedirs(TEST_BASE_PATH)
    os.makedirs(os.path.join(TEST_BASE_PATH, "dir1"))
    os.makedirs(os.path.join(TEST_BASE_PATH, "dir1", "subdir1"))
    os.makedirs(os.path.join(TEST_BASE_PATH, "dir2"))

    with open(os.path.join(TEST_BASE_PATH, "file1.txt"), "w") as f:
        f.write("content of file1")
    with open(os.path.join(TEST_BASE_PATH, "dir1", "file2.py"), "w") as f:
        f.write("print('hello')")
    with open(os.path.join(TEST_BASE_PATH, "dir1", "subdir1", "file3.md"), "w") as f:
        f.write("# Markdown content")
    with open(os.path.join(TEST_BASE_PATH, "dir2", "ignored.log"), "w") as f:
        f.write("log content")

    # Create .gitignore file
    with open(os.path.join(TEST_BASE_PATH, ".gitignore"), "w") as f:
        f.write("*.log\n")
        f.write("dir2/ignored.log\n")

    repo = FileIndexRepository(base_path=TEST_BASE_PATH, index_dir=TEST_INDEX_DIR)
    repo.create_index()
    yield repo

    # Clean up directories after tests
    if os.path.exists(TEST_INDEX_DIR):
        shutil.rmtree(TEST_INDEX_DIR)
    if os.path.exists(TEST_BASE_PATH):
        shutil.rmtree(TEST_BASE_PATH)


def test_create_index(setup_repository):
    ix = open_dir(TEST_INDEX_DIR)
    with ix.searcher() as searcher:
        # Verify the number of indexed documents
        # Confirm that ignored.log is ignored by .gitignore
        assert (
            searcher.doc_count() == 7
        )  # dir1, dir2, file1.txt, .gitignore, subdir1, file2.py, file3.md

        # Verify file existence
        assert searcher.document(filename="file1.txt") is not None
        assert searcher.document(filename="file2.py") is not None
        assert searcher.document(filename="file3.md") is not None
        assert (
            searcher.document(filename="ignored.log") is None
        )  # Ignored by .gitignore

        # Verify directory existence
        assert searcher.document(filename="dir1", is_dir=True) is not None
        assert searcher.document(filename="subdir1", is_dir=True) is not None
        assert searcher.document(filename="dir2", is_dir=True) is not None


def test_search_l1_candidates(setup_repository):
    repo = setup_repository

    # Search directly under the project root
    candidates = repo.search_l1_candidates(TEST_BASE_PATH, "dir")
    assert len(candidates) == 2  # dir1, dir2
    assert any(c.name == "dir1" for c in candidates)
    assert any(c.name == "dir2" for c in candidates)

    # Partial match search
    candidates = repo.search_l1_candidates(TEST_BASE_PATH, "file")
    assert len(candidates) == 1  # file1.txt
    assert any(c.name == "file1.txt" for c in candidates)

    # Search directly under dir1
    candidates = repo.search_l1_candidates(os.path.join(TEST_BASE_PATH, "dir1"), "sub")
    assert len(candidates) == 1  # subdir1
    assert any(c.name == "subdir1" for c in candidates)

    # Non-existent query
    candidates = repo.search_l1_candidates(TEST_BASE_PATH, "nonexistent")
    assert len(candidates) == 0


def test_get_l2_prefetched_data(setup_repository):
    repo = setup_repository

    # Get L2 data for dir1
    prefetched_data = repo.get_l2_prefetched_data(["dir1"], TEST_BASE_PATH)
    assert "dir1" in prefetched_data
    assert len(prefetched_data["dir1"]) == 2  # file2.py, subdir1
    assert any(c.name == "file2.py" for c in prefetched_data["dir1"])
    assert any(c.name == "subdir1" for c in prefetched_data["dir1"])

    # Get L2 data for dir2 (ignored.log is ignored)
    prefetched_data = repo.get_l2_prefetched_data(["dir2"], TEST_BASE_PATH)
    assert "dir2" in prefetched_data
    assert len(prefetched_data["dir2"]) == 0  # Because ignored.log is ignored


def test_get_ls_data(setup_repository):
    repo = setup_repository

    # ls data for directory
    dir1_path = os.path.join(TEST_BASE_PATH, "dir1")
    ls_entries = repo.get_ls_data(dir1_path)
    assert len(ls_entries) == 2  # file2.py, subdir1
    assert any(e.name == "file2.py" for e in ls_entries)
    assert any(e.name == "subdir1" for e in ls_entries)

    # ls data for file
    file1_path = os.path.join(TEST_BASE_PATH, "file1.txt")
    ls_entries = repo.get_ls_data(file1_path)
    assert len(ls_entries) == 1
    assert ls_entries[0].name == "file1.txt"
    assert ls_entries[0].is_dir is False
    assert ls_entries[0].size is not None
    assert ls_entries[0].last_modified is not None

    # Non-existent path
    ls_entries = repo.get_ls_data(os.path.join(TEST_BASE_PATH, "nonexistent"))
    assert len(ls_entries) == 0
