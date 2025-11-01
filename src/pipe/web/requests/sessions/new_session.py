"""
Pydantic model for validating the request body of the new session API endpoint.
"""

import os
from typing import Any

from pipe.web.validators.rules.file_exists import (
    validate_comma_separated_files,
)
from pydantic import BaseModel, field_validator


class NewSessionRequest(BaseModel):
    purpose: str
    background: str
    instruction: str
    roles: str | None = ""
    parent: str | None = None
    references: str | None = ""
    artifacts: str | None = ""
    procedure: str | None = None
    multi_step_reasoning_enabled: bool = False
    hyperparameters: dict[str, Any] | None = None

    @field_validator("purpose", "background", "instruction")
    @classmethod
    def check_not_empty(cls, v: str, field) -> str:
        if not v or not v.strip():
            raise ValueError(f"{field.field_name} must not be empty.")
        return v

    @field_validator("roles")
    @classmethod
    def validate_roles_exist(cls, v: str) -> str:
        validate_comma_separated_files(v)
        return v

    @field_validator("references")
    @classmethod
    def validate_references_exist(cls, v: str) -> str:
        validate_comma_separated_files(v)
        return v

    @field_validator("artifacts")
    @classmethod
    def validate_artifacts_exist(cls, v: str) -> str:
        validate_comma_separated_files(v)
        return v

    @field_validator("procedure")
    @classmethod
    def validate_procedure_exists(cls, v: str) -> str:
        if v and not os.path.isfile(v):
            raise ValueError(f"File not found: '{v}'")
        return v
