from pipe.core.services.session_optimization_service import CompressorResult
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.compress_requests import (
    ApproveCompressorRequest,
    CreateCompressorRequest,
    DenyCompressorRequest,
)
from pipe.web.service_container import get_session_service


class CreateCompressorSessionAction(BaseAction):
    """
    Action to create a compressor session.

    Uses the new pattern:
    - Validation happens BEFORE this action (in Dispatcher)
    - Returns result directly (no ApiResponse)
    - Raises exceptions for errors (Dispatcher handles them)

    This action:
    1. Receives pre-validated request
    2. Calls compression service
    3. Returns result directly
    """

    request_model = CreateCompressorRequest

    def execute(self) -> CompressorResult:
        """
        Execute compression with pre-validated request.

        Returns:
            CompressorResult directly (Dispatcher wraps in ApiResponse)

        Raises:
            Exception: Any unexpected errors (Dispatcher converts to 500)
        """
        req = self.validated_request

        # All validation already done by Dispatcher:
        # - session_id exists
        # - start_turn and end_turn are valid
        # - turn range is correct
        # - target_length is positive
        return get_session_service().run_takt_for_compression(
            req.session_id,
            req.policy,
            req.target_length,
            req.start_turn,
            req.end_turn,
        )


class ApproveCompressorAction(BaseAction):
    """
    Action to approve a compression session.

    Uses the new pattern:
    - session_id validated BEFORE reaching this action
    - Returns None (204 No Content)
    - Raises exceptions for errors
    """

    request_model = ApproveCompressorRequest

    def execute(self) -> dict[str, str]:
        """
        Approve compression for session.

        Returns:
            Success message dict

        Raises:
            Exception: Any unexpected errors
        """
        req = self.validated_request

        get_session_service().approve_compression(req.session_id)

        return {"message": "Compression approved"}


class DenyCompressorAction(BaseAction):
    """
    Action to deny a compression session.

    Uses the new pattern:
    - session_id validated BEFORE reaching this action
    - Returns None (for 204 No Content)
    - Raises exceptions for errors
    """

    request_model = DenyCompressorRequest

    def execute(self) -> None:
        """
        Deny compression for session.

        Returns:
            None (Dispatcher will return 204)

        Raises:
            Exception: Any unexpected errors
        """
        req = self.validated_request

        get_session_service().deny_compression(req.session_id)

        return None
