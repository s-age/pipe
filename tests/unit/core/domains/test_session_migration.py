"""Tests for session_migration domain functions."""

import zoneinfo
from typing import Any
from unittest.mock import patch

import pytest
from pipe.core.domains.session_migration import migrate_session_data


class TestMigrateSessionData:
    """Tests for migrate_session_data function."""

    @pytest.fixture
    def timezone_utc(self):
        """UTC timezone fixture."""
        return zoneinfo.ZoneInfo("UTC")

    @patch("pipe.core.domains.session_migration.get_current_timestamp")
    def test_migrate_created_at_missing(self, mock_get_timestamp, timezone_utc):
        """Test setting default created_at when missing."""
        mock_get_timestamp.return_value = "2026-01-01T00:00:00Z"
        data: dict[str, Any] = {}
        result = migrate_session_data(data, timezone_utc)

        assert result["created_at"] == "2026-01-01T00:00:00Z"
        mock_get_timestamp.assert_called_once_with(timezone_utc)

    def test_migrate_created_at_exists(self, timezone_utc):
        """Test preserving created_at when already exists."""
        data: dict[str, Any] = {"created_at": "2025-12-31T23:59:59Z"}
        result = migrate_session_data(data, timezone_utc)

        assert result["created_at"] == "2025-12-31T23:59:59Z"

    def test_migrate_turn_timestamp_missing(self, timezone_utc):
        """Test setting default timestamp for turns when missing."""
        data: dict[str, Any] = {
            "created_at": "2025-01-01T10:00:00Z",
            "turns": [
                {"type": "user_task", "instruction": "hello"},
                {
                    "type": "model_response",
                    "content": "hi",
                    "timestamp": "2025-01-01T10:05:00Z",
                },
            ],
        }
        result = migrate_session_data(data, timezone_utc)

        assert result["turns"][0]["timestamp"] == "2025-01-01T10:00:00Z"
        assert result["turns"][1]["timestamp"] == "2025-01-01T10:05:00Z"

    def test_migrate_pool_timestamp_missing(self, timezone_utc):
        """Test setting default timestamp for pools when missing."""
        data: dict[str, Any] = {
            "created_at": "2025-01-01T10:00:00Z",
            "pools": [
                {"type": "user_task", "instruction": "pool item"},
            ],
        }
        result = migrate_session_data(data, timezone_utc)

        assert result["pools"][0]["timestamp"] == "2025-01-01T10:00:00Z"

    def test_migrate_compressed_history_range_missing(self, timezone_utc):
        """Test setting default original_turns_range for compressed_history."""
        data: dict[str, Any] = {
            "turns": [
                {
                    "type": "compressed_history",
                    "content": "summary",
                    "timestamp": "2025-01-01T10:00:00Z",
                }
            ]
        }
        result = migrate_session_data(data, timezone_utc)

        assert result["turns"][0]["original_turns_range"] == [0, 0]

    def test_migrate_compressed_history_range_exists(self, timezone_utc):
        """Test preserving original_turns_range for compressed_history when exists."""
        data: dict[str, Any] = {
            "turns": [
                {
                    "type": "compressed_history",
                    "content": "summary",
                    "original_turns_range": [1, 5],
                }
            ]
        }
        result = migrate_session_data(data, timezone_utc)

        assert result["turns"][0]["original_turns_range"] == [1, 5]

    def test_migrate_non_dict_turn_ignored(self, timezone_utc):
        """Test that non-dictionary elements in turns list are ignored."""
        data: dict[str, Any] = {"turns": ["not a dict", {"type": "user_task"}]}
        # Should not raise AttributeError
        result = migrate_session_data(data, timezone_utc)
        assert result["turns"][0] == "not a dict"
        assert "timestamp" in result["turns"][1]

    def test_migrate_empty_lists(self, timezone_utc):
        """Test migration with empty turns and pools lists."""
        data: dict[str, Any] = {"turns": [], "pools": []}
        result = migrate_session_data(data, timezone_utc)
        assert result["turns"] == []
        assert result["pools"] == []

    def test_migrate_missing_lists(self, timezone_utc):
        """Test migration when turns and pools keys are missing."""
        data: dict[str, Any] = {"created_at": "2025-01-01T10:00:00Z"}
        result = migrate_session_data(data, timezone_utc)
        assert "turns" not in result
        assert "pools" not in result
