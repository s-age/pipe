from __future__ import annotations

import os
import zoneinfo
from typing import TYPE_CHECKING, Any, ClassVar

from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.todo import TodoItem
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator


class SessionMetaUpdate(BaseModel):
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


class Session(BaseModel):
    """
    Represents a single user session, corresponding to a unique session file
    (e.g., `${session_id}.json`).
    This class is responsible for holding the detailed state of a conversation and
    persisting itself to a file.
    It does not manage the collection of all sessions or the index file.
    """

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        # Preprocess todos
        if "todos" in data and data["todos"] is not None:
            processed_todos = []
            for item in data["todos"]:
                if isinstance(item, str):
                    processed_todos.append(TodoItem(title=item))
                elif isinstance(item, dict):
                    processed_todos.append(TodoItem(**item))
                else:
                    processed_todos.append(item)
            data["todos"] = processed_todos

        # Preprocess hyperparameters
        if "hyperparameters" in data and data["hyperparameters"] is not None:
            if isinstance(data["hyperparameters"], dict):
                data["hyperparameters"] = Hyperparameters(**data["hyperparameters"])
            # If it's already Hyperparameters, leave it as is

        return data

    if TYPE_CHECKING:
        from pipe.core.models.args import TaktArgs
        from pipe.core.models.prompt import Prompt
        from pipe.core.models.settings import Settings

    # --- Pydantic Configuration ---
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
    hyperparameters: Hyperparameters | None = None
    references: ReferenceCollection = Field(default_factory=ReferenceCollection)
    artifacts: list[str] = []
    procedure: str | None = None
    turns: TurnCollection = Field(default_factory=TurnCollection)
    pools: TurnCollection = Field(default_factory=TurnCollection)
    todos: list[TodoItem] | None = None

    def model_post_init(self, __context: Any) -> None:
        """Initializes instance-specific configurations after the model is created."""
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

    @property
    def file_path(self) -> str:
        return self._get_session_path()

    @classmethod
    def setup(
        cls,
        sessions_dir: str,
        backups_dir: str,
        settings: Settings,
    ):
        """Injects necessary configurations into the Session class from settings."""
        cls.sessions_dir = sessions_dir
        cls.backups_dir = backups_dir
        try:
            cls.timezone_obj = zoneinfo.ZoneInfo(settings.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            cls.timezone_obj = zoneinfo.ZoneInfo("UTC")

        cls.reference_ttl = settings.reference_ttl

        default_hyperparameters_dict = {
            "temperature": settings.parameters.temperature.value,
            "top_p": settings.parameters.top_p.value,
            "top_k": settings.parameters.top_k.value,
        }
        cls.default_hyperparameters = Hyperparameters(**default_hyperparameters_dict)

    def _get_session_path(self) -> str:
        if not self._sessions_dir:
            raise ValueError("Session._sessions_dir is not configured.")
        safe_path_parts = [
            part for part in self.session_id.split("/") if part not in ("", ".", "..")
        ]
        final_path = os.path.join(self._sessions_dir, *safe_path_parts)
        return f"{final_path}.json"

    def _get_lock_path(self) -> str:
        return f"{self._get_session_path()}.lock"

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the session suitable for templates."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "purpose": self.purpose,
            "background": self.background,
            "roles": self.roles,
            "multi_step_reasoning_enabled": self.multi_step_reasoning_enabled,
            "token_count": self.token_count,
            "hyperparameters": (
                self.hyperparameters.model_dump() if self.hyperparameters else None
            ),
            "references": [r.model_dump() for r in self.references],
            "artifacts": self.artifacts,
            "procedure": self.procedure,
            "turns": [t.model_dump() for t in self.turns],
            "pools": [p.model_dump() for p in self.pools],
            "todos": [t.model_dump() for t in self.todos] if self.todos else [],
        }
