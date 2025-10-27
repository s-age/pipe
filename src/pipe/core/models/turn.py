from typing import Any, Literal

from pydantic import BaseModel


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
    response: dict[str, Any]
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
