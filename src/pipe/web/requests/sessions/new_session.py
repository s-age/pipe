"""
Pydantic model for validating the request body of the new session API endpoint.
"""
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from pipe.web.validators.rules.file_exists import validate_comma_separated_files, validate_space_separated_files

class NewSessionRequest(BaseModel):
    purpose: str
    background: str
    instruction: str
    roles: Optional[str] = ""
    parent: Optional[str] = None
    references: Optional[str] = ""
    multi_step_reasoning_enabled: bool = False
    hyperparameters: Optional[Dict[str, Any]] = None

    @field_validator('purpose', 'background', 'instruction')
    @classmethod
    def check_not_empty(cls, v: str, field) -> str:
        if not v or not v.strip():
            raise ValueError(f"{field.field_name} must not be empty.")
        return v

    @field_validator('roles')
    @classmethod
    def validate_roles_exist(cls, v: str) -> str:
        validate_comma_separated_files(v)
        return v

    @field_validator('references')
    @classmethod
    def validate_references_exist(cls, v: str) -> str:
        validate_space_separated_files(v)
        return v
