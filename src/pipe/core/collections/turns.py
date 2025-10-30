from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from pipe.core.models.turn import ToolResponseTurn, Turn
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class TurnCollection(list[Turn]):
    """
    A collection of Turn objects, providing utility methods for turn management.
    """

    if TYPE_CHECKING:
        from pipe.core.collections.turns import TurnCollection

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type["TurnCollection"],
        source: type[Any],
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

    def get_turns_for_prompt(self, tool_response_limit: int = 3) -> Iterator[Turn]:
        """
        Yields turns for prompt generation, applying filtering rules.
        - The last turn (current task) is excluded.
        - Only the last N 'tool_response' turns from the history are included.
        """
        tool_response_count = 0
        history = self[:-1]  # Exclude the last turn

        # Iterate in reverse to easily count the last N tool_responses
        for turn in reversed(history):
            if isinstance(turn, ToolResponseTurn):
                tool_response_count += 1
                if tool_response_count > tool_response_limit:
                    continue
            yield turn
