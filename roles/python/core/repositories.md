# Repositories Layer

## Purpose

Repositories handle **all persistence operations**, providing a clean abstraction over data storage. They are responsible for file I/O, serialization, and ensuring data consistency.

## Responsibilities

1. **Data Persistence** - Save/load models to/from storage
2. **File Operations** - All file system interactions
3. **Serialization** - Convert between models and storage format (JSON)
4. **Locking** - Ensure safe concurrent access
5. **Storage Abstraction** - Hide implementation details

## Rules

### ✅ DO

- Handle all file I/O operations
- Serialize/deserialize models
- Use file locking for concurrency
- Provide clean CRUD interface
- Return models, not raw data
- Handle storage errors gracefully

### ❌ DON'T

- **NO business logic** - Repositories are dumb storage
- **NO data validation** - That's for models and validators
- **NO data transformation** - That's for domains
- **NO service coordination** - Services call repositories, not vice versa
- **NO calling other layers** - Only models and utils allowed

## File Structure

```
repositories/
├── file_repository.py      # Base class for file operations
└── session_repository.py   # Session persistence
```

## Dependencies

**Allowed:**
- ✅ models/ - Work with data models
- ✅ utils/ - File locking, datetime utilities
- ✅ Standard library (os, json, shutil)

**Forbidden:**
- ❌ services/ - Repositories serve services, not vice versa
- ❌ domains/ - No business logic
- ❌ agents/ - No external integrations

## Example

```python
"""Repository for Session persistence."""

import json
import os
from typing import TYPE_CHECKING

from pipe.core.models.settings import Settings
from pipe.core.utils.file import FileLock

if TYPE_CHECKING:
    from pipe.core.models.session import Session

class SessionRepository:
    """
    Handles Session file I/O.
    
    Business Rules:
    - Sessions stored as {session_id}.json
    - File locking prevents concurrent writes
    - Atomic writes via temp file + rename
    """
    
    def __init__(self, project_root: str, settings: Settings):
        self.storage_dir = os.path.join(project_root, settings.session_path)
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def save(self, session: "Session") -> None:
        """Save session atomically."""
        path = self._get_path(session.session_id)
        lock_path = f"{path}.lock"
        
        with FileLock(lock_path):
            # Atomic write: temp file + rename
            temp_path = f"{path}.tmp"
            with open(temp_path, "w") as f:
                json.dump(session.model_dump(), f, indent=2)
            os.rename(temp_path, path)
    
    def load(self, session_id: str) -> "Session":
        """Load session by ID."""
        from pipe.core.models.session import Session
        
        path = self._get_path(session_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(path) as f:
            data = json.load(f)
        return Session(**data)
    
    def delete(self, session_id: str) -> None:
        """Delete session file."""
        path = self._get_path(session_id)
        if os.path.exists(path):
            os.remove(path)
    
    def list_all(self) -> list[str]:
        """List all session IDs."""
        return [
            f[:-5]  # Remove .json
            for f in os.listdir(self.storage_dir)
            if f.endswith(".json")
        ]
    
    def _get_path(self, session_id: str) -> str:
        """Get file path for session."""
        return os.path.join(self.storage_dir, f"{session_id}.json")
```

## Common Patterns

### Pattern 1: Atomic Write

```python
def save(self, entity: Model) -> None:
    """Save with atomic write (temp + rename)."""
    temp_path = f"{path}.tmp"
    with open(temp_path, "w") as f:
        json.dump(entity.model_dump(), f)
    os.rename(temp_path, path)  # Atomic on POSIX
```

### Pattern 2: File Locking

```python
def save(self, entity: Model) -> None:
    """Save with file lock for concurrency."""
    with FileLock(f"{path}.lock"):
        with open(path, "w") as f:
            json.dump(entity.model_dump(), f)
```

### Pattern 3: Error Handling

```python
def load(self, entity_id: str) -> Model:
    """Load with clear error messages."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Entity {entity_id} not found")
    
    try:
        with open(path) as f:
            data = json.load(f)
        return Model(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")
```

## Testing

```python
# tests/core/repositories/test_session_repository.py

def test_save_creates_file(tmp_path):
    """Test save creates JSON file."""
    repo = SessionRepository(str(tmp_path), settings)
    session = create_test_session()
    
    repo.save(session)
    
    path = tmp_path / "sessions" / f"{session.session_id}.json"
    assert path.exists()

def test_load_returns_session(tmp_path):
    """Test load deserializes correctly."""
    repo = SessionRepository(str(tmp_path), settings)
    original = create_test_session()
    repo.save(original)
    
    loaded = repo.load(original.session_id)
    
    assert loaded.session_id == original.session_id
    assert loaded.purpose == original.purpose

def test_delete_removes_file(tmp_path):
    """Test delete removes file."""
    repo = SessionRepository(str(tmp_path), settings)
    session = create_test_session()
    repo.save(session)
    
    repo.delete(session.session_id)
    
    path = tmp_path / "sessions" / f"{session.session_id}.json"
    assert not path.exists()
```

## Summary

**Repositories:**
- ✅ All file I/O operations
- ✅ Serialization/deserialization
- ✅ File locking for concurrency
- ✅ Clean CRUD interface
- ❌ No business logic, validation, or transformation
- ❌ Only called by services

**Repositories manage HOW data is stored, not WHAT data means**
