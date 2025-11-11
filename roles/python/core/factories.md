# Factories Layer

## Purpose

Factories provide **centralized object creation** and dependency injection. They construct complex objects with proper dependencies, abstracting creation logic from the rest of the system.

## Responsibilities

1. **Object Creation** - Construct services, agents, repositories
2. **Dependency Injection** - Wire dependencies together
3. **Configuration** - Apply settings during construction
4. **Initialization** - Ensure objects are properly set up
5. **Single Point of Control** - Centralize creation patterns

## Characteristics

- ✅ Centralized creation logic
- ✅ Dependency wiring
- ✅ Configuration application
- ✅ Single point of instantiation
- ❌ **NO business logic** - only construction
- ❌ **NO workflows** - just create objects
- ❌ **NO state management** - factories are stateless

## File Structure

```
factories/
├── __init__.py
└── service_factory.py    # Service construction
```

## Dependencies

**Allowed:**

- ✅ `services/` - To create services
- ✅ `repositories/` - To create repositories
- ✅ `agents/` - To create agents
- ✅ `models/` - For type definitions (Settings, etc.)

**Forbidden:**

- ❌ `delegates/` - Delegates use factories, not vice versa
- ❌ `domains/` - Factories don't contain business logic

## Template

```python
"""
Factory for creating [component type] with dependencies.
"""

from pipe.core.models.settings import Settings


class ComponentFactory:
    """
    Creates [components] with proper dependencies.

    This factory:
    1. Centralizes object creation
    2. Wires dependencies
    3. Applies configuration
    4. Ensures proper initialization
    """

    def __init__(self, project_root: str, settings: Settings):
        """
        Initialize factory with configuration.

        Args:
            project_root: Path to project root
            settings: Application settings
        """
        self.project_root = project_root
        self.settings = settings

    def create_component(self, *args, **kwargs) -> Component:
        """
        Creates component with dependencies.

        Returns:
            Fully configured component
        """
        # Create dependencies
        dependency = self._create_dependency()

        # Create and return component
        return Component(
            project_root=self.project_root,
            settings=self.settings,
            dependency=dependency,
            *args,
            **kwargs,
        )

    def _create_dependency(self) -> Dependency:
        """
        Internal helper for creating dependencies.

        Private methods encapsulate creation steps.
        """
        return Dependency(self.settings)
```

## Real Example

### ServiceFactory - Service Construction

**Key Responsibilities:**

- Create all services with proper dependencies
- Wire repositories to services
- Apply settings during creation
- Provide cached instances (singleton pattern)

```python
"""
Factory for creating services with dependencies.
"""

from pipe.core.models.settings import Settings
from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.token_service import TokenService
from pipe.core.repositories.session_repository import SessionRepository


class ServiceFactory:
    """
    Creates services with proper dependencies.

    This factory ensures:
    - Services get the correct dependencies
    - Settings are properly applied
    - Single instances are reused (singleton pattern)
    """

    def __init__(self, project_root: str, settings: Settings):
        """
        Initialize factory with configuration.

        Args:
            project_root: Path to project root directory
            settings: Application settings
        """
        self.project_root = project_root
        self.settings = settings

        # Cache for singleton instances
        self._session_service: SessionService | None = None
        self._prompt_service: PromptService | None = None
        self._token_service: TokenService | None = None
        self._session_repository: SessionRepository | None = None

    def create_session_service(self) -> SessionService:
        """
        Creates SessionService with dependencies.

        Uses singleton pattern - creates once, returns cached instance.

        Returns:
            SessionService instance
        """
        if self._session_service is None:
            repository = self.create_session_repository()
            self._session_service = SessionService(
                project_root=self.project_root,
                settings=self.settings,
                repository=repository,
            )

        return self._session_service

    def create_prompt_service(self) -> PromptService:
        """
        Creates PromptService with dependencies.

        Returns:
            PromptService instance
        """
        if self._prompt_service is None:
            session_service = self.create_session_service()
            self._prompt_service = PromptService(
                project_root=self.project_root,
                settings=self.settings,
                session_service=session_service,
            )

        return self._prompt_service

    def create_token_service(self) -> TokenService:
        """
        Creates TokenService.

        TokenService has no dependencies, but factory provides
        consistent creation pattern.

        Returns:
            TokenService instance
        """
        if self._token_service is None:
            self._token_service = TokenService(
                settings=self.settings,
            )

        return self._token_service

    def create_session_repository(self) -> SessionRepository:
        """
        Creates SessionRepository.

        Repository is a dependency of SessionService.

        Returns:
            SessionRepository instance
        """
        if self._session_repository is None:
            self._session_repository = SessionRepository(
                project_root=self.project_root,
                settings=self.settings,
            )

        return self._session_repository

    def create_all_services(self) -> dict[str, Any]:
        """
        Creates all services at once.

        Useful for initialization or testing.

        Returns:
            Dictionary of service name to service instance
        """
        return {
            'session': self.create_session_service(),
            'prompt': self.create_prompt_service(),
            'token': self.create_token_service(),
        }
```

## Factory Patterns

### Pattern 1: Singleton Pattern

Factory caches instances to ensure only one exists:

```python
class ServiceFactory:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._service: Service | None = None  # Cache

    def create_service(self) -> Service:
        """Returns cached instance or creates new one."""
        if self._service is None:
            self._service = Service(self.settings)
        return self._service
```

### Pattern 2: Builder Pattern

For complex objects, use builder pattern:

```python
class ServiceFactory:
    def create_service(self) -> Service:
        """Builds service step by step."""
        # Step 1: Create dependencies
        repo = self._create_repository()
        cache = self._create_cache()

        # Step 2: Apply configuration
        config = self._build_config()

        # Step 3: Construct service
        service = Service(
            repository=repo,
            cache=cache,
            config=config,
        )

        # Step 4: Initialize
        service.initialize()

        return service
```

### Pattern 3: Factory Method

For variations of same type:

```python
class AgentFactory:
    def create_agent(self, agent_type: str) -> Agent:
        """Creates different agent types."""
        if agent_type == "gemini_api":
            return self._create_gemini_api_agent()
        elif agent_type == "gemini_cli":
            return self._create_gemini_cli_agent()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    def _create_gemini_api_agent(self) -> GeminiAPIAgent:
        return GeminiAPIAgent(api_key=self.settings.api_key)

    def _create_gemini_cli_agent(self) -> GeminiCLIAgent:
        return GeminiCLIAgent(cli_path=self.settings.cli_path)
```

### Pattern 4: Lazy Initialization

Create objects only when needed:

```python
class ServiceFactory:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._services: dict[str, Any] = {}

    def get_service(self, name: str) -> Any:
        """Lazily creates and caches service."""
        if name not in self._services:
            self._services[name] = self._create_service(name)
        return self._services[name]

    def _create_service(self, name: str) -> Any:
        if name == 'session':
            return SessionService(...)
        elif name == 'prompt':
            return PromptService(...)
        # etc.
```

## Usage Example

### In Main Entry Point

```python
# src/pipe/core/dispatcher.py

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings

def main():
    # Load settings
    settings = Settings.load_from_yaml("settings.yml")

    # Create factory
    factory = ServiceFactory(
        project_root="/path/to/project",
        settings=settings,
    )

    # Create services via factory
    session_service = factory.create_session_service()
    prompt_service = factory.create_prompt_service()

    # Use services
    session = session_service.start_session(...)
```

### In Tests

```python
# tests/test_workflow.py

@pytest.fixture
def factory():
    """Provides factory with test settings."""
    settings = Settings(
        sessions_path="test_sessions",
        timezone="UTC",
    )
    return ServiceFactory(
        project_root="/tmp/test",
        settings=settings,
    )

def test_workflow(factory):
    # Create services via factory
    session_service = factory.create_session_service()

    # Test workflow
    session_id = session_service.start_session("Test", "Testing")
    assert session_id is not None
```

## Testing

### Unit Testing Factory

```python
# tests/core/factories/test_service_factory.py

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings


def test_create_session_service():
    settings = Settings(sessions_path="sessions", timezone="UTC")
    factory = ServiceFactory("/test", settings)

    service = factory.create_session_service()

    assert service is not None
    assert service.project_root == "/test"
    assert service.settings == settings


def test_singleton_pattern():
    """Factory should return same instance."""
    settings = Settings(sessions_path="sessions", timezone="UTC")
    factory = ServiceFactory("/test", settings)

    service1 = factory.create_session_service()
    service2 = factory.create_session_service()

    assert service1 is service2  # Same instance


def test_dependency_injection():
    """Factory should wire dependencies correctly."""
    settings = Settings(sessions_path="sessions", timezone="UTC")
    factory = ServiceFactory("/test", settings)

    prompt_service = factory.create_prompt_service()

    # PromptService should have SessionService dependency
    assert prompt_service.session_service is not None


def test_create_all_services():
    settings = Settings(sessions_path="sessions", timezone="UTC")
    factory = ServiceFactory("/test", settings)

    services = factory.create_all_services()

    assert 'session' in services
    assert 'prompt' in services
    assert 'token' in services
```

## Best Practices

### 1. Centralize Object Creation

```python
# ✅ GOOD: Use factory for all creation
factory = ServiceFactory(project_root, settings)
service = factory.create_session_service()

# ❌ BAD: Create directly scattered throughout code
repository = SessionRepository(project_root, settings)
service = SessionService(project_root, settings, repository)
```

### 2. Use Singleton When Appropriate

```python
# ✅ GOOD: Cache expensive objects
def create_session_service(self) -> SessionService:
    if self._session_service is None:
        self._session_service = SessionService(...)
    return self._session_service

# ❌ BAD: Create new instance every time
def create_session_service(self) -> SessionService:
    return SessionService(...)  # New instance each time
```

### 3. Keep Factories Simple

```python
# ✅ GOOD: Factory only creates objects
def create_service(self) -> Service:
    return Service(self.settings)

# ❌ BAD: Factory contains business logic
def create_service(self) -> Service:
    service = Service(self.settings)
    service.initialize_database()  # Business logic!
    service.load_data()  # Business logic!
    return service
```

### 4. Clear Dependency Order

```python
# ✅ GOOD: Dependencies created first
def create_prompt_service(self) -> PromptService:
    # Create dependency first
    session_service = self.create_session_service()

    # Then create dependent service
    return PromptService(
        session_service=session_service,
        ...
    )

# ❌ BAD: Circular dependencies
def create_service_a(self) -> ServiceA:
    service_b = self.create_service_b()  # Depends on B
    return ServiceA(service_b)

def create_service_b(self) -> ServiceB:
    service_a = self.create_service_a()  # Depends on A - circular!
    return ServiceB(service_a)
```

## Advanced Patterns

### Configurable Factory

```python
class ServiceFactory:
    """Factory with configurable behavior."""

    def __init__(
        self,
        project_root: str,
        settings: Settings,
        use_cache: bool = True,
    ):
        self.project_root = project_root
        self.settings = settings
        self.use_cache = use_cache
        self._cache: dict[str, Any] = {}

    def create_service(self, service_type: str) -> Any:
        # Use cache if enabled
        if self.use_cache and service_type in self._cache:
            return self._cache[service_type]

        # Create service
        service = self._create_service_by_type(service_type)

        # Cache if enabled
        if self.use_cache:
            self._cache[service_type] = service

        return service
```

### Environment-Aware Factory

```python
class ServiceFactory:
    """Factory that adapts to environment."""

    def __init__(self, project_root: str, settings: Settings, env: str):
        self.project_root = project_root
        self.settings = settings
        self.env = env  # 'development', 'test', 'production'

    def create_repository(self) -> Repository:
        """Creates repository appropriate for environment."""
        if self.env == 'test':
            # Use in-memory repository for tests
            return InMemoryRepository()
        else:
            # Use file repository for dev/prod
            return FileRepository(self.project_root, self.settings)
```

## Summary

Factories are the **construction layer**:

- ✅ Centralized object creation
- ✅ Dependency injection
- ✅ Configuration application
- ✅ Singleton pattern support
- ❌ No business logic
- ❌ No workflows
- ❌ No state (except caching)

Factories ensure objects are created correctly and consistently throughout the system.
