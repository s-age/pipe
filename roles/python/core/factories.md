# Factories Layer

## Purpose

Factories provide **object construction logic** with dependency injection. They centralize complex initialization and manage dependency graphs.

## Responsibilities

1. **Dependency Injection** - Wire dependencies
2. **Object Construction** - Create configured instances
3. **Configuration Management** - Load and apply settings
4. **Singleton Management** - Manage shared instances
5. **Lazy Initialization** - Create on demand

## Rules

### ✅ DO

- Centralize object construction
- Inject dependencies
- Load configuration
- Manage object lifecycle
- Provide clean initialization API

### ❌ DON'T

- **NO business logic** - Only construction
- **NO persistence** - Factories create, don't save
- **NO complex orchestration** - Just wire dependencies
- **NO state beyond construction** - Create and return

## File Structure

```
factories/
├── service_factory.py    # Service construction
├── agent_factory.py      # Agent construction
└── ...
```

## Dependencies

**Allowed:**
- ✅ All layers (to construct them)
- ✅ Settings/Config
- ✅ Standard library

**Forbidden:**
- ❌ Complex business logic
- ❌ Persistence operations

## Example

```python
"""Service factory."""

from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_workflow_service import SessionWorkflowService
from pipe.core.services.session_turn_service import SessionTurnService

class ServiceFactory:
    """
    Constructs services with dependencies.
    
    Manages dependency injection for service layer.
    """
    
    def __init__(self, project_root: str, settings: Settings):
        self.project_root = project_root
        self.settings = settings
        
        # Shared instances
        self._session_repo = None
    
    def get_session_repository(self) -> SessionRepository:
        """Get or create session repository (singleton)."""
        if self._session_repo is None:
            self._session_repo = SessionRepository(
                self.project_root,
                self.settings
            )
        return self._session_repo
    
    def create_workflow_service(self) -> SessionWorkflowService:
        """Create workflow service with dependencies."""
        return SessionWorkflowService(
            session_repo=self.get_session_repository(),
            timezone=self.settings.timezone
        )
    
    def create_turn_service(self) -> SessionTurnService:
        """Create turn service with dependencies."""
        return SessionTurnService(
            session_repo=self.get_session_repository()
        )
```

## Common Patterns

### Pattern 1: Singleton Management

```python
def get_repository(self) -> Repository:
    """Get singleton repository."""
    if self._repo is None:
        self._repo = Repository(self.config)
    return self._repo
```

### Pattern 2: Factory Method

```python
def create_service(self, service_type: str) -> Service:
    """Create service by type."""
    if service_type == "workflow":
        return self.create_workflow_service()
    elif service_type == "turn":
        return self.create_turn_service()
    raise ValueError(f"Unknown service type: {service_type}")
```

### Pattern 3: Configuration Loading

```python
def __init__(self, config_path: str):
    """Initialize with config."""
    self.settings = Settings.from_file(config_path)
    self.project_root = self.settings.project_root
```

## Testing

```python
# tests/core/factories/test_service_factory.py

def test_factory_creates_workflow_service():
    """Test factory creates workflow service."""
    factory = ServiceFactory(str(tmp_path), settings)
    
    service = factory.create_workflow_service()
    
    assert isinstance(service, SessionWorkflowService)

def test_factory_reuses_repository():
    """Test factory returns same repository instance."""
    factory = ServiceFactory(str(tmp_path), settings)
    
    repo1 = factory.get_session_repository()
    repo2 = factory.get_session_repository()
    
    assert repo1 is repo2
```

## Summary

**Factories:**
- ✅ Object construction
- ✅ Dependency injection
- ✅ Configuration management
- ✅ Singleton management
- ❌ No business logic or persistence

**Factories wire dependencies, services implement operations**
