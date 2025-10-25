from typing import Dict, Any, Union
from pydantic import BaseModel
from typing_extensions import Literal

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
    response: Dict[str, Any]
    timestamp: str

Turn = Union[UserTaskTurn, ModelResponseTurn, FunctionCallingTurn, ToolResponseTurn]
