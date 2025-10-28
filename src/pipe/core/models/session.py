import hashlib
import json
import os
import zoneinfo

from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.reference import Reference
from pipe.core.models.todo import TodoItem
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import locked_json_write, read_json_file
from pydantic import BaseModel, ConfigDict, Field


class Session(BaseModel):
    """
    Represents a single user session, corresponding to a unique session file
    (e.g., `${session_id}.json`).
    This class is responsible for holding the detailed state of a conversation and
    persisting itself to a file.
    It does not manage the collection of all sessions or the index file.
    """

    # --- Pydantic Configuration ---
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # --- Class Variables for Configuration ---
    sessions_dir: str | None = None
    timezone_obj: zoneinfo.ZoneInfo | None = None
    default_hyperparameters: Hyperparameters | None = None

    session_id: str
    created_at: str
    purpose: str | None = None
    background: str | None = None
    roles: list[str] = []
    multi_step_reasoning_enabled: bool = False
    token_count: int = 0
    hyperparameters: Hyperparameters | None = None
    references: list[Reference] = Field(default_factory=list)
    turns: TurnCollection = Field(default_factory=TurnCollection)
    pools: TurnCollection = Field(default_factory=TurnCollection)
    todos: list[TodoItem] | None = None

    @classmethod
    def setup(
        cls,
        sessions_dir: str,
        timezone_obj: zoneinfo.ZoneInfo,
        default_hyperparameters: Hyperparameters,
    ):
        """Injects necessary configurations into the Session class."""
        cls.sessions_dir = sessions_dir
        cls.timezone_obj = timezone_obj
        cls.default_hyperparameters = default_hyperparameters

    def _get_session_path(self) -> str:
        if not self.__class__.sessions_dir:
            raise ValueError("Session.sessions_dir is not configured.")
        safe_path_parts = [
            part for part in self.session_id.split("/") if part not in ("", ".", "..")
        ]
        final_path = os.path.join(self.__class__.sessions_dir, *safe_path_parts)
        return f"{final_path}.json"

    def _get_lock_path(self) -> str:
        return f"{self._get_session_path()}.lock"

    def save(self):
        """Saves the session to a JSON file using a locked write utility."""
        if self.references:
            ref_collection = ReferenceCollection(self.references)
            ref_collection.sort_by_ttl()

        session_path = self._get_session_path()
        lock_path = self._get_lock_path()

        os.makedirs(os.path.dirname(session_path), exist_ok=True)
        locked_json_write(lock_path, session_path, self.model_dump(mode="json"))

    @classmethod
    def _get_path_for_id(cls, session_id: str) -> str:
        """A static utility to get a session path without needing an instance."""
        if not cls.sessions_dir:
            raise ValueError("Session.sessions_dir is not configured.")
        safe_path_parts = [
            part for part in session_id.split("/") if part not in ("", ".", "..")
        ]
        final_path = os.path.join(cls.sessions_dir, *safe_path_parts)
        return f"{final_path}.json"

    @classmethod
    def find(cls, session_id: str) -> "Session | None":
        """Loads a single session from its JSON file, applying data migrations if
        necessary."""
        if not cls.sessions_dir or not cls.timezone_obj:
            raise ValueError("Session class is not configured.")

        session_path = cls._get_path_for_id(session_id)

        try:
            data = read_json_file(session_path)
        except (FileNotFoundError, ValueError):
            return None

        # --- Data Migration ---
        session_creation_time = data.get(
            "created_at", get_current_timestamp(cls.timezone_obj)
        )
        for turn_list_key in ["turns", "pools"]:
            if turn_list_key in data and isinstance(data[turn_list_key], list):
                for turn_data in data[turn_list_key]:
                    if isinstance(turn_data, dict):
                        if "timestamp" not in turn_data:
                            turn_data["timestamp"] = session_creation_time
                        if (
                            turn_data.get("type") == "compressed_history"
                            and "original_turns_range" not in turn_data
                        ):
                            turn_data["original_turns_range"] = [0, 0]
        # --- End of Data Migration ---

        instance = cls.model_validate(data)
        return instance

    @classmethod
    def create(
        cls,
        purpose: str,
        background: str,
        roles: list,
        multi_step_reasoning_enabled: bool = False,
        token_count: int = 0,
        hyperparameters: dict | None = None,
        parent_id: str | None = None,
    ) -> "Session":
        if not cls.timezone_obj or not cls.default_hyperparameters:
            raise ValueError("Session class is not configured.")

        if parent_id:
            parent_session = cls.find(parent_id)
            if not parent_session:
                raise FileNotFoundError(
                    f"Parent session with ID '{parent_id}' not found."
                )

        timestamp = get_current_timestamp(cls.timezone_obj)
        identity_str = json.dumps(
            {
                "purpose": purpose,
                "background": background,
                "roles": roles,
                "multi_step_reasoning_enabled": multi_step_reasoning_enabled,
                "timestamp": timestamp,
            },
            sort_keys=True,
        )
        session_hash = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

        session_id = f"{parent_id}/{session_hash}" if parent_id else session_hash

        session = cls(
            session_id=session_id,
            created_at=timestamp,
            purpose=purpose,
            background=background,
            roles=roles,
            multi_step_reasoning_enabled=multi_step_reasoning_enabled,
            token_count=token_count,
            hyperparameters=hyperparameters
            if hyperparameters is not None
            else cls.default_hyperparameters,
        )

        session.save()
        return session

    def edit_meta(self, new_meta_data: dict):
        """Updates metadata and saves the session."""
        if "purpose" in new_meta_data:
            self.purpose = new_meta_data["purpose"]
        if "background" in new_meta_data:
            self.background = new_meta_data["background"]
        if "multi_step_reasoning_enabled" in new_meta_data:
            self.multi_step_reasoning_enabled = new_meta_data[
                "multi_step_reasoning_enabled"
            ]
        if "token_count" in new_meta_data:
            self.token_count = new_meta_data["token_count"]
        if "hyperparameters" in new_meta_data:
            self.hyperparameters = new_meta_data["hyperparameters"]

        self.save()

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
            "turns": [t.model_dump() for t in self.turns],
            "pools": [p.model_dump() for p in self.pools],
            "todos": [t.model_dump() for t in self.todos] if self.todos else [],
        }
