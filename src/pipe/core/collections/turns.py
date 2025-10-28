import typing
from collections import UserList
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from pipe.core.models.turn import (
    CompressedHistoryTurn,
    FunctionCallingTurn,
    ModelResponseTurn,
    ToolResponseTurn,
    Turn,
    UserTaskTurn,
)
from pydantic_core import core_schema

if TYPE_CHECKING:
    pass


class TurnCollection(UserList):
    """
    A collection of Turn objects with custom filtering logic for prompt generation.
    """

    def __init__(self, data: list | None = None):
        initialized_data = data if data is not None else []
        super().__init__(initialized_data)

    def get_for_prompt(self, tool_response_limit: int = 3) -> Iterator[Turn]:
        """
        Yields turns for prompt generation, applying filtering rules.
        - The last turn (current task) is excluded.
        - Only the last N 'tool_response' turns from the history are included.
        """
        tool_response_count = 0
        history = self.data[:-1]  # Exclude the last turn

        # Iterate in reverse to easily count the last N tool_responses
        for turn in reversed(history):
            if isinstance(turn, ToolResponseTurn):
                tool_response_count += 1
                if tool_response_count > tool_response_limit:
                    continue
            yield turn

        # The turns are yielded in reverse order, so the caller should reverse
        # them back.
        # Example: reversed_turns = list(turn_collection.get_for_prompt())
        #          prompt_turns = list(reversed(reversed_turns))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Callable[[Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        # Define the schema for the items in the list, which is a discriminated union.

        # Explicitly list all subtypes of Turn to avoid import-order issues with
        # typing.get_args(Turn)
        turn_subtypes = [
            UserTaskTurn,
            ModelResponseTurn,
            FunctionCallingTurn,
            ToolResponseTurn,
            CompressedHistoryTurn,
        ]

        choices = {
            typing.get_args(t.__annotations__["type"])[0]: handler(t)
            for t in turn_subtypes
        }

        turn_schema = core_schema.tagged_union_schema(
            choices=choices,
            discriminator="type",
        )
        items_schema = core_schema.list_schema(turn_schema)

        # This defines a schema that validates a list of the items defined above,
        # and then converts that list into an instance of our class.
        list_to_collection_schema = core_schema.chain_schema(
            [
                items_schema,
                core_schema.no_info_plain_validator_function(cls),
            ]
        )

        return core_schema.json_or_python_schema(
            # When parsing from JSON, we expect a list that needs to be converted.
            json_schema=list_to_collection_schema,
            # When creating from Python, it could be an instance of our class already,
            # or it could be a list that needs to be converted.
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    list_to_collection_schema,
                ]
            ),
            # This defines how to serialize our class back to a JSON-compatible
            # type (a list).
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: [t.model_dump() for t in instance]
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        handler: Callable[[Any], dict[str, Any]],
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema.update(type="array", items={"$ref": "#/definitions/Turn"})
        return json_schema

    def expire_old_tool_responses(self, expiration_threshold: int = 3) -> bool:
        """
        Expires the message content of old tool_response turns to save tokens,
        while preserving the 'succeeded' status. This uses a safe rebuild pattern.
        Returns True if any turns were modified.
        """
        if not self.data:
            return False

        user_tasks = [turn for turn in self.data if turn.type == "user_task"]
        if len(user_tasks) <= expiration_threshold:
            return False

        expiration_threshold_timestamp = user_tasks[-expiration_threshold].timestamp

        new_turns = []
        modified = False
        for turn in self.data:
            if (
                turn.type == "tool_response"
                and turn.timestamp < expiration_threshold_timestamp
                and isinstance(turn.response, dict)
                and turn.response.get("status") == "succeeded"
            ):
                modified_turn = turn.model_copy(deep=True)
                modified_turn.response["message"] = (
                    "This tool response has expired to save tokens."
                )
                new_turns.append(modified_turn)
                modified = True
            else:
                new_turns.append(turn)

        if modified:
            self.data = new_turns

        return modified
