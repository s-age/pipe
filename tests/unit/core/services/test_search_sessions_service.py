import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pipe.core.services.search_sessions_service import SearchSessionsService


@pytest.fixture
def sessions_dir(tmp_path: Path) -> Path:
    """Create a temporary sessions directory."""
    d = tmp_path / "sessions"
    d.mkdir()
    return d


@pytest.fixture
def service(sessions_dir: Path) -> SearchSessionsService:
    """Create a SearchSessionsService instance."""
    return SearchSessionsService(str(sessions_dir))


class TestSearchSessionsService:
    """Tests for SearchSessionsService."""

    def test_init(self, sessions_dir: Path):
        """Test initialization."""
        service = SearchSessionsService(str(sessions_dir))
        assert service.sessions_dir == str(sessions_dir)

    def test_iter_session_files(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test iterating over session files, skipping backups and non-json."""
        # Create some files
        (sessions_dir / "session1.json").write_text("{}")
        (sessions_dir / "session2.JSON").write_text("{}")
        (sessions_dir / "not_a_session.txt").write_text("{}")

        backups_dir = sessions_dir / "backups"
        backups_dir.mkdir()
        (backups_dir / "backup1.json").write_text("{}")

        sub_dir = sessions_dir / "sub"
        sub_dir.mkdir()
        (sub_dir / "session3.json").write_text("{}")

        files = list(service._iter_session_files())

        # Should find session1, session2, session3
        # Should NOT find not_a_session.txt or backup1.json
        assert len(files) == 3
        basenames = [os.path.basename(f) for f in files]
        assert "session1.json" in basenames
        assert "session2.JSON" in basenames
        assert "session3.json" in basenames
        assert "backup1.json" not in basenames

    def test_compute_session_id(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test computing session ID from file path."""
        fpath = str(sessions_dir / "session1.json")
        assert service._compute_session_id(fpath) == "session1"

        fpath_sub = str(sessions_dir / "sub" / "session2.json")
        # relpath should be "sub/session2.json" -> "sub/session2"
        # Note: on Windows, relpath might use \, but the method replaces it with /
        assert service._compute_session_id(fpath_sub) == "sub/session2"

    def test_compute_session_id_non_json(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test computing session ID for a non-json file (Line 42 coverage)."""
        fpath = str(sessions_dir / "README.md")
        assert service._compute_session_id(fpath) == "README.md"

    def test_search_empty_query(self, service: SearchSessionsService):
        """Test search with empty or whitespace query."""
        assert service.search("") == []
        assert service.search("   ") == []
        assert service.search(None) == []  # type: ignore

    def test_search_filename_match(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test matching by filename."""
        fpath = sessions_dir / "find_me.json"
        fpath.write_text("{}")

        results = service.search("find")
        assert len(results) == 1
        assert results[0].session_id == "find_me"
        assert results[0].title == "find_me"
        assert results[0].path == str(fpath)

    def test_search_purpose_match(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test matching by purpose field."""
        fpath = sessions_dir / "session1.json"
        data = {"purpose": "This is a test purpose", "background": "Other"}
        fpath.write_text(json.dumps(data))

        results = service.search("test purpose")
        assert len(results) == 1
        assert results[0].session_id == "session1"
        assert results[0].title == "This is a test purpose"

    def test_search_background_match(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test matching by background field."""
        fpath = sessions_dir / "session1.json"
        data = {"purpose": "", "background": "Important background info"}
        fpath.write_text(json.dumps(data))

        results = service.search("background info")
        assert len(results) == 1
        assert results[0].session_id == "session1"
        assert results[0].title == "Important background info"

    def test_search_turn_instruction_match(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test matching by turn instruction."""
        fpath = sessions_dir / "session1.json"
        data = {
            "purpose": "P",
            "turns": [
                {"type": "user_task", "instruction": "Search for this secret word"},
                {"type": "model_response", "content": "Okay"},
            ],
        }
        fpath.write_text(json.dumps(data))

        results = service.search("secret word")
        assert len(results) == 1
        assert results[0].session_id == "session1"
        assert results[0].title == "P"

    def test_search_turn_content_match(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test matching by turn content."""
        fpath = sessions_dir / "session1.json"
        data = {
            "background": "B",
            "turns": [
                {"type": "user_task", "instruction": "Hi"},
                {"type": "model_response", "content": "The answer is 42"},
            ],
        }
        fpath.write_text(json.dumps(data))

        results = service.search("answer is 42")
        assert len(results) == 1
        assert results[0].session_id == "session1"
        assert results[0].title == "B"

    def test_search_case_insensitive(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test that search is case-insensitive."""
        fpath = sessions_dir / "Session.json"
        data = {"purpose": "PURPOSE"}
        fpath.write_text(json.dumps(data))

        assert len(service.search("session")) == 1
        assert len(service.search("purpose")) == 1

    def test_search_json_load_error(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test that corrupted JSON files are skipped."""
        fpath = sessions_dir / "corrupted.json"
        fpath.write_text("{ invalid json")

        results = service.search("query")
        assert results == []

    def test_search_deduplication(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test that a session is returned only once even if multiple fields match."""
        fpath = sessions_dir / "match_all.json"
        data = {
            "purpose": "match",
            "background": "match",
            "turns": [{"instruction": "match"}, {"content": "match"}],
        }
        fpath.write_text(json.dumps(data))

        results = service.search("match")
        assert len(results) == 1

    def test_search_already_matched_skip(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test skipping already matched session ID (Line 68 coverage)."""
        fpath = sessions_dir / "session1.json"
        fpath.write_text(json.dumps({"purpose": "match"}))

        # Mock _iter_session_files to return the same file twice
        with patch.object(
            service, "_iter_session_files", return_value=[str(fpath), str(fpath)]
        ):
            results = service.search("match")
            assert len(results) == 1

    def test_search_non_dict_turn_skip(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test skipping non-dict turns (Line 95 coverage)."""
        fpath = sessions_dir / "session1.json"
        data = {
            "turns": ["not a dict", {"instruction": "match"}],
        }
        fpath.write_text(json.dumps(data))

        results = service.search("match")
        assert len(results) == 1
        assert results[0].session_id == "session1"

    def test_search_multiple_sessions(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test searching across multiple sessions."""
        (sessions_dir / "s1.json").write_text(json.dumps({"purpose": "apple"}))
        (sessions_dir / "s2.json").write_text(json.dumps({"purpose": "banana"}))
        (sessions_dir / "s3.json").write_text(json.dumps({"purpose": "apple pie"}))

        results = service.search("apple")
        assert len(results) == 2
        ids = {r.session_id for r in results}
        assert ids == {"s1", "s3"}

    def test_search_title_fallback(
        self, sessions_dir: Path, service: SearchSessionsService
    ):
        """Test title fallback logic when purpose/background are missing."""
        fpath = sessions_dir / "no_meta.json"
        data = {"turns": [{"instruction": "find me"}]}
        fpath.write_text(json.dumps(data))

        results = service.search("find me")
        assert len(results) == 1
        assert results[0].title == "no_meta"
