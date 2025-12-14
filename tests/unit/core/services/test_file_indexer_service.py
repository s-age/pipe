import os
from unittest.mock import MagicMock

import pytest
from pipe.core.models.file_search import (  # noqa: F401
    Level1Candidate,
    LsEntry,
    SearchL2Response,
)
from pipe.core.services.file_indexer_service import FileIndexerService

TEST_BASE_PATH = "/tmp/test_project_root"


@pytest.fixture
def mock_repository():
    repo_instance = MagicMock()
    repo_instance.base_path = TEST_BASE_PATH
    return repo_instance


@pytest.fixture
def file_indexer_service(mock_repository):
    return FileIndexerService(repository=mock_repository)


def test_create_index(file_indexer_service, mock_repository):
    file_indexer_service.create_index()
    mock_repository.create_index.assert_called_once()


def test_search_l2_data_root_path(file_indexer_service, mock_repository):
    mock_repository.search_l1_candidates.return_value = [
        Level1Candidate(name="dir1", is_dir=True, path_segment="dir1"),
        Level1Candidate(name="file1.txt", is_dir=False, path_segment="file1.txt"),
    ]
    mock_repository.get_l2_prefetched_data.return_value = {
        "dir1": [
            Level1Candidate(name="subdir1", is_dir=True, path_segment="subdir1"),
            Level1Candidate(name="file2.py", is_dir=False, path_segment="file2.py"),
        ]
    }

    response = file_indexer_service.search_l2_data([], "test")

    mock_repository.search_l1_candidates.assert_called_once_with(TEST_BASE_PATH, "test")
    mock_repository.get_l2_prefetched_data.assert_called_once_with(
        ["dir1"], TEST_BASE_PATH
    )
    assert isinstance(response, SearchL2Response)
    assert len(response.level_1_candidates) == 2
    assert "dir1" in response.level_2_prefetched


def test_search_l2_data_nested_path(file_indexer_service, mock_repository):
    mock_repository.search_l1_candidates.return_value = [
        Level1Candidate(name="subdir1", is_dir=True, path_segment="subdir1")
    ]
    mock_repository.get_l2_prefetched_data.return_value = {
        "subdir1": [
            Level1Candidate(name="file3.md", is_dir=False, path_segment="file3.md")
        ]
    }

    current_path = ["dir1"]
    expected_parent_path = os.path.join(TEST_BASE_PATH, "dir1")
    response = file_indexer_service.search_l2_data(current_path, "sub")

    mock_repository.search_l1_candidates.assert_called_once_with(
        expected_parent_path, "sub"
    )
    mock_repository.get_l2_prefetched_data.assert_called_once_with(
        ["subdir1"], expected_parent_path
    )
    assert isinstance(response, SearchL2Response)
    assert len(response.level_1_candidates) == 1
    assert "subdir1" in response.level_2_prefetched


def test_get_ls_data_file(file_indexer_service, mock_repository):
    mock_repository.get_ls_data.return_value = [
        LsEntry(
            name="file1.txt",
            is_dir=False,
            size=100,
            last_modified=12345.0,
            path=os.path.join(TEST_BASE_PATH, "file1.txt"),
        )
    ]

    final_path = ["file1.txt"]
    expected_full_path = os.path.join(TEST_BASE_PATH, "file1.txt")
    response = file_indexer_service.get_ls_data(final_path)

    mock_repository.get_ls_data.assert_called_once_with(expected_full_path)
    assert len(response) == 1
    assert response[0].name == "file1.txt"


def test_get_ls_data_directory(file_indexer_service, mock_repository):
    mock_repository.get_ls_data.return_value = [
        LsEntry(
            name="subdir1",
            is_dir=True,
            size=None,
            last_modified=12346.0,
            path=os.path.join(TEST_BASE_PATH, "dir1", "subdir1"),
        ),
        LsEntry(
            name="file2.py",
            is_dir=False,
            size=50,
            last_modified=12347.0,
            path=os.path.join(TEST_BASE_PATH, "dir1", "file2.py"),
        ),
    ]

    final_path = ["dir1"]
    expected_full_path = os.path.join(TEST_BASE_PATH, "dir1")
    response = file_indexer_service.get_ls_data(final_path)

    mock_repository.get_ls_data.assert_called_once_with(expected_full_path)
    assert len(response) == 2
    assert any(e.name == "subdir1" for e in response)
    assert any(e.name == "file2.py" for e in response)
