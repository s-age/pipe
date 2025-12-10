from typing import ClassVar

from pipe.web.requests.base_request import BaseRequest
from pydantic import field_validator


class CreateCompressorRequest(BaseRequest):
    """
    Unified request model for creating a compressor session.

    Validates all compression parameters including session existence,
    turn ranges, and policy settings. Validation happens BEFORE
    action execution (Laravel/Struts style).

    Body Fields:
        session_id: Session ID to compress
        policy: Compression policy to use
        target_length: Target length for compression
        start_turn: Starting turn number (1-based)
        end_turn: Ending turn number (1-based)

    Examples:
        # Created automatically by dispatcher
        request = CreateCompressorRequest.create_with_path_params(
            path_params={},
            body_data={
                "session_id": "abc-123",
                "policy": "standard",
                "target_length": 1000,
                "start_turn": 1,
                "end_turn": 10,
            },
        )

        # Type-safe access in action
        result = service.compress(
            request.session_id,
            request.policy,
            request.target_length,
            request.start_turn,
            request.end_turn,
        )
    """

    # No path params for this endpoint - all data in body
    path_params: ClassVar[list[str]] = []

    # Body fields
    session_id: str
    policy: str
    target_length: int
    start_turn: int
    end_turn: int

    @field_validator("start_turn", "end_turn")
    @classmethod
    def validate_turns_positive(cls, v):
        """Validate turn numbers are positive (1-based)."""
        if v < 1:
            raise ValueError("Turn number must be >= 1")
        return v

    @field_validator("end_turn")
    @classmethod
    def validate_turn_range(cls, v, info):
        """Validate end_turn is not before start_turn."""
        start_turn = info.data.get("start_turn")
        if start_turn is not None and v < start_turn:
            raise ValueError("end_turn must be greater than or equal to start_turn")
        return v

    @field_validator("session_id")
    @classmethod
    def validate_session_exists(cls, v, info):
        """Validate that session exists and is accessible."""
        from pipe.web.service_container import get_session_service

        session = get_session_service().get_session(v)
        if not session:
            raise ValueError(f"Session '{v}' not found")

        # Store session in data for later validators to access
        # Note: We can't use context in field validators, so we'll re-fetch if needed
        return v

    @field_validator("start_turn", "end_turn")
    @classmethod
    def validate_turn_exists(cls, v, info):
        """Validate that turn exists in session."""
        from pipe.web.service_container import get_session_service

        session_id = info.data.get("session_id")
        if not session_id:
            # session_id validation will catch this
            return v

        session = get_session_service().get_session(session_id)
        if session:
            # v is 1-based; valid range is 1..len(session.turns)
            if v > len(session.turns):
                raise ValueError(
                    f"Turn {v} does not exist in session "
                    f"(max: {len(session.turns)})"
                )

        return v

    @field_validator("target_length")
    @classmethod
    def validate_target_length_positive(cls, v):
        """Validate target length is positive."""
        if v <= 0:
            raise ValueError("target_length must be positive")
        return v


class ApproveCompressorRequest(BaseRequest):
    """
    Unified request model for approving a compressor session.

    Simple request with only path parameter validation.
    Validates that the session exists before reaching action.

    Path Parameters:
        session_id: Session ID to approve (from URL)

    Examples:
        # Created automatically by dispatcher
        request = ApproveCompressorRequest.create_with_path_params(
            path_params={"session_id": "abc-123"},
            body_data=None,
        )
    """

    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter
    session_id: str

    @field_validator("session_id")
    @classmethod
    def validate_session_exists(cls, v):
        """Validate that session exists."""
        from pipe.web.service_container import get_session_service

        session = get_session_service().get_session(v)
        if not session:
            raise ValueError(f"Session '{v}' not found")
        return v


class DenyCompressorRequest(BaseRequest):
    """
    Unified request model for denying a compressor session.

    Simple request with only path parameter validation.
    Validates that the session exists before reaching action.

    Path Parameters:
        session_id: Session ID to deny (from URL)

    Examples:
        # Created automatically by dispatcher
        request = DenyCompressorRequest.create_with_path_params(
            path_params={"session_id": "abc-123"},
            body_data=None,
        )
    """

    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter
    session_id: str

    @field_validator("session_id")
    @classmethod
    def validate_session_exists(cls, v):
        """Validate that session exists."""
        from pipe.web.service_container import get_session_service

        session = get_session_service().get_session(v)
        if not session:
            raise ValueError(f"Session '{v}' not found")
        return v
