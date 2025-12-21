"""Pydantic models for verification service results."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VerificationResult(BaseModel):
    """Result of summary verification process."""

    verification_status: Literal["pending_approval", "rejected"] = Field(
        description="Verification status"
    )
    verifier_session_id: str = Field(description="ID of the verifier session")
    message: str | None = Field(default=None, description="Status message")
    verifier_response: str = Field(description="Response from verifier agent")

    next_action: str = Field(description="Instructions for next action")

    model_config = ConfigDict(frozen=True)


class VerificationError(BaseModel):
    """Error result when verification fails."""

    error: str = Field(description="Error message describing what went wrong")

    model_config = ConfigDict(frozen=True)


# Union type for verification results
VerificationOutput = VerificationResult | VerificationError
