"""
Unit tests for the datetime utility module.
"""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from freezegun import freeze_time
from pipe.core.utils.datetime import get_current_datetime, get_current_timestamp


class TestDatetimeUtils:
    """Tests for datetime utility functions."""

    @freeze_time("2025-01-01 10:30:00")
    def test_get_current_datetime_utc_default(self):
        """Test get_current_datetime returns UTC datetime by default."""
        expected_datetime = datetime(2025, 1, 1, 10, 30, 0, tzinfo=UTC)
        result = get_current_datetime()
        assert result == expected_datetime
        assert result.tzinfo == UTC

    @freeze_time("2025-01-01 10:30:00")
    def test_get_current_datetime_with_timezone(self):
        """Test get_current_datetime returns datetime in specified timezone."""
        tokyo_tz = ZoneInfo("Asia/Tokyo")
        expected_datetime = datetime(
            2025, 1, 1, 19, 30, 0, tzinfo=tokyo_tz
        )  # 10:30 UTC is 19:30 JST
        result = get_current_datetime(tz=tokyo_tz)
        assert result == expected_datetime
        assert result.tzinfo == tokyo_tz

    @freeze_time("2025-01-01 10:30:00")
    def test_get_current_timestamp_iso_format_default_utc(self):
        """Test get_current_timestamp returns ISO 8601 format in UTC by default."""
        expected_timestamp = "2025-01-01T10:30:00+00:00"
        result = get_current_timestamp()
        assert result == expected_timestamp

    @freeze_time("2025-01-01 10:30:00")
    def test_get_current_timestamp_iso_format_with_timezone(self):
        """Test get_current_timestamp returns ISO 8601 format in specified timezone."""
        tokyo_tz = ZoneInfo("Asia/Tokyo")
        expected_timestamp = "2025-01-01T19:30:00+09:00"  # 10:30 UTC is 19:30 JST
        result = get_current_timestamp(tz=tokyo_tz)
        assert result == expected_timestamp

    @freeze_time("2025-01-01 10:30:00")
    def test_get_current_timestamp_custom_format_default_utc(self):
        """Test get_current_timestamp returns custom format in UTC by default."""
        custom_format = "%Y/%m/%d %H:%M:%S %Z%z"
        expected_timestamp = "2025/01/01 10:30:00 UTC+0000"
        result = get_current_timestamp(fmt=custom_format)
        assert result == expected_timestamp

    @freeze_time("2025-01-01 10:30:00")
    def test_get_current_timestamp_custom_format_with_timezone(self):
        """Test get_current_timestamp returns custom format in specified timezone."""
        tokyo_tz = ZoneInfo("Asia/Tokyo")
        custom_format = "%Y/%m/%d %H:%M:%S %Z%z"
        expected_timestamp = "2025/01/01 19:30:00 JST+0900"  # 10:30 UTC is 19:30 JST
        result = get_current_timestamp(tz=tokyo_tz, fmt=custom_format)
        assert result == expected_timestamp
