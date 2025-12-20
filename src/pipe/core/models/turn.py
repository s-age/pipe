from typing import Literal

from pipe.core.models.base import CamelCaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class TurnResponse(CamelCaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )  # Allow extra fields for flexibility
    status: str
    message: str


class UserTaskTurnUpdate(CamelCaseModel):
    """
    Update DTO for UserTaskTurn.

    Used at service layer (I/O boundary) for partial updates.
    All fields are optional to support partial updates.
    Extra fields are rejected to prevent invalid data.
    """

    model_config = ConfigDict(extra="forbid")

    instruction: str | None = None
    timestamp: str | None = None


class ModelResponseTurnUpdate(CamelCaseModel):
    """
    Update DTO for ModelResponseTurn.

    Used at service layer (I/O boundary) for partial updates.
    All fields are optional to support partial updates.
    Extra fields are rejected to prevent invalid data.
    """

    model_config = ConfigDict(extra="forbid")

    content: str | None = None
    thought: str | None = None
    timestamp: str | None = None
    raw_response: str | None = None


class UserTaskTurn(CamelCaseModel):
    type: Literal["user_task"]
    instruction: str
    timestamp: str


class ModelResponseTurn(CamelCaseModel):
    type: Literal["model_response"]
    content: str
    thought: str | None = None
    timestamp: str
    raw_response: str | None = None


class FunctionCallingTurn(CamelCaseModel):
    type: Literal["function_calling"]
    response: str
    timestamp: str
    raw_response: str | None = None


class ToolResponseTurn(CamelCaseModel):
    type: Literal["tool_response"]
    name: str
    response: TurnResponse
    timestamp: str


class CompressedHistoryTurn(CamelCaseModel):
    type: Literal["compressed_history"]
    content: str
    original_turns_range: list[int]
    timestamp: str


Turn = (
    UserTaskTurn
    | ModelResponseTurn
    | FunctionCallingTurn
    | ToolResponseTurn
    | CompressedHistoryTurn
)
