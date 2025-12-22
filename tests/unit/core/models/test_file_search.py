import pytest
from pipe.core.models.file_search import (
    FileIndexEntry,
    Level1Candidate,
    LsEntry,
    LsResponse,
    PrefetchResult,
    SearchL2Request,
    SearchL2Response,
)
from pydantic import ValidationError


class TestFileSearchModels:
    """Tests for file search related Pydantic models."""

    def test_file_index_entry_valid(self):
        """Test FileIndexEntry with valid data."""
        data = {
            "path": "/path/to/file.txt",
            "filename": "file.txt",
            "is_dir": False,
            "parent_path_hash": "abc123hash",
            "size": 1024,
            "last_modified": 1609459200.0,
        }
        entry = FileIndexEntry.model_validate(data)
        assert entry.path == "/path/to/file.txt"
        assert entry.is_dir is False
        assert entry.size == 1024

    def test_file_index_entry_optional_fields(self):
        """Test FileIndexEntry with optional fields missing."""
        entry = FileIndexEntry(
            path="/path/to/dir",
            filename="dir",
            is_dir=True,
            parent_path_hash="hash",
        )
        assert entry.size is None
        assert entry.last_modified is None

    def test_file_index_entry_camel_case_serialization(self):
        """Test FileIndexEntry serializes to camelCase."""
        entry = FileIndexEntry(
            path="/path/to/file",
            filename="file",
            is_dir=False,
            parent_path_hash="hash",
            last_modified=123.456,
        )
        dumped = entry.model_dump(by_alias=True)
        assert "parentPathHash" in dumped
        assert "lastModified" in dumped
        assert dumped["parentPathHash"] == "hash"

    def test_level1_candidate_valid(self):
        """Test Level1Candidate validation."""
        data = {"name": "src", "is_dir": True, "path_segment": "src"}
        candidate = Level1Candidate.model_validate(data)
        assert candidate.name == "src"
        assert candidate.is_dir is True

    def test_search_l2_request_valid(self):
        """Test SearchL2Request validation."""
        data = {"current_path_list": ["src", "components"], "query": "button"}
        request = SearchL2Request.model_validate(data)
        assert request.current_path_list == ["src", "components"]
        assert request.query == "button"

    def test_search_l2_request_camel_case(self):
        """Test SearchL2Request from camelCase data."""
        data = {"currentPathList": ["src"], "query": "test"}
        request = SearchL2Request.model_validate(data)
        assert request.current_path_list == ["src"]

    def test_search_l2_response_valid(self):
        """Test SearchL2Response validation and nested camelCase."""
        l1_cand = Level1Candidate(name="file.ts", is_dir=False, path_segment="file.ts")
        data = {
            "level_1_candidates": [l1_cand],
            "level_2_prefetched": {"dir_name": [l1_cand]},
        }
        response = SearchL2Response.model_validate(data)
        assert len(response.level_1_candidates) == 1
        assert "dir_name" in response.level_2_prefetched

        # Test camelCase serialization
        dumped = response.model_dump(by_alias=True)
        assert "level1Candidates" in dumped
        assert "level2Prefetched" in dumped
        assert dumped["level1Candidates"][0]["pathSegment"] == "file.ts"

    def test_ls_entry_camel_case(self):
        """Test LsEntry camelCase aliases."""
        data = {
            "name": "main.py",
            "isDir": True,
            "lastModified": 12345.6,
            "path": "/root/main.py",
        }
        entry = LsEntry.model_validate(data)
        assert entry.is_dir is True
        assert entry.last_modified == 12345.6

    def test_ls_response_serialization(self):
        """Test LsResponse serialization to camelCase."""
        entry = LsEntry(name="d", is_dir=True, path="/d", size=100)
        response = LsResponse(entries=[entry])
        dumped = response.model_dump(by_alias=True)
        assert "entries" in dumped
        assert dumped["entries"][0]["isDir"] is True
        assert dumped["entries"][0]["path"] == "/d"

    def test_prefetch_result_serialization(self):
        """Test PrefetchResult serialization."""
        l1 = Level1Candidate(name="a", is_dir=False, path_segment="seg")
        result = PrefetchResult(data={"key": [l1]})
        dumped = result.model_dump(by_alias=True)
        assert "data" in dumped
        assert dumped["data"]["key"][0]["pathSegment"] == "seg"

    def test_missing_required_field_raises_error(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            # Missing parent_path_hash
            FileIndexEntry(path="/p", filename="f", is_dir=False)

    def test_invalid_type_raises_error(self):
        """Test that invalid types raise ValidationError."""
        with pytest.raises(ValidationError):
            # is_dir should be bool
            Level1Candidate(name="n", is_dir="not-a-bool", path_segment="p")
