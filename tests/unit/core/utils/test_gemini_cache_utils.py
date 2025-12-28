"""Tests for Gemini API cache utilities."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

from pipe.core.models.cache_registry import CacheRegistry, CacheRegistryEntry
from pipe.core.utils.gemini_cache_utils import (
    _clean_expired_caches,
    _create_cache,
    is_cache_expired,
)


class TestIsCacheExpired:
    """Tests for is_cache_expired function."""

    def test_cache_not_expired(self):
        """Test that valid cache returns False."""
        # Future time (1 hour from now)
        future_time = datetime.now(UTC) + timedelta(hours=1)
        expire_time_str = future_time.isoformat()

        result = is_cache_expired(expire_time_str)

        assert result is False

    def test_cache_expired(self):
        """Test that expired cache returns True."""
        # Past time (1 hour ago)
        past_time = datetime.now(UTC) - timedelta(hours=1)
        expire_time_str = past_time.isoformat()

        result = is_cache_expired(expire_time_str)

        assert result is True

    def test_cache_timezone_naive_treated_as_utc(self):
        """Test that timezone-naive datetime is treated as UTC."""
        # Future time without timezone
        future_time = datetime.now(UTC) + timedelta(hours=1)
        expire_time_str = future_time.replace(tzinfo=None).isoformat()

        result = is_cache_expired(expire_time_str)

        assert result is False

    def test_cache_invalid_format_treated_as_expired(self):
        """Test that invalid datetime format returns True (expired)."""
        invalid_strings = [
            "not-a-date",
            "2025-13-45",  # Invalid month/day
            "",
            "invalid",
        ]

        for invalid_str in invalid_strings:
            result = is_cache_expired(invalid_str)
            assert result is True, f"Expected True for invalid string: {invalid_str}"

    def test_cache_with_custom_current_time(self):
        """Test that custom current_time parameter works for testing."""
        expire_time_str = "2025-01-15T10:30:00+00:00"
        current_time_before = datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC)
        current_time_after = datetime(2025, 1, 15, 11, 0, 0, tzinfo=UTC)

        # Before expiration
        result_before = is_cache_expired(expire_time_str, current_time_before)
        assert result_before is False

        # After expiration
        result_after = is_cache_expired(expire_time_str, current_time_after)
        assert result_after is True


class TestCleanExpiredCaches:
    """Tests for _clean_expired_caches function."""

    def test_clean_expired_caches_removes_expired(self):
        """Test that expired caches are deleted from both API and registry."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.caches.delete = MagicMock()

        # Create registry with expired entries
        past_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        cache_registry = CacheRegistry(
            entries={
                "hash1": CacheRegistryEntry(
                    name="cachedContents/expired1",
                    expire_time=past_time,
                    session_id="session1",
                ),
                "hash2": CacheRegistryEntry(
                    name="cachedContents/expired2",
                    expire_time=past_time,
                    session_id="session2",
                ),
            }
        )

        registry_path = "/tmp/test_registry.json"

        with patch(
            "pipe.core.utils.gemini_cache_utils._save_registry"
        ) as mock_save_registry:
            _clean_expired_caches(mock_client, registry_path, cache_registry, limit=5)

            # Verify API delete was called twice
            assert mock_client.caches.delete.call_count == 2

            # Verify entries were removed from registry
            assert len(cache_registry.entries) == 0

            # Verify registry was saved
            mock_save_registry.assert_called_once()

    def test_clean_expired_caches_respects_limit(self):
        """Test that deletion respects the limit parameter."""
        mock_client = MagicMock()
        mock_client.caches.delete = MagicMock()

        # Create registry with 10 expired entries
        past_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        entries = {
            f"hash{i}": CacheRegistryEntry(
                name=f"cachedContents/expired{i}",
                expire_time=past_time,
                session_id=f"session{i}",
            )
            for i in range(10)
        }
        cache_registry = CacheRegistry(entries=entries)

        registry_path = "/tmp/test_registry.json"

        with patch("pipe.core.utils.gemini_cache_utils._save_registry"):
            _clean_expired_caches(mock_client, registry_path, cache_registry, limit=3)

            # Verify only 3 deletes were called
            assert mock_client.caches.delete.call_count == 3

            # Verify 3 entries were removed from registry
            assert len(cache_registry.entries) == 7

    def test_clean_expired_caches_deletes_oldest_first(self):
        """Test that caches are deleted in order of oldest expire_time first."""
        mock_client = MagicMock()
        deleted_names = []

        def track_delete(name):
            deleted_names.append(name)

        mock_client.caches.delete = MagicMock(side_effect=track_delete)

        # Create registry with different expiration times
        now = datetime.now(UTC)
        cache_registry = CacheRegistry(
            entries={
                "hash1": CacheRegistryEntry(
                    name="cachedContents/oldest",
                    expire_time=(now - timedelta(hours=3)).isoformat(),
                    session_id="session1",
                ),
                "hash2": CacheRegistryEntry(
                    name="cachedContents/middle",
                    expire_time=(now - timedelta(hours=2)).isoformat(),
                    session_id="session2",
                ),
                "hash3": CacheRegistryEntry(
                    name="cachedContents/newest",
                    expire_time=(now - timedelta(hours=1)).isoformat(),
                    session_id="session3",
                ),
            }
        )

        registry_path = "/tmp/test_registry.json"

        with patch("pipe.core.utils.gemini_cache_utils._save_registry"):
            _clean_expired_caches(mock_client, registry_path, cache_registry, limit=5)

            # Verify deletion order
            assert deleted_names == [
                "cachedContents/oldest",
                "cachedContents/middle",
                "cachedContents/newest",
            ]

    def test_clean_expired_caches_handles_404_gracefully(self):
        """Test that 404 errors (already deleted) are handled gracefully."""
        mock_client = MagicMock()

        def raise_404(name):
            raise Exception("404 Not Found")

        mock_client.caches.delete = MagicMock(side_effect=raise_404)

        past_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        cache_registry = CacheRegistry(
            entries={
                "hash1": CacheRegistryEntry(
                    name="cachedContents/deleted",
                    expire_time=past_time,
                    session_id="session1",
                ),
            }
        )

        registry_path = "/tmp/test_registry.json"

        with patch("pipe.core.utils.gemini_cache_utils._save_registry"):
            # Should not raise exception
            _clean_expired_caches(mock_client, registry_path, cache_registry, limit=5)

            # Verify entry was still removed from registry
            assert len(cache_registry.entries) == 0

    def test_clean_expired_caches_skips_valid_caches(self):
        """Test that valid (non-expired) caches are not deleted."""
        mock_client = MagicMock()
        mock_client.caches.delete = MagicMock()

        # Create registry with one expired and one valid cache
        now = datetime.now(UTC)
        cache_registry = CacheRegistry(
            entries={
                "hash1": CacheRegistryEntry(
                    name="cachedContents/expired",
                    expire_time=(now - timedelta(hours=1)).isoformat(),
                    session_id="session1",
                ),
                "hash2": CacheRegistryEntry(
                    name="cachedContents/valid",
                    expire_time=(now + timedelta(hours=1)).isoformat(),
                    session_id="session2",
                ),
            }
        )

        registry_path = "/tmp/test_registry.json"

        with patch("pipe.core.utils.gemini_cache_utils._save_registry"):
            _clean_expired_caches(mock_client, registry_path, cache_registry, limit=5)

            # Verify only one delete was called
            assert mock_client.caches.delete.call_count == 1

            # Verify only expired entry was removed
            assert len(cache_registry.entries) == 1
            assert "hash2" in cache_registry.entries


class TestCreateCache:
    """Tests for _create_cache function."""

    def test_create_cache_uses_api_expire_time(self):
        """Test that _create_cache uses expire_time from API response."""
        mock_client = MagicMock()
        mock_cached_obj = MagicMock()
        mock_cached_obj.name = "cachedContents/test123"

        # Set expire_time attribute on mock
        api_expire_time = datetime.now(UTC) + timedelta(hours=1)
        mock_cached_obj.expire_time = api_expire_time

        mock_client.caches.create.return_value = mock_cached_obj

        cache_registry = CacheRegistry()
        registry_path = "/tmp/test_registry.json"

        with patch("pipe.core.utils.gemini_cache_utils._save_registry"):
            result = _create_cache(
                client=mock_client,
                static_content="test content",
                model_name="gemini-2.0-flash-exp",
                tools=[],
                content_hash="hash123",
                cache_registry=cache_registry,
                registry_path=registry_path,
                session_id="test_session_123",
            )

            # Verify cache was created
            assert result == "cachedContents/test123"

            # Verify registry uses API expire_time
            assert "hash123" in cache_registry.entries
            assert (
                cache_registry.entries["hash123"].expire_time
                == api_expire_time.isoformat()
            )
            assert cache_registry.entries["hash123"].session_id == "test_session_123"

    def test_create_cache_fallback_without_api_expire_time(self):
        """Test that _create_cache falls back to conservative time when API doesn't provide expire_time."""
        mock_client = MagicMock()
        mock_cached_obj = MagicMock()
        mock_cached_obj.name = "cachedContents/test123"

        # Do not set expire_time attribute (simulating old API or missing field)
        del mock_cached_obj.expire_time

        mock_client.caches.create.return_value = mock_cached_obj

        cache_registry = CacheRegistry()
        registry_path = "/tmp/test_registry.json"

        fixed_now = datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC)

        with (
            patch("pipe.core.utils.gemini_cache_utils._save_registry"),
            patch(
                "pipe.core.utils.gemini_cache_utils.get_current_datetime",
                return_value=fixed_now,
            ),
        ):
            result = _create_cache(
                client=mock_client,
                static_content="test content",
                model_name="gemini-2.0-flash-exp",
                tools=[],
                content_hash="hash123",
                cache_registry=cache_registry,
                registry_path=registry_path,
                session_id="test_session_456",
            )

            # Verify cache was created
            assert result == "cachedContents/test123"

            # Verify registry uses fallback time (55 minutes = 3300 seconds)
            expected_expire_time = fixed_now + timedelta(seconds=3300)
            assert "hash123" in cache_registry.entries
            assert (
                cache_registry.entries["hash123"].expire_time
                == expected_expire_time.isoformat()
            )
            assert cache_registry.entries["hash123"].session_id == "test_session_456"
