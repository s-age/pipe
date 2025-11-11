# Models Layer

## Purpose

Models are **pure data structures** defined with Pydantic. They represent the core domain entities with strict type safety, validation, and serialization capabilities. Models are the atomic building blocks of the entire system.

## Responsibilities

1. **Data Structure Definition** - Define the shape of domain entities
2. **Type Safety** - Enforce type constraints at runtime
3. **Validation** - Ensure data integrity through Pydantic validators
4. **Serialization** - Convert between Python objects and JSON/dict
5. **Immutability Contracts** - Define which fields can/cannot be modified

## Characteristics

- ✅ Pydantic BaseModel subclasses
- ✅ Type-annotated fields
- ✅ Field validators for data integrity
- ✅ Serialization/deserialization support
- ✅ Clear, self-documenting structure
- ❌ **NO business logic** - models are data containers
- ❌ **NO external dependencies** - only Pydantic and stdlib
- ❌ **NO service/repository access** - models are passive
- ❌ **NO side effects** - models don't do I/O

## File Structure

```
models/
├── __init__.py
├── args.py              # CLI arguments
├── artifact.py          # Artifact definition
├── hyperparameters.py   # Model hyperparameters
├── prompt.py            # Prompt structure
├── reference.py         # File reference
├── session.py           # Session (main entity)
├── settings.py          # Application settings
├── todo.py              # Todo item
├── turn.py              # Turn types (conversation)
└── prompts/             # Prompt-specific models
    └── ...
```

## Dependencies

**Allowed:**

- ✅ Pydantic (BaseModel, Field, validators)
- ✅ Standard library (datetime, enum, typing)
- ✅ Other models (composition)

**Forbidden:**

- ❌ Any other core layer (services, domains, repositories, etc.)
- ❌ External libraries (except Pydantic)
- ❌ File I/O
- ❌ Business logic

## Template

```python
"""
Model for [Entity Name].
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, ConfigDict


class EntityModel(BaseModel):
    """
    Represents [entity description].

    Attributes:
        id: Unique identifier
        name: Human-readable name
        status: Current status
        created_at: Creation timestamp
    """

    # Configure model behavior
    model_config = ConfigDict(
        frozen=False,  # Set to True for immutable models
        validate_assignment=True,  # Validate on field assignment
        arbitrary_types_allowed=False,  # Usually False unless needed
    )

    # Fields with type annotations
    id: str = Field(
        ...,  # Required field
        description="Unique identifier",
        min_length=1,
    )

    name: str = Field(
        default="",
        description="Human-readable name",
    )

    status: Literal["active", "inactive", "pending"] = Field(
        default="pending",
        description="Current status",
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )

    # Optional: Field validators
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validates name field.

        This is DATA VALIDATION, not business logic.
        """
        if v and not v.strip():
            raise ValueError("Name cannot be only whitespace")
        return v.strip()

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validates ID format."""
        if not v or len(v) < 8:
            raise ValueError("ID must be at least 8 characters")
        return v
```

## Real Examples

### Session - Main Domain Entity

**Key Characteristics:**

- Central entity representing a conversation session
- Composed of multiple sub-models (Turns, References, etc.)
- Handles serialization/deserialization
- Validates data integrity

```python
from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.todo import TodoItem
from pipe.core.models.turn import Turn


class Session(BaseModel):
    """
    Represents a single user session.

    This is the main entity, corresponding to a session file (${session_id}.json).
    It holds the complete state of a conversation including:
    - Conversation history (turns)
    - File references
    - Todo items
    - Hyperparameters
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable - session evolves over time
        validate_assignment=True,  # Validate on updates
        arbitrary_types_allowed=True,  # For custom collections
    )

    # Core identity
    id: str = Field(
        ...,
        description="Unique session identifier (hash of purpose + background)",
    )

    purpose: str = Field(
        ...,
        description="The overall purpose/goal of the session",
    )

    background: str = Field(
        ...,
        description="Background context for the session",
    )

    # Session metadata
    created_at: str = Field(
        ...,
        description="Session creation timestamp (ISO format)",
    )

    parent_id: str | None = Field(
        default=None,
        description="ID of parent session (if this is a fork)",
    )

    roles: list[str] = Field(
        default_factory=list,
        description="Paths to role definition files",
    )

    # Session content
    turns: TurnCollection = Field(
        default_factory=TurnCollection,
        description="Conversation history",
    )

    references: ReferenceCollection = Field(
        default_factory=ReferenceCollection,
        description="File references with TTL",
    )

    todos: list[TodoItem] = Field(
        default_factory=list,
        description="Todo items for this session",
    )

    artifacts: list[str] = Field(
        default_factory=list,
        description="Expected output artifacts (file paths)",
    )

    # Configuration
    hyperparameters: Hyperparameters = Field(
        default_factory=Hyperparameters,
        description="Model hyperparameters (temperature, etc.)",
    )

    multi_step_reasoning: bool = Field(
        default=False,
        description="Whether to use multi-step reasoning mode",
    )

    # Pre-processing validator for backward compatibility
    @model_validator(mode="before")
    @classmethod
    def _preprocess_todos(cls, data: Any) -> Any:
        """
        Handles legacy todo format (plain strings).

        This is DATA VALIDATION, not business logic.
        """
        if isinstance(data, dict) and "todos" in data and data["todos"] is not None:
            processed_todos = []
            for item in data["todos"]:
                if isinstance(item, str):
                    # Convert legacy string format
                    processed_todos.append(TodoItem(title=item))
                elif isinstance(item, dict):
                    processed_todos.append(TodoItem(**item))
                else:
                    processed_todos.append(item)
            data["todos"] = processed_todos
        return data
```

### Turn - Conversation Element

**Key Characteristics:**

- Polymorphic turn types (UserTask, ModelResponse, ToolResponse, etc.)
- Each turn type has specific fields
- Common timestamp field
- Used in TurnCollection

```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Turn(BaseModel):
    """
    Base class for all turn types.

    A turn represents a single element in the conversation history.
    """

    model_config = ConfigDict(frozen=True)  # Turns are immutable once created

    type: str = Field(
        ...,
        description="Turn type discriminator",
    )

    timestamp: str = Field(
        ...,
        description="Turn timestamp (ISO format)",
    )


class UserTaskTurn(Turn):
    """
    User's task/instruction turn.
    """

    type: Literal["user_task"] = "user_task"
    message: str = Field(
        ...,
        description="User's instruction or task",
    )


class ModelResponseTurn(Turn):
    """
    AI model's response turn.
    """

    type: Literal["model_response"] = "model_response"
    message: str = Field(
        ...,
        description="Model's response text",
    )


class FunctionCallingTurn(Turn):
    """
    Model's function/tool call request.
    """

    type: Literal["function_calling"] = "function_calling"
    tool_name: str = Field(
        ...,
        description="Name of tool to call",
    )

    tool_args: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for tool call",
    )


class ToolResponseTurn(Turn):
    """
    Result of tool execution.
    """

    type: Literal["tool_response"] = "tool_response"
    tool_name: str = Field(
        ...,
        description="Name of tool that was called",
    )

    message: str = Field(
        ...,
        description="Tool execution result",
    )

    succeeded: bool = Field(
        default=True,
        description="Whether tool execution succeeded",
    )
```

### Reference - File Reference with TTL

```python
from pydantic import BaseModel, Field, field_validator


class Reference(BaseModel):
    """
    Represents a file reference with Time-To-Live.

    References can be:
    - Persistent (TTL = -1): Never expire
    - Temporary (TTL > 0): Expire after N turns
    """

    model_config = ConfigDict(frozen=False)

    path: str = Field(
        ...,
        description="Relative path to file from project root",
    )

    ttl: int = Field(
        default=5,
        description="Time-to-live: -1 for persistent, N for temporary",
    )

    persistent: bool = Field(
        default=False,
        description="Whether reference persists across sessions",
    )

    @field_validator('path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        """
        Validates path is not empty.

        Business rules (like checking if path is within project root)
        belong in domains/, not here.
        """
        if not v or not v.strip():
            raise ValueError("Reference path cannot be empty")
        return v.strip()

    @field_validator('ttl')
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        """Validates TTL is -1 or positive."""
        if v < -1:
            raise ValueError("TTL must be -1 (persistent) or >= 0")
        return v
```

### TodoItem - Task Item

```python
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class TodoStatus(str, Enum):
    """Todo item status."""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class TodoItem(BaseModel):
    """
    Represents a todo item in a session.
    """

    model_config = ConfigDict(frozen=False)

    id: int = Field(
        default=0,
        description="Unique ID within session",
    )

    title: str = Field(
        ...,
        description="Todo title/summary",
    )

    description: str = Field(
        default="",
        description="Detailed description",
    )

    status: TodoStatus = Field(
        default=TodoStatus.NOT_STARTED,
        description="Current status",
    )

    created_at: str | None = Field(
        default=None,
        description="Creation timestamp",
    )

    completed_at: str | None = Field(
        default=None,
        description="Completion timestamp",
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validates title is not empty."""
        if not v or not v.strip():
            raise ValueError("Todo title cannot be empty")
        return v.strip()
```

### Hyperparameters - Model Configuration

```python
from pydantic import BaseModel, Field, field_validator


class Hyperparameters(BaseModel):
    """
    Model hyperparameters for AI generation.
    """

    model_config = ConfigDict(frozen=False)

    temperature: float = Field(
        default=1.0,
        description="Sampling temperature (0.0 to 2.0)",
    )

    top_p: float = Field(
        default=0.95,
        description="Nucleus sampling threshold",
    )

    top_k: int = Field(
        default=40,
        description="Top-k sampling parameter",
    )

    max_output_tokens: int = Field(
        default=8192,
        description="Maximum tokens in response",
    )

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validates temperature range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

    @field_validator('top_p')
    @classmethod
    def validate_top_p(cls, v: float) -> float:
        """Validates top_p range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Top_p must be between 0.0 and 1.0")
        return v

    @field_validator('max_output_tokens')
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """Validates max tokens is positive."""
        if v <= 0:
            raise ValueError("Max output tokens must be positive")
        return v
```

### Settings - Application Configuration

```python
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Application-wide settings loaded from YAML.
    """

    model_config = ConfigDict(frozen=True)  # Settings are immutable

    sessions_path: str = Field(
        default="sessions",
        description="Path to sessions directory",
    )

    timezone: str = Field(
        default="UTC",
        description="Timezone for timestamps",
    )

    default_model: str = Field(
        default="gemini-2.0-flash",
        description="Default AI model to use",
    )

    max_context_tokens: int = Field(
        default=1000000,
        description="Maximum context window size",
    )

    tool_response_limit: int = Field(
        default=3,
        description="Max tool responses in prompt",
    )
```

## Model Patterns

### Pattern 1: Composition

```python
class Session(BaseModel):
    """Session composed of multiple models."""
    turns: TurnCollection
    references: ReferenceCollection
    hyperparameters: Hyperparameters
    todos: list[TodoItem]
```

### Pattern 2: Inheritance for Polymorphism

```python
class Turn(BaseModel):
    """Base turn class."""
    type: str
    timestamp: str

class UserTaskTurn(Turn):
    """Specific turn type."""
    type: Literal["user_task"] = "user_task"
    message: str
```

### Pattern 3: Custom Serialization

```python
class Session(BaseModel):
    def to_json_file(self, path: str) -> None:
        """
        Custom serialization (though this should be in repository).
        Prefer keeping models pure and moving I/O to repositories.
        """
        data = self.model_dump(mode="json")
        # ... save to file
```

### Pattern 4: Model Validators for Data Integrity

```python
@model_validator(mode="after")
def validate_consistency(self) -> "Session":
    """
    Cross-field validation.

    Use sparingly - complex validation might belong in validators/ layer.
    """
    if self.status == "completed" and not self.completed_at:
        raise ValueError("Completed sessions must have completion time")
    return self
```

## Field Types

### Common Field Types

```python
from typing import Literal, Any
from datetime import datetime

class Model(BaseModel):
    # Primitive types
    text: str
    number: int
    decimal: float
    flag: bool

    # Optional types
    optional_text: str | None = None

    # Literal (enum-like)
    status: Literal["active", "inactive", "pending"]

    # Collections
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Nested models
    config: Configuration
    items: list[TodoItem]

    # Datetime (prefer str for JSON serialization)
    created_at: str  # ISO format
    # or
    created_at: datetime
```

### Field Constraints

```python
from pydantic import Field

class Model(BaseModel):
    # String constraints
    name: str = Field(min_length=1, max_length=100)

    # Numeric constraints
    age: int = Field(ge=0, le=150)  # greater/equal, less/equal
    score: float = Field(gt=0.0, lt=1.0)  # greater than, less than

    # Pattern matching
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

    # Description for documentation
    id: str = Field(..., description="Unique identifier")
```

## Testing Models

### Unit Testing

```python
# tests/core/models/test_session.py
import pytest
from pipe.core.models.session import Session
from pipe.core.models.turn import UserTaskTurn


def test_session_creation():
    session = Session(
        id="test123",
        purpose="Test purpose",
        background="Test background",
        created_at="2024-01-01T00:00:00",
    )

    assert session.id == "test123"
    assert session.purpose == "Test purpose"
    assert len(session.turns) == 0


def test_session_validation():
    with pytest.raises(ValueError):
        Session(
            id="",  # Invalid: empty ID
            purpose="Test",
            background="Test",
            created_at="2024-01-01T00:00:00",
        )


def test_session_serialization():
    session = Session(
        id="test123",
        purpose="Test",
        background="Test",
        created_at="2024-01-01T00:00:00",
    )

    # Serialize
    data = session.model_dump()

    # Deserialize
    restored = Session(**data)

    assert restored.id == session.id
    assert restored.purpose == session.purpose


def test_turn_immutability():
    turn = UserTaskTurn(
        message="Test task",
        timestamp="2024-01-01T00:00:00",
    )

    with pytest.raises(Exception):
        turn.message = "Modified"  # Should fail if frozen=True
```

## Best Practices

### 1. Keep Models Pure

```python
# ✅ GOOD: Pure data model
class Session(BaseModel):
    id: str
    purpose: str
    turns: list[Turn]

# ❌ BAD: Business logic in model
class Session(BaseModel):
    id: str
    purpose: str
    turns: list[Turn]

    def filter_recent_turns(self):  # Business logic doesn't belong here
        return self.turns[-10:]
```

### 2. Use Validators for Data Integrity Only

```python
# ✅ GOOD: Data validation
@field_validator('email')
@classmethod
def validate_email(cls, v: str) -> str:
    if '@' not in v:
        raise ValueError("Invalid email format")
    return v

# ❌ BAD: Business logic in validator
@field_validator('status')
@classmethod
def validate_status(cls, v: str) -> str:
    if v == 'inactive':
        send_notification()  # Side effect! Doesn't belong here
    return v
```

### 3. Prefer Immutability When Possible

```python
# ✅ GOOD: Immutable for value objects
class Turn(BaseModel):
    model_config = ConfigDict(frozen=True)  # Can't be modified
    timestamp: str
    message: str

# ✅ GOOD: Mutable for entities that evolve
class Session(BaseModel):
    model_config = ConfigDict(frozen=False)
    turns: list[Turn]  # Can add turns over time
```

### 4. Document Models Well

```python
# ✅ GOOD: Clear documentation
class Session(BaseModel):
    """
    Represents a single user session.

    A session contains the complete conversation history and context
    for an AI interaction, including turns, references, and todos.

    Attributes:
        id: Unique session identifier (SHA256 hash)
        purpose: Overall goal of the session
        turns: Chronological conversation history
    """
    id: str = Field(..., description="Unique session identifier")
    purpose: str = Field(..., description="Overall goal")
    turns: list[Turn] = Field(default_factory=list, description="History")
```

## Summary

Models are the **foundation** of the system:

- ✅ Pure data structures with Pydantic
- ✅ Type-safe and validated
- ✅ Serialization support
- ✅ Self-documenting
- ❌ No business logic
- ❌ No external dependencies
- ❌ No side effects

Models define **what** the data looks like, while other layers define **what to do** with it.
