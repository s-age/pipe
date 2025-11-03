"""
Pydantic model for validating the request body of the new session API endpoint.
"""

import os
from typing import Any

from pipe.core.models.reference import Reference
from pipe.web.validators.rules.file_exists import validate_list_of_files_exist
from pydantic import BaseModel, field_validator


class StartSessionRequest(BaseModel):
    purpose: str
    background: str
    instruction: str
    roles: list[str] | None = None
    parent: str | None = None
    references: list[Reference] | None = None
    artifacts: list[str] | None = None
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
    def validate_list_of_strings_exist(cls, v: list[str]) -> list[str]:
        validate_list_of_files_exist(v)
        return v

    @field_validator("references")
    @classmethod
    def validate_list_of_references_exist(cls, v: list[Reference]) -> list[Reference]:
        validate_list_of_files_exist([ref.path for ref in v])
        return v

    @field_validator("procedure")
    @classmethod
    def validate_procedure_exists(cls, v: str) -> str:
        if v and not os.path.isfile(v):
            raise ValueError(f"File not found: '{v}'")
        return v
