"""Domain logic for Session.

Separates business logic from data structures (models).
"""

import hashlib
import json
import zoneinfo
from typing import TYPE_CHECKING

from pipe.core.collections.turns import TurnCollection
from pipe.core.utils.datetime import get_current_timestamp

if TYPE_CHECKING:
    from pipe.core.models.session import Session


def fork_session(
    original: "Session", fork_index: int, timezone_obj: zoneinfo.ZoneInfo
) -> "Session":
    """Creates a new, in-memory Session object by forking an existing one.

    Args:
        original: The original session to fork from
        fork_index: Index of the turn to fork from (must be a model_response turn)
        timezone_obj: Timezone for timestamp generation

    Returns:
        New Session object forked from the original

    Raises:
        IndexError: If fork_index is out of range
        ValueError: If the turn at fork_index is not a model_response
    """
    from pipe.core.models.session import Session

    # Validate fork_index range
    if not (0 <= fork_index < len(original.turns)):
        raise IndexError(
            f"fork_index {fork_index} is out of range (0-{len(original.turns)-1})."
        )

    # Validate that fork point is a model_response turn
    fork_turn = original.turns[fork_index]
    if fork_turn.type != "model_response":
        raise ValueError(
            "Forking is only allowed from a 'model_response' turn. "
            f"Turn {fork_index + 1} is of type '{fork_turn.type}'."
        )

    timestamp = get_current_timestamp(timezone_obj)
    forked_purpose = f"Fork of: {original.purpose}"
    forked_turns = TurnCollection(original.turns[: fork_index + 1])

    identity_str = json.dumps(
        {
            "purpose": forked_purpose,
            "original_id": original.session_id,
            "fork_at_turn": fork_index,
            "timestamp": timestamp,
        },
        sort_keys=True,
    )
    new_session_id_suffix = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

    parent_path = (
        original.session_id.rsplit("/", 1)[0] if "/" in original.session_id else None
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
        background=original.background,
        roles=original.roles,
        multi_step_reasoning_enabled=original.multi_step_reasoning_enabled,
        hyperparameters=original.hyperparameters,
        references=original.references,
        artifacts=original.artifacts,
        procedure=original.procedure,
        turns=forked_turns,
    )


def destroy_session(session: "Session"):
    """
    Deletes the session's data files.

    Note: This function is deprecated. Use SessionRepository.delete() instead,
    which properly handles both session files and index updates.

    Args:
        session: The session to destroy (not used, kept for backward compatibility)
    """
    raise NotImplementedError(
        "destroy_session() is deprecated. "
        "Use SessionRepository.delete(session_id) instead."
    )
