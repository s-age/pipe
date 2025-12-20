from __future__ import annotations

import zoneinfo
from typing import TYPE_CHECKING, Any, ClassVar, TypedDict

from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.base import CamelCaseModel
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.todo import TodoItem
from pydantic import ConfigDict, Field, PrivateAttr, model_validator
from pydantic.alias_generators import to_camel


class TodoItemInput(TypedDict, total=False):
    """Typed dictionary for TodoItem input data."""

    title: str
    description: str | None
    checked: bool


class HyperparametersInput(TypedDict, total=False):
    """Typed dictionary for Hyperparameters input data."""

    temperature: float | None
    top_p: float | None
    top_k: float | None


class ReferenceInput(TypedDict, total=False):
    """Typed dictionary for Reference input data."""

    path: str
    disabled: bool
    ttl: int | None
    persist: bool


class TurnResponseInput(TypedDict, total=False):
    """Typed dictionary for TurnResponse input data."""

    status: str
    message: str


class UserTaskTurnInput(TypedDict):
    """Typed dictionary for UserTaskTurn input data."""

    type: str
    instruction: str
    timestamp: str


class ModelResponseTurnInput(TypedDict):
    """Typed dictionary for ModelResponseTurn input data."""

    type: str
    content: str
    timestamp: str


class FunctionCallingTurnInput(TypedDict):
    """Typed dictionary for FunctionCallingTurn input data."""

    type: str
    response: str
    timestamp: str


class ToolResponseTurnInput(TypedDict):
    """Typed dictionary for ToolResponseTurn input data."""

    type: str
    name: str
    response: TurnResponseInput
    timestamp: str


class CompressedHistoryTurnInput(TypedDict):
    """Typed dictionary for CompressedHistoryTurn input data."""

    type: str
    content: str
    original_turns_range: list[int]
    timestamp: str


# Type alias for Turn inputs
TurnInputType = (
    UserTaskTurnInput
    | ModelResponseTurnInput
    | FunctionCallingTurnInput
    | ToolResponseTurnInput
    | CompressedHistoryTurnInput
)


class SessionInputData(TypedDict, total=False):
    """Typed dictionary for Session input data during deserialization from JSON."""

    session_id: str
    created_at: str
    purpose: str | None
    background: str | None
    roles: list[str]
    multi_step_reasoning_enabled: bool
    token_count: int
    cached_content_token_count: int
    hyperparameters: HyperparametersInput | None
    references: list[ReferenceInput]
    artifacts: list[str]
    procedure: str | None
    turns: list[TurnInputType]
    pools: list[TurnInputType]
    todos: list[TodoItemInput | str]
    raw_response: str | None


class SessionMetaUpdate(CamelCaseModel):
    """Session metadata update DTO.

    All fields are optional to support partial updates (PATCH).
    Only provided fields will be updated.
    """

    purpose: str | None = None
    background: str | None = None
    roles: list[str] | None = None
    multi_step_reasoning_enabled: bool | None = None
    artifacts: list[str] | None = None
    procedure: str | None = None


class Session(CamelCaseModel):
    """
    Represents a single user session, corresponding to a unique session file
    (e.g., `${session_id}.json`).
    This class is responsible for holding the detailed state of a conversation and
    persisting itself to a file.
    It does not manage the collection of all sessions or the index file.
    """

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data: SessionInputData) -> SessionInputData:
        # Preprocess multi_step_reasoning_enabled (convert null to False)
        if "multi_step_reasoning_enabled" in data:
            if data["multi_step_reasoning_enabled"] is None:
                data["multi_step_reasoning_enabled"] = False

        # Preprocess todos
        if "todos" in data:
            if data["todos"] is None:
                data["todos"] = []
            elif data["todos"] is not None:
                processed_todos = []
                for item in data["todos"]:
                    if isinstance(item, str):
                        processed_todos.append(TodoItem(title=item))
                    elif isinstance(item, TodoItem):
                        processed_todos.append(item)
                    else:
                        # Assume it's dict-like with TodoItem fields
                        processed_todos.append(TodoItem(**item))
                data["todos"] = processed_todos

        # Preprocess hyperparameters
        if "hyperparameters" in data and data["hyperparameters"] is not None:
            if isinstance(data["hyperparameters"], Hyperparameters):
                pass  # Already Hyperparameters, leave it as is
            else:
                # Assume it's dict-like with Hyperparameters fields
                data["hyperparameters"] = Hyperparameters(**data["hyperparameters"])

        return data

    if TYPE_CHECKING:
        from pipe.core.models.args import TaktArgs
        from pipe.core.models.prompt import Prompt
        from pipe.core.models.settings import Settings

    # --- Pydantic Configuration ---
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    # --- Class Variables for Configuration (used by factories) ---
    sessions_dir: ClassVar[str | None] = None
    backups_dir: ClassVar[str | None] = None
    timezone_obj: ClassVar[zoneinfo.ZoneInfo | None] = None
    default_hyperparameters: ClassVar[Hyperparameters | None] = None
    reference_ttl: ClassVar[int] = 3

    # --- Private Instance Attributes for self-contained persistence ---
    _sessions_dir: str | None = PrivateAttr(None)
    _backups_dir: str | None = PrivateAttr(None)
    _timezone_obj: zoneinfo.ZoneInfo | None = PrivateAttr(None)
    _default_hyperparameters: Hyperparameters | None = PrivateAttr(None)
    _reference_ttl: int = PrivateAttr(3)

    # --- Public Fields ---
    session_id: str
    created_at: str
    purpose: str | None = None
    background: str | None = None
    roles: list[str] = []
    multi_step_reasoning_enabled: bool = False
    token_count: int = 0
    cached_content_token_count: int = 0  # From last API response usage_metadata
    hyperparameters: Hyperparameters | None = None
    references: ReferenceCollection = Field(default_factory=ReferenceCollection)
    artifacts: list[str] = []
    procedure: str | None = None
    turns: TurnCollection = Field(default_factory=TurnCollection)
    pools: TurnCollection = Field(default_factory=TurnCollection)
    todos: list[TodoItem] = Field(default_factory=list)
    raw_response: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """Initializes instance-specific configurations after the model is created.

        Note: __context parameter type is Any because it's a Pydantic framework
        requirement. The context parameter is opaque and not used.
        """
        # Populate private attributes from class variables. This ensures that
        # instances created by factories or direct instantiation are self-contained.
        self._sessions_dir = self.__class__.sessions_dir
        self._backups_dir = self.__class__.backups_dir
        self._timezone_obj = self.__class__.timezone_obj
        self._default_hyperparameters = self.__class__.default_hyperparameters
        self._reference_ttl = self.__class__.reference_ttl

        # Configure the reference collection with the instance-specific TTL
        if self.references:
            self.references.default_ttl = self._reference_ttl
