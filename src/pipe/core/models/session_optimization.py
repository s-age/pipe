"""
Models for session optimization (compression, therapist, doctor).
"""

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class TurnEdit(CamelCaseModel):
    turn: int
    new_content: str


class TurnCompression(CamelCaseModel):
    start: int
    end: int
    reason: str = ""


class SessionModifications(CamelCaseModel):
    deletions: list[int]
    edits: list[TurnEdit]
    compressions: list[TurnCompression]


class DoctorResult(CamelCaseModel):
    status: str
    reason: str
    applied_deletions: list[int]
    applied_edits: list[TurnEdit]
    applied_compressions: list[TurnCompression]


class DiagnosisData(CamelCaseModel):
    summary: str = ""
    deletions: list[int] = Field(default_factory=list)
    edits: list[TurnEdit] = Field(default_factory=list)
    compressions: list[TurnCompression] = Field(default_factory=list)
    raw_diagnosis: str = ""
