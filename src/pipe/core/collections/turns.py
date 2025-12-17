from collections.abc import Iterator
from typing import TYPE_CHECKING

from pipe.core.models.turn import (
    ModelResponseTurnUpdate,
    Turn,
    UserTaskTurnUpdate,
)
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class TurnCollection(list[Turn]):
    """
    A collection of Turn objects, providing utility methods for turn management.

    This collection encapsulates turn management operations, following the
    "Tell, Don't Ask" principle by validating and performing operations
    internally rather than exposing raw data manipulation.
    """

    if TYPE_CHECKING:
        from pipe.core.collections.turns import TurnCollection

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type["TurnCollection"],
        source: type["TurnCollection"],
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """
        Instructs Pydantic how to validate and serialize TurnCollection.
        Allows initialization from a list of Turn objects or dictionaries that can be
        coerced into Turn objects.
        """
        # Get the schema for a single Turn using the handler

        return core_schema.no_info_after_validator_function(
            cls._validate_from_list,
            handler.generate_schema(list[Turn]),
        )

    @classmethod
    def _validate_from_list(cls, value: list[Turn]) -> "TurnCollection":
        """
        Custom validation logic to create a TurnCollection from a list of Turn objects.
        """
        return cls(value)

    def add(self, turn: Turn):
        """Adds a turn to this collection.

        Args:
            turn: The turn to add
        """
        self.append(turn)

    def edit_by_index(
        self,
        turn_index: int,
        new_data: UserTaskTurnUpdate | ModelResponseTurnUpdate,
    ):
        """Edits a specific turn in this collection.

        Args:
            turn_index: Index of the turn to edit
            new_data: Update data - accepts typed DTOs (UserTaskTurnUpdate
                or ModelResponseTurnUpdate)

        Raises:
            IndexError: If turn_index is out of range
            ValueError: If the turn type cannot be edited
        """
        from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn

        if not (0 <= turn_index < len(self)):
            raise IndexError("Turn index out of range.")

        original_turn = self[turn_index]
        if original_turn.type not in ["user_task", "model_response"]:
            raise ValueError(
                f"Editing turns of type '{original_turn.type}' is not allowed."
            )

        turn_as_dict = original_turn.model_dump()

        # Convert DTO to dict, excluding unset fields for partial updates
        if isinstance(new_data, UserTaskTurnUpdate | ModelResponseTurnUpdate):
            update_dict = new_data.model_dump(exclude_unset=True)
        else:
            # Should not reach here due to type hints, but handle gracefully
            update_dict = new_data if isinstance(new_data, dict) else {}
        turn_as_dict.update(update_dict)

        if original_turn.type == "user_task":
            self[turn_index] = UserTaskTurn(**turn_as_dict)
        elif original_turn.type == "model_response":
            self[turn_index] = ModelResponseTurn(**turn_as_dict)

    def delete_by_index(self, turn_index: int):
        """Deletes a specific turn from this collection.

        Args:
            turn_index: Index of the turn to delete

        Raises:
            IndexError: If turn_index is out of range
        """
        if not (0 <= turn_index < len(self)):
            raise IndexError("Turn index out of range.")
        del self[turn_index]

    def merge_from(self, other: "TurnCollection"):
        """Merges turns from another collection into this one.

        Args:
            other: The collection to merge from
        """
        self.extend(other)

    def get_turns_for_prompt(self, tool_response_limit: int = 3) -> Iterator[Turn]:
        """Get turns for prompt generation, delegating to domain function.

        This is a backward-compatibility wrapper. Consider using
        domains.turns.get_turns_for_prompt() instead.

        Args:
            tool_response_limit: Maximum number of tool_response turns to include

        Yields:
            Turn objects suitable for prompt generation
        """
        from pipe.core.domains.turns import (
            get_turns_for_prompt as domain_get_turns_for_prompt,
        )

        return domain_get_turns_for_prompt(self, tool_response_limit)
