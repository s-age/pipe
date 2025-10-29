from __future__ import annotations

import sys
import zoneinfo
from collections.abc import Iterator

from pipe.core.models.session import Session
from pipe.core.models.turn import Turn
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.file import locked_json_read, locked_json_write


class SessionCollection:
    """
    Manages the collection of session metadata, corresponding to the
    `sessions/index.json` file.
    This class is responsible for loading, saving, and managing the session index.
    It provides methods for finding, adding, and deleting session entries from the
    index, but it does not handle the loading or saving of individual session
    files (e.g., `${session_id}.json`).
    """

    def __init__(
        self,
        index_path: str,
        timezone_name: str,
        purpose: str | None = None,
        created_at: str | None = None,
    ):
        self.index_path = index_path
        self.lock_path = f"{index_path}.lock"
        try:
            self.timezone_obj = zoneinfo.ZoneInfo(timezone_name)
        except zoneinfo.ZoneInfoNotFoundError:
            print(
                f"Warning: Timezone '{timezone_name}' not found. Using UTC.",
                file=sys.stderr,
            )
            self.timezone_obj = zoneinfo.ZoneInfo("UTC")
        self._index_data = locked_json_read(
            self.lock_path, self.index_path, default_data={"sessions": {}}
        )

    def save(self):
        """Saves the current session index to `index.json`."""
        locked_json_write(self.lock_path, self.index_path, self._index_data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._index_data.get("sessions", {}))

    def __len__(self) -> int:
        return len(self._index_data.get("sessions", {}))

    def find(self, session_id: str) -> dict | None:
        """Finds a session's metadata by its ID from the index."""
        return self._index_data.get("sessions", {}).get(session_id)

    def add(self, session: Session):
        """Adds a new session to the collection."""
        if "sessions" not in self._index_data:
            self._index_data["sessions"] = {}
        if session.session_id in self._index_data["sessions"]:
            raise ValueError(f"Session with ID '{session.session_id}' already exists.")

        self.update(session.session_id, session.purpose, session.created_at)

    def update(
        self, session_id: str, purpose: str | None = None, created_at: str | None = None
    ):
        """Updates an existing session's metadata in the index."""
        if "sessions" not in self._index_data:
            self._index_data["sessions"] = {}
        if session_id not in self._index_data["sessions"]:
            self._index_data["sessions"][session_id] = {}

        self._index_data["sessions"][session_id]["last_updated"] = (
            get_current_timestamp(self.timezone_obj)
        )
        if created_at:
            self._index_data["sessions"][session_id]["created_at"] = created_at
        if purpose:
            self._index_data["sessions"][session_id]["purpose"] = purpose

    def delete(self, session_id: str) -> bool:
        """Deletes a session from the collection. Returns True if successful."""
        if (
            "sessions" in self._index_data
            and session_id in self._index_data["sessions"]
        ):
            del self._index_data["sessions"][session_id]
            # Also delete children sessions
            children_to_delete = [
                sid
                for sid in self._index_data["sessions"]
                if sid.startswith(f"{session_id}/")
            ]
            for child_id in children_to_delete:
                del self._index_data["sessions"][child_id]
            return True
        return False

    def add_turn(self, session: Session, turn_data: Turn):
        session.turns.append(turn_data)
        session.save()
        self.update(session.session_id)
        self.save()

    def edit_turn(self, session: Session, turn_index: int, new_data: dict):
        from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn

        if not (0 <= turn_index < len(session.turns)):
            raise IndexError("Turn index out of range.")

        original_turn = session.turns[turn_index]
        if original_turn.type not in ["user_task", "model_response"]:
            raise ValueError(
                f"Editing turns of type '{original_turn.type}' is not allowed."
            )

        turn_as_dict = original_turn.model_dump()
        turn_as_dict.update(new_data)

        if original_turn.type == "user_task":
            session.turns[turn_index] = UserTaskTurn(**turn_as_dict)
        elif original_turn.type == "model_response":
            session.turns[turn_index] = ModelResponseTurn(**turn_as_dict)

        session.save()
        self.update(session.session_id)
        self.save()

    def delete_turn(self, session: Session, turn_index: int):
        if not (0 <= turn_index < len(session.turns)):
            raise IndexError("Turn index out of range.")

        del session.turns[turn_index]
        session.save()
        self.update(session.session_id)
        self.save()

    def merge_pool(self, session: Session):
        from pipe.core.collections.turns import TurnCollection

        if session.pools:
            session.turns.extend(session.pools)
            session.pools = TurnCollection()
            session.save()
            self.update(session.session_id)
            self.save()

    def fork(self, original_session: Session, fork_index: int) -> Session:
        import hashlib
        import json

        from pipe.core.collections.turns import TurnCollection

        if not (0 <= fork_index < len(original_session.turns)):
            raise IndexError("fork_index is out of range.")

        fork_turn = original_session.turns[fork_index]
        if fork_turn.type != "model_response":
            raise ValueError(
                "Forking is only allowed from a 'model_response' turn. "
                f"Turn {fork_index + 1} is of type '{fork_turn.type}'."
            )

        timestamp = get_current_timestamp(self.timezone_obj)
        forked_purpose = f"Fork of: {original_session.purpose}"
        forked_turns = TurnCollection(original_session.turns[: fork_index + 1])

        identity_str = json.dumps(
            {
                "purpose": forked_purpose,
                "original_id": original_session.session_id,
                "fork_at_turn": fork_index,
                "timestamp": timestamp,
            },
            sort_keys=True,
        )
        new_session_id_suffix = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

        parent_path = (
            original_session.session_id.rsplit("/", 1)[0]
            if "/" in original_session.session_id
            else None
        )
        new_session_id = (
            f"{parent_path}/{new_session_id_suffix}"
            if parent_path
            else new_session_id_suffix
        )

        new_session = Session(
            session_id=new_session_id,
            created_at=timestamp,
            purpose=forked_purpose,
            background=original_session.background,
            roles=original_session.roles,
            multi_step_reasoning_enabled=original_session.multi_step_reasoning_enabled,
            hyperparameters=original_session.hyperparameters
            or Session.default_hyperparameters,
            references=original_session.references,
            turns=forked_turns,
        )

        new_session.save()
        self.update(new_session.session_id, new_session.purpose, new_session.created_at)
        self.save()

        return new_session

    def get_sorted_by_last_updated(self) -> list[tuple[str, dict]]:
        """
        Returns a list of (session_id, session_meta) tuples,
        sorted by 'last_updated' in descending order.
        """
        if not self._index_data or "sessions" not in self._index_data:
            return []

        return sorted(
            self._index_data["sessions"].items(),
            key=lambda item: item[1].get("last_updated", ""),
            reverse=True,
        )
