# Repositories Layer

## Purpose

Repositories are the **persistence layer**, providing a clean abstraction over data storage and retrieval. They handle all file I/O operations, ensuring that the rest of the application remains independent of storage implementation details.

## Responsibilities

1. **Data Persistence** - Save and load domain models to/from storage
2. **File Operations** - Handle all file system interactions
3. **Data Serialization** - Convert between models and storage format (JSON, etc.)
4. **Locking and Concurrency** - Ensure safe concurrent access
5. **Storage Abstraction** - Hide storage implementation from other layers

## Characteristics

- ✅ All file I/O operations
- ✅ Data serialization/deserialization
- ✅ File locking for concurrent access
- ✅ Storage format management (JSON, YAML, etc.)
- ✅ Backup and recovery operations
- ❌ **NO business logic** - repositories are dumb data stores
- ❌ **NO data validation** - that's for models and validators
- ❌ **NO data transformation** - that's for domains
- ❌ **NO service coordination** - repositories serve services

## File Structure

```
repositories/
├── __init__.py
├── file_repository.py      # Base class for file operations
└── session_repository.py   # Session persistence
```

## Dependencies

**Allowed:**

- ✅ `models/` - To work with data models
- ✅ `utils/` - For file locking, datetime utilities
- ✅ Standard library (os, json, shutil, etc.)

**Forbidden:**

- ❌ `services/` - Repositories are called BY services
- ❌ `domains/` - No business logic
- ❌ `agents/` - No external integrations
- ❌ `delegates/` - Wrong direction of dependency

## Template

```python
"""
Repository for managing [Entity] persistence.
"""

import json
import os
from typing import TYPE_CHECKING

from pipe.core.models.settings import Settings
from pipe.core.utils.file import FileLock

if TYPE_CHECKING:
    from pipe.core.models.some_model import SomeModel


class SomeRepository:
    """
    Handles reading and writing of [Entity] objects to/from filesystem.

    Responsibilities:
    - Save entity to storage
    - Load entity from storage
    - Delete entity from storage
    - List all entities
    - Handle file locking
    """

    def __init__(self, project_root: str, settings: Settings):
        """
        Initialize repository with storage location.

        Args:
            project_root: Path to project root
            settings: Application settings
        """
        self.project_root = project_root
        self.settings = settings

        # Define storage paths
        self.storage_dir = os.path.join(
            project_root,
            settings.storage_path
        )
        self.lock_path = os.path.join(self.storage_dir, ".lock")

        # Initialize storage directory
        self._initialize_storage()

    def _initialize_storage(self) -> None:
        """
        Creates storage directory if it doesn't exist.
        """
        os.makedirs(self.storage_dir, exist_ok=True)

    def save(self, entity: "SomeModel") -> None:
        """
        Saves entity to storage.

        Args:
            entity: Entity to save

        Raises:
            RuntimeError: If save operation fails
        """
        entity_path = self._get_entity_path(entity.id)

        try:
            with FileLock(self.lock_path):
                # Serialize to JSON
                data = entity.model_dump(mode="json")

                # Write to file
                with open(entity_path, 'w') as f:
                    json.dump(data, f, indent=2)

        except OSError as e:
            raise RuntimeError(f"Failed to save entity {entity.id}: {e}") from e

    def find(self, entity_id: str) -> "SomeModel | None":
        """
        Loads entity from storage.

        Args:
            entity_id: ID of entity to load

        Returns:
            Entity if found, None otherwise

        Raises:
            RuntimeError: If load operation fails
        """
        entity_path = self._get_entity_path(entity_id)

        if not os.path.exists(entity_path):
            return None

        try:
            with open(entity_path, 'r') as f:
                data = json.load(f)

            # Deserialize from JSON
            from pipe.core.models.some_model import SomeModel
            return SomeModel(**data)

        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load entity {entity_id}: {e}") from e

    def delete(self, entity_id: str) -> bool:
        """
        Deletes entity from storage.

        Args:
            entity_id: ID of entity to delete

        Returns:
            True if deleted, False if not found

        Raises:
            RuntimeError: If delete operation fails
        """
        entity_path = self._get_entity_path(entity_id)

        if not os.path.exists(entity_path):
            return False

        try:
            with FileLock(self.lock_path):
                os.remove(entity_path)
            return True

        except OSError as e:
            raise RuntimeError(f"Failed to delete entity {entity_id}: {e}") from e

    def list_all(self) -> list[str]:
        """
        Lists all entity IDs in storage.

        Returns:
            List of entity IDs
        """
        try:
            if not os.path.exists(self.storage_dir):
                return []

            files = os.listdir(self.storage_dir)
            # Filter for entity files (e.g., *.json)
            entity_ids = [
                f[:-5]  # Remove .json extension
                for f in files
                if f.endswith('.json')
            ]
            return entity_ids

        except OSError:
            return []

    def _get_entity_path(self, entity_id: str) -> str:
        """
        Gets file path for entity.

        Args:
            entity_id: Entity ID

        Returns:
            Absolute path to entity file
        """
        return os.path.join(self.storage_dir, f"{entity_id}.json")
```

## Real Examples

### SessionRepository - Session Persistence

**Key Responsibilities:**

- Save/load session files (${session_id}.json)
- Manage session index (index.json)
- Handle session backups
- Provide atomic operations with file locking

```python
"""
Repository for managing Session persistence.
"""

import hashlib
import os
import shutil
import json
from typing import TYPE_CHECKING

from pipe.core.models.settings import Settings
from pipe.core.repositories.file_repository import FileRepository
from pipe.core.utils.file import FileLock
from pipe.core.utils.datetime import get_current_timestamp

if TYPE_CHECKING:
    from pipe.core.models.session import Session


class SessionRepository(FileRepository):
    """
    Handles reading and writing of Session objects to/from filesystem.

    File Structure:
    - sessions/${session_id}.json - Individual session files
    - sessions/index.json - Session index/catalog
    - sessions/backups/ - Backup directory
    """

    def __init__(self, project_root: str, settings: Settings):
        super().__init__()
        self.project_root = project_root
        self.settings = settings

        # Define paths
        self.sessions_dir = os.path.join(project_root, settings.sessions_path)
        self.backups_dir = os.path.join(self.sessions_dir, "backups")
        self.index_path = os.path.join(self.sessions_dir, "index.json")
        self.index_lock_path = f"{self.index_path}.lock"

        # Initialize directories
        self._initialize_dirs()

    def _initialize_dirs(self) -> None:
        """
        Creates necessary directories for session storage.
        """
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)

    def find(self, session_id: str) -> "Session | None":
        """
        Loads session from file.

        Args:
            session_id: Session ID to load

        Returns:
            Session if found, None otherwise
        """
        session_path = self._get_session_path(session_id)

        if not os.path.exists(session_path):
            return None

        try:
            data = self._read_json(session_path)
            from pipe.core.models.session import Session
            return Session(**data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def save(self, session: "Session") -> None:
        """
        Saves session to file and updates index.

        This is an atomic operation using file locking.

        Args:
            session: Session to save

        Raises:
            RuntimeError: If save fails
        """
        session_path = self._get_session_path(session.id)

        try:
            # Create backup if session exists
            if os.path.exists(session_path):
                self._create_backup(session.id)

            # Save session file
            with FileLock(f"{session_path}.lock"):
                data = session.model_dump(mode="json")
                self._write_json(session_path, data)

            # Update index
            self._update_index(session)

        except OSError as e:
            raise RuntimeError(f"Failed to save session {session.id}: {e}") from e

    def delete(self, session_id: str) -> bool:
        """
        Deletes session file and removes from index.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        session_path = self._get_session_path(session_id)

        if not os.path.exists(session_path):
            return False

        try:
            # Create backup before deleting
            self._create_backup(session_id)

            # Delete session file
            with FileLock(f"{session_path}.lock"):
                os.remove(session_path)

            # Remove from index
            self._remove_from_index(session_id)

            return True

        except OSError as e:
            raise RuntimeError(f"Failed to delete session {session_id}: {e}") from e

    def list_all(self) -> list[str]:
        """
        Lists all session IDs from index.

        Returns:
            List of session IDs
        """
        try:
            if not os.path.exists(self.index_path):
                return []

            index = self._read_json(self.index_path)
            return list(index.keys())

        except Exception:
            return []

    def get_session_metadata(self, session_id: str) -> dict | None:
        """
        Gets session metadata from index without loading full session.

        Args:
            session_id: Session ID

        Returns:
            Metadata dict if found, None otherwise
        """
        try:
            if not os.path.exists(self.index_path):
                return None

            index = self._read_json(self.index_path)
            return index.get(session_id)

        except Exception:
            return None

    def _get_session_path(self, session_id: str) -> str:
        """
        Gets file path for session.

        Args:
            session_id: Session ID

        Returns:
            Absolute path to session file
        """
        return os.path.join(self.sessions_dir, f"{session_id}.json")

    def _create_backup(self, session_id: str) -> None:
        """
        Creates backup of session file.

        Args:
            session_id: Session ID to backup
        """
        session_path = self._get_session_path(session_id)

        if not os.path.exists(session_path):
            return

        timestamp = get_current_timestamp().replace(":", "-")
        backup_name = f"{session_id}_{timestamp}.json"
        backup_path = os.path.join(self.backups_dir, backup_name)

        shutil.copy2(session_path, backup_path)

    def _update_index(self, session: "Session") -> None:
        """
        Updates session index with metadata.

        Args:
            session: Session to add/update in index
        """
        with FileLock(self.index_lock_path):
            # Load existing index
            if os.path.exists(self.index_path):
                index = self._read_json(self.index_path)
            else:
                index = {}

            # Update metadata
            index[session.id] = {
                "purpose": session.purpose,
                "created_at": session.created_at,
                "updated_at": get_current_timestamp(),
                "parent_id": session.parent_id,
                "turn_count": len(session.turns),
            }

            # Write updated index
            self._write_json(self.index_path, index)

    def _remove_from_index(self, session_id: str) -> None:
        """
        Removes session from index.

        Args:
            session_id: Session ID to remove
        """
        with FileLock(self.index_lock_path):
            if not os.path.exists(self.index_path):
                return

            index = self._read_json(self.index_path)
            index.pop(session_id, None)
            self._write_json(self.index_path, index)
```

### FileRepository - Base Repository Class

**Key Responsibilities:**

- Provide common file operations
- Standardize JSON read/write
- Handle file locking utilities
- Base class for all repositories

```python
"""
Base repository class providing common file operations.
"""

import json
import os
from typing import Any


class FileRepository:
    """
    Base class for repositories that store data in files.

    Provides common file I/O operations with consistent error handling.
    """

    def _read_json(self, file_path: str) -> dict:
        """
        Reads and parses JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON data

        Raises:
            RuntimeError: If read or parse fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to read JSON from {file_path}: {e}") from e

    def _write_json(self, file_path: str, data: dict | list) -> None:
        """
        Writes data to JSON file with pretty printing.

        Args:
            file_path: Path to JSON file
            data: Data to write

        Raises:
            RuntimeError: If write fails
        """
        try:
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write with pretty formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Trailing newline

        except OSError as e:
            raise RuntimeError(f"Failed to write JSON to {file_path}: {e}") from e

    def _read_text(self, file_path: str) -> str:
        """
        Reads text file.

        Args:
            file_path: Path to text file

        Returns:
            File contents

        Raises:
            RuntimeError: If read fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except OSError as e:
            raise RuntimeError(f"Failed to read text from {file_path}: {e}") from e

    def _write_text(self, file_path: str, content: str) -> None:
        """
        Writes text to file.

        Args:
            file_path: Path to text file
            content: Content to write

        Raises:
            RuntimeError: If write fails
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        except OSError as e:
            raise RuntimeError(f"Failed to write text to {file_path}: {e}") from e

    def _file_exists(self, file_path: str) -> bool:
        """
        Checks if file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists
        """
        return os.path.exists(file_path)

    def _delete_file(self, file_path: str) -> None:
        """
        Deletes file if it exists.

        Args:
            file_path: Path to delete

        Raises:
            RuntimeError: If delete fails
        """
        if not self._file_exists(file_path):
            return

        try:
            os.remove(file_path)
        except OSError as e:
            raise RuntimeError(f"Failed to delete {file_path}: {e}") from e
```

## Repository Patterns

### Pattern 1: Atomic Operations with Locking

```python
def save(self, entity: Entity) -> None:
    """
    Atomic save with file locking.
    """
    entity_path = self._get_entity_path(entity.id)

    with FileLock(f"{entity_path}.lock"):
        # All operations here are atomic
        data = entity.model_dump()
        self._write_json(entity_path, data)
        self._update_index(entity)
```

### Pattern 2: Backup Before Modify

```python
def update(self, entity: Entity) -> None:
    """
    Updates entity with automatic backup.
    """
    if self._file_exists(self._get_entity_path(entity.id)):
        self._create_backup(entity.id)

    self.save(entity)
```

### Pattern 3: Index Maintenance

```python
def save(self, entity: Entity) -> None:
    """
    Saves entity and maintains index.
    """
    # Save main file
    self._save_entity_file(entity)

    # Update index (metadata only)
    self._update_index({
        "id": entity.id,
        "name": entity.name,
        "updated_at": get_current_timestamp(),
    })
```

## Testing

### Unit Testing Repositories

```python
# tests/core/repositories/test_session_repository.py
import pytest
import tempfile
import os

from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings


@pytest.fixture
def temp_dir():
    """Creates temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def repository(temp_dir):
    """Creates repository with temp storage."""
    settings = Settings(sessions_path="sessions")
    return SessionRepository(temp_dir, settings)


def test_save_and_load_session(repository):
    # Create session
    session = Session(
        id="test123",
        purpose="Test",
        background="Testing",
        turns=[],
    )

    # Save
    repository.save(session)

    # Load
    loaded = repository.find("test123")

    # Verify
    assert loaded is not None
    assert loaded.id == "test123"
    assert loaded.purpose == "Test"


def test_find_nonexistent_session(repository):
    result = repository.find("nonexistent")
    assert result is None


def test_delete_session(repository):
    # Create and save
    session = Session(id="test123", purpose="Test", background="Testing", turns=[])
    repository.save(session)

    # Delete
    result = repository.delete("test123")
    assert result is True

    # Verify deleted
    loaded = repository.find("test123")
    assert loaded is None


def test_list_all_sessions(repository):
    # Create multiple sessions
    for i in range(3):
        session = Session(
            id=f"test{i}",
            purpose=f"Test {i}",
            background="Testing",
            turns=[],
        )
        repository.save(session)

    # List
    session_ids = repository.list_all()

    # Verify
    assert len(session_ids) == 3
    assert "test0" in session_ids
    assert "test1" in session_ids
    assert "test2" in session_ids


def test_concurrent_access(repository):
    """Tests file locking prevents corruption."""
    import threading

    session = Session(id="test123", purpose="Test", background="Testing", turns=[])
    repository.save(session)

    def modify_session():
        for _ in range(10):
            loaded = repository.find("test123")
            loaded.purpose = f"Updated {threading.current_thread().name}"
            repository.save(loaded)

    threads = [threading.Thread(target=modify_session) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify no corruption
    final = repository.find("test123")
    assert final is not None
    assert "Updated" in final.purpose
```

## Best Practices

### 1. Always Use File Locking

```python
# ✅ GOOD: Use locking for concurrent access
def save(self, entity: Entity) -> None:
    with FileLock(self.lock_path):
        self._write_json(path, data)

# ❌ BAD: No locking
def save(self, entity: Entity) -> None:
    self._write_json(path, data)  # Race condition!
```

### 2. Handle Errors Gracefully

```python
# ✅ GOOD: Clear error handling
def find(self, entity_id: str) -> Entity | None:
    try:
        data = self._read_json(path)
        return Entity(**data)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Corrupted data: {e}") from e

# ❌ BAD: Let errors propagate
def find(self, entity_id: str) -> Entity:
    data = self._read_json(path)  # May raise various exceptions
    return Entity(**data)
```

### 3. Create Backups for Updates

```python
# ✅ GOOD: Backup before overwriting
def save(self, entity: Entity) -> None:
    if self._file_exists(path):
        self._create_backup(entity.id)
    self._write_json(path, data)

# ❌ BAD: Overwrite without backup
def save(self, entity: Entity) -> None:
    self._write_json(path, data)  # Data loss if write fails
```

### 4. Keep Repositories Dumb

```python
# ✅ GOOD: Repository just stores/retrieves
def save(self, session: Session) -> None:
    data = session.model_dump()
    self._write_json(path, data)

# ❌ BAD: Repository contains business logic
def save(self, session: Session) -> None:
    # Business logic doesn't belong here
    if len(session.turns) > 100:
        session.turns = session.turns[-50:]
    data = session.model_dump()
    self._write_json(path, data)
```

## Summary

Repositories are the **persistence abstraction**:

- ✅ All file I/O operations
- ✅ Data serialization/deserialization
- ✅ File locking for safety
- ✅ Backup and recovery
- ❌ No business logic
- ❌ No data validation
- ❌ No transformation

Repositories are **dumb storage** - they save what you give them and return what they have.
