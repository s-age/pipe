from __future__ import annotations

import hashlib
import json
import os
import zoneinfo
from typing import TYPE_CHECKING, Any, ClassVar

from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.todo import TodoItem
from pipe.core.models.turn import Turn
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import (
    FileLock,
    delete_file,
)
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class Session(BaseModel):
    """
    Represents a single user session, corresponding to a unique session file
    (e.g., `${session_id}.json`).
    This class is responsible for holding the detailed state of a conversation and
    persisting itself to a file.
    It does not manage the collection of all sessions or the index file.
    """

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
            "temperature": settings.parameters.temperature.model_dump(),
            "top_p": settings.parameters.top_p.model_dump(),
            "top_k": settings.parameters.top_k.model_dump(),
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

    def destroy(self):
        """Deletes the session's JSON file and lock file."""
        session_path = self._get_session_path()
        lock_path = self._get_lock_path()
        with FileLock(lock_path):
            delete_file(session_path)

    def fork(self, fork_index: int, timezone_obj: zoneinfo.ZoneInfo) -> Session:
        """Creates a new, in-memory Session object by forking this one."""
        from pipe.core.collections.turns import TurnCollection

        timestamp = get_current_timestamp(timezone_obj)
        forked_purpose = f"Fork of: {self.purpose}"
        forked_turns = TurnCollection(self.turns[: fork_index + 1])

        identity_str = json.dumps(
            {
                "purpose": forked_purpose,
                "original_id": self.session_id,
                "fork_at_turn": fork_index,
                "timestamp": timestamp,
            },
            sort_keys=True,
        )
        new_session_id_suffix = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

        parent_path = (
            self.session_id.rsplit("/", 1)[0] if "/" in self.session_id else None
        )
        new_session_id = (
            f"{parent_path}/{new_session_id_suffix}"
            if parent_path
            else new_session_id_suffix
        )

        return Session(
            session_id=new_session_id,
            created_at=timestamp,
            purpose=forked_purpose,
            background=self.background,
            roles=self.roles,
            multi_step_reasoning_enabled=self.multi_step_reasoning_enabled,
            hyperparameters=self.hyperparameters,
            references=self.references,
            artifacts=self.artifacts,
            procedure=self.procedure,
            turns=forked_turns,
        )

    def edit_meta(self, new_meta_data: dict):
        """Updates metadata and saves the session."""
        if "purpose" in new_meta_data:
            self.purpose = new_meta_data["purpose"]
        if "background" in new_meta_data:
            self.background = new_meta_data["background"]
        if "roles" in new_meta_data:
            self.roles = new_meta_data["roles"]
        if "multi_step_reasoning_enabled" in new_meta_data:
            self.multi_step_reasoning_enabled = new_meta_data[
                "multi_step_reasoning_enabled"
            ]
        if "artifacts" in new_meta_data:
            self.artifacts = new_meta_data["artifacts"]
        if "procedure" in new_meta_data:
            self.procedure = new_meta_data["procedure"]
        if "token_count" in new_meta_data:
            self.token_count = new_meta_data["token_count"]
        if "hyperparameters" in new_meta_data:
            self.hyperparameters = Hyperparameters(**new_meta_data["hyperparameters"])

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
            "hyperparameters": self.hyperparameters.model_dump()
            if self.hyperparameters
            else None,
            "references": [r.model_dump() for r in self.references],
            "artifacts": self.artifacts,
            "procedure": self.procedure,
            "turns": [t.model_dump() for t in self.turns],
            "pools": [p.model_dump() for p in self.pools],
            "todos": [t.model_dump() for t in self.todos] if self.todos else [],
        }

    def add_turn(self, turn_data: Turn):
        """Adds a turn to the session's history."""
        self.turns.append(turn_data)

    def edit_turn(self, turn_index: int, new_data: dict):
        """Edits a specific turn in the session's history."""
        from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn

        if not (0 <= turn_index < len(self.turns)):
            raise IndexError("Turn index out of range.")

        original_turn = self.turns[turn_index]
        if original_turn.type not in ["user_task", "model_response"]:
            raise ValueError(
                f"Editing turns of type '{original_turn.type}' is not allowed."
            )

        turn_as_dict = original_turn.model_dump()
        turn_as_dict.update(new_data)

        if original_turn.type == "user_task":
            self.turns[turn_index] = UserTaskTurn(**turn_as_dict)
        elif original_turn.type == "model_response":
            self.turns[turn_index] = ModelResponseTurn(**turn_as_dict)

    def delete_turn(self, turn_index: int):
        """Deletes a specific turn from the session's history."""
        if not (0 <= turn_index < len(self.turns)):
            raise IndexError("Turn index out of range.")
        del self.turns[turn_index]

    def merge_pool(self):
        """Merges the turn pool into the main history."""
        from pipe.core.collections.turns import TurnCollection

        if self.pools:
            self.turns.extend(self.pools)
            self.pools = TurnCollection()
