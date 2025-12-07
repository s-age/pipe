from typing import Literal

from pydantic import BaseModel


class TurnResponse(BaseModel):
    status: str
    message: str


class UserTaskTurnUpdate(BaseModel):
    """Update DTO for UserTaskTurn. All fields optional for partial updates."""

    instruction: str | None = None
    timestamp: str | None = None


class ModelResponseTurnUpdate(BaseModel):
    """Update DTO for ModelResponseTurn. All fields optional for partial updates."""

    content: str | None = None
    timestamp: str | None = None


class UserTaskTurn(BaseModel):
    type: Literal["user_task"]
    instruction: str
    timestamp: str


class ModelResponseTurn(BaseModel):
    type: Literal["model_response"]
    content: str
    timestamp: str


class FunctionCallingTurn(BaseModel):
    type: Literal["function_calling"]
    response: str
    timestamp: str


class ToolResponseTurn(BaseModel):
    type: Literal["tool_response"]
    name: str
    response: TurnResponse
    timestamp: str


class CompressedHistoryTurn(BaseModel):
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
