"""
Domain functions for migrating Session data from legacy formats.

This module handles backward-compatibility transformations for Session data
loaded from disk. It applies migrations before Pydantic validation to ensure
old data can be successfully loaded.
"""

from typing import Any

from pipe.core.utils.datetime import get_current_timestamp


def migrate_session_data(data: dict[str, Any], timezone_obj: Any) -> dict[str, Any]:
    """
    Migrate legacy Session data format to current format.

    This function applies the following migrations:
    1. Sets default `created_at` if missing
    2. Sets default `timestamp` for turns/pools if missing
    3. Sets default `original_turns_range` for compressed_history turns if missing

    Args:
        data: Raw session data dictionary loaded from JSON
        timezone_obj: ZoneInfo object for timestamp generation

    Returns:
        Migrated session data dictionary ready for Pydantic validation
    """
    # Migration 1: Set default created_at if missing
    session_creation_time = data.get("created_at", get_current_timestamp(timezone_obj))

    # Migration 2 & 3: Migrate turns and pools
    for turn_list_key in ["turns", "pools"]:
        if turn_list_key in data and isinstance(data[turn_list_key], list):
            for turn_data in data[turn_list_key]:
                if not isinstance(turn_data, dict):
                    continue

                # Migration 2: Set default timestamp if missing
                if "timestamp" not in turn_data:
                    turn_data["timestamp"] = session_creation_time

                # Migration 3: Set default original_turns_range for compressed_history
                if (
                    turn_data.get("type") == "compressed_history"
                    and "original_turns_range" not in turn_data
                ):
                    turn_data["original_turns_range"] = [0, 0]

    return data
