import hashlib
import json
import os
import sys
import zoneinfo
from typing import TYPE_CHECKING, ClassVar

from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.todo import TodoItem
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import (
    FileLock,
    copy_file,
    create_directory,
    delete_file,
    locked_json_write,
    read_json_file,
)
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from pipe.core.models.args import TaktArgs
    from pipe.core.models.prompt import Prompt
    from pipe.core.models.settings import Settings


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
    sessions_dir: ClassVar[str | None] = None
    backups_dir: ClassVar[str | None] = None
    timezone_obj: ClassVar[zoneinfo.ZoneInfo | None] = None
    default_hyperparameters: ClassVar[Hyperparameters | None] = None

    session_id: str
    created_at: str
    purpose: str | None = None
    background: str | None = None
    roles: list[str] = []
    multi_step_reasoning_enabled: bool = False
    token_count: int = 0
    hyperparameters: Hyperparameters | None = None
    references: ReferenceCollection = Field(default_factory=ReferenceCollection)
    turns: TurnCollection = Field(default_factory=TurnCollection)
    pools: TurnCollection = Field(default_factory=TurnCollection)
    todos: list[TodoItem] | None = None

    @property
    def file_path(self) -> str:
        return self._get_session_path()

    @classmethod
    def setup(
        cls,
        sessions_dir: str,
        backups_dir: str,
        timezone_name: str,
        default_hyperparameters: Hyperparameters,
    ):
        """Injects necessary configurations into the Session class."""
        cls.sessions_dir = sessions_dir
        cls.backups_dir = backups_dir
        try:
            cls.timezone_obj = zoneinfo.ZoneInfo(timezone_name)
        except zoneinfo.ZoneInfoNotFoundError:
            cls.timezone_obj = zoneinfo.ZoneInfo("UTC")
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

        create_directory(os.path.dirname(session_path))
        locked_json_write(lock_path, session_path, self.model_dump(mode="json"))

    def backup(self):
        """Creates a timestamped backup of the session file."""
        if not self.__class__.backups_dir or not self.__class__.timezone_obj:
            raise ValueError("Session.backups_dir is not configured.")

        session_path = self._get_session_path()
        if not os.path.exists(session_path):
            return

        session_hash = hashlib.sha256(self.session_id.encode("utf-8")).hexdigest()
        timestamp = get_current_timestamp(self.__class__.timezone_obj).replace(":", "")
        backup_filename = f"{session_hash}-{timestamp}.json"
        backup_path = os.path.join(self.__class__.backups_dir, backup_filename)

        copy_file(session_path, backup_path)

    def destroy(self):
        """Deletes the session's JSON file and lock file."""
        session_path = self._get_session_path()
        lock_path = self._get_lock_path()
        with FileLock(lock_path):
            delete_file(session_path)

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
        if "roles" in new_meta_data:
            self.roles = new_meta_data["roles"]
        if "multi_step_reasoning_enabled" in new_meta_data:
            self.multi_step_reasoning_enabled = new_meta_data[
                "multi_step_reasoning_enabled"
            ]
        if "token_count" in new_meta_data:
            self.token_count = new_meta_data["token_count"]
        if "hyperparameters" in new_meta_data:
            self.hyperparameters = Hyperparameters(**new_meta_data["hyperparameters"])

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

    def to_prompt(self, settings: "Settings", project_root: str) -> "Prompt":
        """Builds and returns a Prompt object from this session's data."""
        from pipe.core.collections.todos import TodoCollection
        from pipe.core.models.prompt import Prompt
        from pipe.core.models.prompts.constraints import (
            PromptConstraints,
            PromptHyperparameters,
        )
        from pipe.core.models.prompts.conversation_history import (
            PromptConversationHistory,
        )
        from pipe.core.models.prompts.current_task import PromptCurrentTask
        from pipe.core.models.prompts.file_reference import PromptFileReference
        from pipe.core.models.prompts.roles import PromptRoles
        from pipe.core.models.prompts.session_goal import PromptSessionGoal
        from pipe.core.models.prompts.todo import PromptTodo

        # 1. Build Hyperparameters
        merged_params = settings.parameters.model_dump()
        if self.hyperparameters:
            session_params = self.hyperparameters.model_dump()
            for key, value_desc_pair in session_params.items():
                if (
                    key in merged_params
                    and value_desc_pair
                    and "value" in value_desc_pair
                ):
                    merged_params[key]["value"] = value_desc_pair["value"]

        hyperparameters = PromptHyperparameters.from_merged_params(merged_params)

        # 2. Build Constraints
        constraints = PromptConstraints.build(
            settings, hyperparameters, self.multi_step_reasoning_enabled
        )

        # 3. Build other prompt components
        roles = PromptRoles.build(self.roles, project_root)

        references_with_content = list(self.references.get_for_prompt(project_root))
        prompt_references = [
            PromptFileReference(**ref) for ref in references_with_content
        ]

        todos_for_prompt = TodoCollection(self.todos).get_for_prompt()
        prompt_todos = [PromptTodo(**todo) for todo in todos_for_prompt]

        conversation_history = PromptConversationHistory.build(
            self.turns, settings.tool_response_expiration
        )

        current_task_turn_data = self.turns[-1].model_dump()
        current_task = PromptCurrentTask(**current_task_turn_data)

        # 4. Assemble the final Prompt object
        prompt_data = {
            "current_datetime": get_current_timestamp(
                zoneinfo.ZoneInfo(settings.timezone)
            ),
            "description": (
                "This structured prompt guides your response. First, understand the "
                "core instructions: `main_instruction` defines your thinking "
                "process. Next, identify the immediate objective from `current_task` "
                "and `todos`. Then, gather all context required to execute the task "
                "by processing `session_goal`, `roles`, `constraints`, "
                "`conversation_history`, and `file_references` in that order. "
                "Finally, execute the `current_task` by synthesizing all gathered "
                "information."
            ),
            "session_goal": PromptSessionGoal.build(
                purpose=self.purpose, background=self.background
            ),
            "roles": roles,
            "constraints": constraints,
            "main_instruction": (
                "Your main instruction is to be helpful and follow all previous "
                "instructions."
            ),
            "conversation_history": conversation_history,
            "current_task": current_task,
            "todos": prompt_todos if prompt_todos else None,
            "file_references": prompt_references if prompt_references else None,
            "reasoning_process": {
                "description": "Think step-by-step to achieve the goal."
            }
            if self.multi_step_reasoning_enabled
            else None,
        }

        return Prompt(**prompt_data)

    @classmethod
    def prepare(
        cls,
        args: "TaktArgs",
        is_dry_run: bool = False,
    ) -> "Session":
        """
        Finds an existing session based on args or creates a new one,
        then applies initial turns and references from args.
        """
        from pipe.core.models.turn import UserTaskTurn

        session_id = args.session.strip().rstrip(".") if args.session else None

        if session_id:
            session = cls.find(session_id)
            if not session:
                raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

            if not is_dry_run and args.instruction:
                new_turn = UserTaskTurn(
                    type="user_task",
                    instruction=args.instruction,
                    timestamp=get_current_timestamp(cls.timezone_obj),
                )
                session.turns.append(new_turn)
            print(f"Continuing session: {session.session_id}", file=sys.stderr)
        else:
            if not all([args.purpose, args.background]):
                raise ValueError(
                    "A new session requires --purpose and --background for the first "
                    "instruction."
                )

            session = cls.create(
                purpose=args.purpose,
                background=args.background,
                roles=args.roles or [],
                multi_step_reasoning_enabled=args.multi_step_reasoning,
                parent_id=args.parent,
            )

            if not is_dry_run and args.instruction:
                first_turn = UserTaskTurn(
                    type="user_task",
                    instruction=args.instruction,
                    timestamp=get_current_timestamp(cls.timezone_obj),
                )
                session.turns.append(first_turn)
            print(f"New session created: {session.session_id}", file=sys.stderr)

        if args.references:
            for ref_path in args.references:
                if ref_path.strip():
                    session.references.add(ref_path.strip())

        session.save()
        return session
