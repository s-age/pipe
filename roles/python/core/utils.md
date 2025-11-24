# Utils Layer

## Purpose

Utils provide **pure utility functions** with no dependencies on other core layers. These are fundamental helpers for datetime operations, file I/O, and other universal needs that can be used anywhere in the system.

## Responsibilities

1. **Pure Functions** - Stateless utility functions
2. **Common Operations** - Datetime, file operations, string manipulation
3. **No Dependencies** - Independent of core business logic
4. **Reusability** - Used across all layers
5. **Reliability** - Well-tested, battle-hardened utilities

## Characteristics

- ✅ Pure functions (no side effects except necessary I/O)
- ✅ No dependencies on other core layers
- ✅ Stateless operations
- ✅ Standard library focused
- ❌ **NO business logic** - only generic utilities
- ❌ **NO state management** - stateless functions only
- ❌ **NO layer-specific logic** - must be universally useful

## File Structure

```
utils/
├── __init__.py
├── datetime.py       # Datetime utilities
└── file.py           # File operations (locking, etc.)
```

## Dependencies

**Allowed:**

- ✅ Standard library only (os, datetime, json, etc.)
- ✅ Well-established third-party libraries (if absolutely necessary)

**Forbidden:**

- ❌ Any core layer (services, domains, repositories, models, etc.)
- ❌ Business logic
- ❌ Application state

## Template

```python
"""
Utilities for [domain].

These are pure utility functions with no dependencies on application logic.
"""


def utility_function(param: str) -> str:
    """
    Pure utility function.

    This function:
    - Takes input
    - Applies transformation
    - Returns output
    - Has no side effects (except I/O if needed)

    Args:
        param: Input parameter

    Returns:
        Transformed result

    Examples:
        utility_function("hello")  # Returns "HELLO"
    """
    return param.upper()


def another_utility(data: dict) -> str:
    """
    Another pure utility.

    Args:
        data: Input data

    Returns:
        Processed result
    """
    # Pure logic, no dependencies
    return json.dumps(data, indent=2)
```

## Real Examples

### datetime.py - Datetime Utilities

**Key Utilities:**

- Get current timestamp in ISO format
- Parse ISO timestamps
- Convert between timezones
- Calculate time differences

```python
"""
Datetime utilities.

Provides timezone-aware datetime operations using the standard library.
"""

import datetime
import zoneinfo
from typing import Optional


def get_current_timestamp(tz: zoneinfo.ZoneInfo | None = None) -> str:
    """
    Gets current timestamp in ISO 8601 format.

    Args:
        tz: Timezone (UTC if None)

    Returns:
        ISO format timestamp string (e.g., "2024-01-15T10:30:00+00:00")

    Examples:
        get_current_timestamp()  # UTC
        get_current_timestamp(zoneinfo.ZoneInfo("America/New_York"))
    """
    tz = tz or zoneinfo.ZoneInfo("UTC")
    return datetime.datetime.now(tz).isoformat()


def parse_timestamp(timestamp_str: str) -> datetime.datetime:
    """
    Parses ISO 8601 format timestamp.

    Args:
        timestamp_str: ISO format timestamp string

    Returns:
        datetime object

    Raises:
        ValueError: If timestamp format is invalid

    Examples:
        parse_timestamp("2024-01-15T10:30:00+00:00")
    """
    try:
        return datetime.datetime.fromisoformat(timestamp_str)
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e


def get_timezone(tz_name: str) -> zoneinfo.ZoneInfo:
    """
    Gets timezone object by name.

    Args:
        tz_name: Timezone name (e.g., "UTC", "America/New_York")

    Returns:
        ZoneInfo object

    Raises:
        ValueError: If timezone name is invalid

    Examples:
        get_timezone("UTC")
        get_timezone("Asia/Tokyo")
    """
    try:
        return zoneinfo.ZoneInfo(tz_name)
    except zoneinfo.ZoneInfoNotFoundError as e:
        raise ValueError(f"Invalid timezone: {tz_name}") from e


def convert_timezone(
    timestamp: datetime.datetime,
    target_tz: zoneinfo.ZoneInfo,
) -> datetime.datetime:
    """
    Converts datetime to different timezone.

    Args:
        timestamp: datetime object (must be timezone-aware)
        target_tz: Target timezone

    Returns:
        datetime in target timezone

    Raises:
        ValueError: If timestamp is not timezone-aware

    Examples:
        dt = parse_timestamp("2024-01-15T10:30:00+00:00")
        tokyo_time = convert_timezone(dt, get_timezone("Asia/Tokyo"))
    """
    if timestamp.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")

    return timestamp.astimezone(target_tz)


def format_timestamp(
    timestamp: datetime.datetime,
    format_str: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """
    Formats datetime as string.

    Args:
        timestamp: datetime object
        format_str: strftime format string

    Returns:
        Formatted string

    Examples:
        dt = parse_timestamp("2024-01-15T10:30:00+00:00")
        format_timestamp(dt, "%Y-%m-%d")  # "2024-01-15"
    """
    return timestamp.strftime(format_str)


def calculate_duration(
    start: datetime.datetime,
    end: datetime.datetime,
) -> datetime.timedelta:
    """
    Calculates duration between two timestamps.

    Args:
        start: Start timestamp
        end: End timestamp

    Returns:
        timedelta object

    Examples:
        start = parse_timestamp("2024-01-15T10:00:00+00:00")
        end = parse_timestamp("2024-01-15T12:00:00+00:00")
        duration = calculate_duration(start, end)
        hours = duration.total_seconds() / 3600  # 2.0
    """
    return end - start


def is_timestamp_expired(
    timestamp: datetime.datetime,
    max_age_seconds: int,
    reference_time: datetime.datetime | None = None,
) -> bool:
    """
    Checks if timestamp has expired based on max age.

    Args:
        timestamp: Timestamp to check
        max_age_seconds: Maximum age in seconds
        reference_time: Reference time (now if None)

    Returns:
        True if expired, False otherwise

    Examples:
        old_time = parse_timestamp("2024-01-15T10:00:00+00:00")
        is_timestamp_expired(old_time, 3600)  # Check if older than 1 hour
    """
    if reference_time is None:
        # Use current time in same timezone as timestamp
        reference_time = datetime.datetime.now(timestamp.tzinfo)

    age = calculate_duration(timestamp, reference_time)
    return age.total_seconds() > max_age_seconds
```

### file.py - File Operation Utilities

**Key Utilities:**

- File locking context manager
- Safe file deletion
- Atomic file writes
- Path validation

```python
"""
File operation utilities.

Provides safe file operations and locking mechanisms.
"""

import os
import fcntl
import tempfile
import shutil
from typing import Iterator
from contextlib import contextmanager


class FileLock:
    """
    Context manager for file locking.

    Uses fcntl for POSIX-compliant file locking.
    Ensures only one process can access a file at a time.

    Usage:
        with FileLock('/path/to/file.lock'):
            # Critical section - only one process at a time
            modify_shared_resource()

    Attributes:
        lock_path: Path to lock file
        lock_file: Open file object for lock
    """

    def __init__(self, lock_path: str):
        """
        Initialize file lock.

        Args:
            lock_path: Path to lock file
        """
        self.lock_path = lock_path
        self.lock_file = None

    def __enter__(self):
        """Acquire lock."""
        # Create lock file if it doesn't exist
        os.makedirs(os.path.dirname(self.lock_path) or '.', exist_ok=True)

        # Open lock file
        self.lock_file = open(self.lock_path, 'w')

        # Acquire exclusive lock (blocks until available)
        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock."""
        if self.lock_file:
            # Release lock
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)

            # Close file
            self.lock_file.close()

        return False  # Don't suppress exceptions


@contextmanager
def atomic_write(file_path: str) -> Iterator[str]:
    """
    Context manager for atomic file writes.

    Writes to a temporary file, then moves it to the target path.
    This ensures the target file is never in a partially-written state.

    Usage:
        with atomic_write('config.json') as temp_path:
            with open(temp_path, 'w') as f:
                json.dump(data, f)
        # File is now atomically replaced

    Args:
        file_path: Target file path

    Yields:
        Path to temporary file for writing

    Examples:
        with atomic_write('data.json') as temp_path:
            with open(temp_path, 'w') as f:
                f.write('{"key": "value"}')
    """
    # Create temp file in same directory as target
    # (ensures same filesystem for atomic move)
    target_dir = os.path.dirname(file_path) or '.'
    os.makedirs(target_dir, exist_ok=True)

    # Create temporary file
    fd, temp_path = tempfile.mkstemp(
        dir=target_dir,
        prefix='.tmp_',
        suffix=os.path.basename(file_path),
    )
    os.close(fd)  # Close file descriptor, we'll use path

    try:
        # Yield temp path for writing
        yield temp_path

        # Atomic move (replace target with temp)
        shutil.move(temp_path, file_path)

    except Exception:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def delete_file(file_path: str) -> None:
    """
    Safely deletes file if it exists.

    Does nothing if file doesn't exist (idempotent).

    Args:
        file_path: Path to file to delete

    Examples:
        delete_file('/tmp/cache.json')
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def ensure_directory(dir_path: str) -> None:
    """
    Ensures directory exists, creating it if necessary.

    Args:
        dir_path: Path to directory

    Examples:
        ensure_directory('data/cache')
    """
    os.makedirs(dir_path, exist_ok=True)


def is_path_safe(path: str, base_dir: str) -> bool:
    """
    Checks if path is safe (doesn't escape base directory).

    Prevents path traversal attacks (e.g., "../../etc/passwd").

    Args:
        path: Path to check
        base_dir: Base directory that path must be within

    Returns:
        True if path is safe, False otherwise

    Examples:
        is_path_safe("data/file.txt", "/app")  # True
        is_path_safe("../etc/passwd", "/app")  # False
    """
    # Resolve to absolute paths
    base_abs = os.path.abspath(base_dir)
    path_abs = os.path.abspath(os.path.join(base_dir, path))

    # Check if path is within base directory
    return path_abs.startswith(base_abs)


def get_file_size(file_path: str) -> int:
    """
    Gets file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file doesn't exist

    Examples:
        size = get_file_size('data.json')
        print(f"File is {size} bytes")
    """
    return os.path.getsize(file_path)


def get_file_extension(file_path: str) -> str:
    """
    Gets file extension (without dot).

    Args:
        file_path: Path to file

    Returns:
        File extension (lowercase, no dot)

    Examples:
        get_file_extension("script.py")  # "py"
        get_file_extension("data.tar.gz")  # "gz"
    """
    _, ext = os.path.splitext(file_path)
    return ext.lstrip('.').lower()


def normalize_path(path: str) -> str:
    """
    Normalizes file path (resolves .., removes redundant separators).

    Args:
        path: Path to normalize

    Returns:
        Normalized path

    Examples:
        normalize_path("src/../lib/utils.py")  # "lib/utils.py"
        normalize_path("src//utils.py")  # "src/utils.py"
    """
    return os.path.normpath(path)
```

## Utility Patterns

### Pattern 1: Pure Transformation

```python
def transform_data(input_data: str) -> str:
    """Pure transformation - no side effects."""
    return input_data.upper()
```

### Pattern 2: Context Manager for Resources

```python
@contextmanager
def managed_resource():
    """Context manager pattern."""
    resource = acquire_resource()
    try:
        yield resource
    finally:
        release_resource(resource)
```

### Pattern 3: Safe Operations with Error Handling

```python
def safe_operation(value: str) -> Optional[int]:
    """Returns None on error instead of raising."""
    try:
        return int(value)
    except ValueError:
        return None
```

## Testing

### Unit Testing Utils

```python
# tests/core/utils/test_datetime.py
import datetime
import zoneinfo
from pipe.core.utils.datetime import (
    get_current_timestamp,
    parse_timestamp,
    convert_timezone,
)


def test_get_current_timestamp():
    timestamp = get_current_timestamp()

    # Should be valid ISO format
    parsed = datetime.datetime.fromisoformat(timestamp)
    assert parsed is not None


def test_parse_timestamp():
    timestamp_str = "2024-01-15T10:30:00+00:00"
    parsed = parse_timestamp(timestamp_str)

    assert parsed.year == 2024
    assert parsed.month == 1
    assert parsed.day == 15
    assert parsed.hour == 10
    assert parsed.minute == 30


def test_convert_timezone():
    # Create UTC timestamp
    utc = zoneinfo.ZoneInfo("UTC")
    tokyo = zoneinfo.ZoneInfo("Asia/Tokyo")

    dt = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=utc)

    # Convert to Tokyo time
    tokyo_time = convert_timezone(dt, tokyo)

    # Tokyo is UTC+9
    assert tokyo_time.hour == 21


def test_is_timestamp_expired():
    from pipe.core.utils.datetime import is_timestamp_expired

    # Create old timestamp
    old_time = datetime.datetime(
        2024, 1, 1, 12, 0, 0,
        tzinfo=zoneinfo.ZoneInfo("UTC")
    )

    # Check if expired (1 hour max age)
    assert is_timestamp_expired(old_time, 3600) is True
```

```python
# tests/core/utils/test_file.py
import os
import tempfile
from pipe.core.utils.file import (
    FileLock,
    atomic_write,
    is_path_safe,
)


def test_file_lock():
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_path = os.path.join(tmpdir, "test.lock")

        # Acquire lock
        with FileLock(lock_path):
            # Inside critical section
            assert os.path.exists(lock_path)

        # Lock released (file still exists but unlocked)


def test_atomic_write():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = os.path.join(tmpdir, "data.txt")

        # Write atomically
        with atomic_write(target) as temp_path:
            with open(temp_path, 'w') as f:
                f.write("test data")

        # Verify file was created
        assert os.path.exists(target)

        # Verify content
        with open(target, 'r') as f:
            assert f.read() == "test data"


def test_is_path_safe():
    base = "/app"

    # Safe paths
    assert is_path_safe("data/file.txt", base) is True
    assert is_path_safe("./file.txt", base) is True

    # Unsafe paths
    assert is_path_safe("../etc/passwd", base) is False
    assert is_path_safe("/etc/passwd", base) is False
```

## Best Practices

### 1. No Business Logic

```python
# ✅ GOOD: Generic utility
def format_timestamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")

# ❌ BAD: Business logic in utils
def format_session_timestamp(session: Session) -> str:
    # Business logic doesn't belong in utils
    if session.is_active:
        return session.created_at.strftime("%Y-%m-%d")
    return "N/A"
```

### 2. No Dependencies on Core Layers

```python
# ✅ GOOD: Only stdlib
import datetime
import os

def utility():
    # Uses only standard library
    pass

# ❌ BAD: Depends on core layers
from pipe.core.services.session_service import SessionService

def utility(service: SessionService):  # Utils can't depend on services
    pass
```

### 3. Pure Functions When Possible

```python
# ✅ GOOD: Pure function
def calculate_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

# ❌ BAD: Hidden side effects
def calculate_hash(data: str) -> str:
    log_to_file(data)  # Side effect!
    return hashlib.sha256(data.encode()).hexdigest()
```

### 4. Well-Documented

```python
# ✅ GOOD: Clear documentation
def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parses ISO 8601 format timestamp.

    Args:
        timestamp_str: ISO format timestamp

    Returns:
        datetime object

    Raises:
        ValueError: If format is invalid
    """
    ...
```

## Summary

Utils are the **foundation utilities**:

- ✅ Pure functions
- ✅ No dependencies on core layers
- ✅ Stateless operations
- ✅ Reusable across the system
- ❌ No business logic
- ❌ No application state
- ❌ No layer-specific code

Utils are the bedrock - reliable, simple, and universally useful.
