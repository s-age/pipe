"""Pydantic model for validating the edit multi-step reasoning API request body."""

from pydantic import BaseModel


class EditMultiStepReasoningRequest(BaseModel):
    """Request body for toggling multi-step reasoning for a session.

    Fields:
        multi_step_reasoning_enabled: bool
    """

    multi_step_reasoning_enabled: bool
