from datetime import UTC, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from pipe.core.utils.datetime import get_current_datetime, get_current_timestamp


class TestGetCurrentDatetime:
    """Tests for get_current_datetime function."""

    def test_get_current_datetime_utc_default(self):
        """Test that get_current_datetime returns UTC by default."""
        fixed_now = datetime(2025, 12, 23, 12, 0, 0, tzinfo=UTC)
        with patch("pipe.core.utils.datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now

            result = get_current_datetime()

            assert result == fixed_now
            assert result.tzinfo == UTC
            mock_datetime.now.assert_called_once_with(UTC)

    def test_get_current_datetime_specific_tz(self):
        """Test that get_current_datetime returns datetime in specified timezone."""
        jst = ZoneInfo("Asia/Tokyo")
        fixed_now = datetime(2025, 12, 23, 21, 0, 0, tzinfo=jst)
        with patch("pipe.core.utils.datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now

            result = get_current_datetime(tz=jst)

            assert result == fixed_now
            assert result.tzinfo == jst
            mock_datetime.now.assert_called_once_with(jst)


class TestGetCurrentTimestamp:
    """Tests for get_current_timestamp function."""

    def test_get_current_timestamp_iso_default(self):
        """Test that get_current_timestamp returns ISO format by default."""
        fixed_now = datetime(2025, 12, 23, 12, 0, 0, tzinfo=UTC)
        with patch("pipe.core.utils.datetime.get_current_datetime") as mock_get_now:
            mock_get_now.return_value = fixed_now

            result = get_current_timestamp()

            assert result == "2025-12-23T12:00:00+00:00"
            mock_get_now.assert_called_once_with(UTC)

    def test_get_current_timestamp_specific_tz(self):
        """Test that get_current_timestamp returns ISO format for specific timezone."""
        jst = ZoneInfo("Asia/Tokyo")
        fixed_now = datetime(2025, 12, 23, 21, 0, 0, tzinfo=jst)
        with patch("pipe.core.utils.datetime.get_current_datetime") as mock_get_now:
            mock_get_now.return_value = fixed_now

            result = get_current_timestamp(tz=jst)

            assert result == "2025-12-23T21:00:00+09:00"
            mock_get_now.assert_called_once_with(jst)

    def test_get_current_timestamp_custom_format(self):
        """Test get_current_timestamp with a custom format string."""
        fixed_now = datetime(2025, 12, 23, 12, 0, 0, tzinfo=UTC)
        fmt = "%Y/%m/%d %H:%M:%S"
        with patch("pipe.core.utils.datetime.get_current_datetime") as mock_get_now:
            mock_get_now.return_value = fixed_now

            result = get_current_timestamp(fmt=fmt)

            assert result == "2025/12/23 12:00:00"
            mock_get_now.assert_called_once_with(UTC)
