#!/usr/bin/env python3
"""
Analyze session JSON files and extract key metrics.

Usage:
    python scripts/analyze/analyze_sessions.py [--after YYYY-MM-DDTHH:MM:SSZ]
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze session JSON files and extract key metrics"
    )
    parser.add_argument(
        "--after",
        type=str,
        help="Filter sessions created after this UTC datetime (format: YYYY-MM-DDTHH:MM:SSZ)",
    )
    return parser.parse_args()


def parse_datetime_utc(dt_str: str) -> datetime:
    """Parse datetime string to UTC datetime object.

    Handles both UTC (Z suffix) and timezone-aware formats (+09:00, etc).
    """
    # Replace 'Z' with '+00:00' for ISO format parsing
    if dt_str.endswith("Z"):
        dt_str = dt_str[:-1] + "+00:00"

    dt = datetime.fromisoformat(dt_str)
    # Convert to UTC
    return dt.astimezone(UTC)


def extract_session_metrics(session_file: Path) -> dict[str, Any] | None:
    """Extract metrics from a single session JSON file."""
    try:
        with open(session_file, encoding="utf-8") as f:
            data = json.load(f)

        # Calculate approximation_tokens
        cumulative_total = data.get("cumulative_total_tokens", 0)
        cumulative_cached = data.get("cumulative_cached_tokens", 0)
        # ceil(cumulative_total_tokens - (cumulative_cached_tokens * 0.9))
        import math

        approximation_tokens = math.ceil(cumulative_total - (cumulative_cached * 0.9))

        # Extract file_name from purpose by removing "Generate tests for " prefix
        purpose = data.get("purpose", "")
        file_name = purpose.replace("Generate tests for ", "") if purpose else ""

        return {
            "session_id": data.get("session_id", ""),
            "file_name": file_name,
            "token_count": data.get("token_count", 0),
            "cumulative_total_tokens": cumulative_total,
            "cumulative_cached_tokens": cumulative_cached,
            "approximation_tokens": approximation_tokens,
            "references_count": len(data.get("references", [])),
            "turns": len(data.get("turns", [])),
        }
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Warning: Failed to process {session_file}: {e}")
        return None


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Parse filter datetime if provided
    filter_datetime_utc: datetime | None = None
    if args.after:
        try:
            filter_datetime_utc = parse_datetime_utc(args.after)
            print(
                f"Filtering sessions created after: {filter_datetime_utc.isoformat()}"
            )
        except ValueError as e:
            print(f"Error: Invalid datetime format: {e}")
            return

    # Find all session JSON files
    sessions_dir = Path("sessions")
    if not sessions_dir.exists():
        print("Error: sessions directory not found")
        return

    # Pattern: sessions/*/*.json (excluding .lock files and .streaming.log files)
    session_files = []
    for session_subdir in sessions_dir.iterdir():
        if session_subdir.is_dir():
            for json_file in session_subdir.glob("*.json"):
                # Skip lock files
                if not json_file.name.endswith(".lock"):
                    session_files.append(json_file)

    print(f"Found {len(session_files)} session JSON files")

    # Extract metrics from each session
    results = []
    for session_file in session_files:
        # Check created_at filter if specified
        if filter_datetime_utc:
            try:
                with open(session_file, encoding="utf-8") as f:
                    data = json.load(f)
                    created_at_str = data.get("created_at", "")
                    if created_at_str:
                        created_at = parse_datetime_utc(created_at_str)
                        if created_at <= filter_datetime_utc:
                            continue
            except (json.JSONDecodeError, ValueError, KeyError):
                continue

        metrics = extract_session_metrics(session_file)
        if metrics:
            results.append(metrics)

    print(f"Successfully extracted metrics from {len(results)} sessions")

    # Output results as JSON array
    print("\n" + "=" * 80)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
