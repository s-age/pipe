"""Create compressor session action."""

from pipe.core.services.session_optimization_service import CompressorResult
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.compress_requests import CreateCompressorRequest


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
        from pipe.web.service_container import get_session_optimization_service

        req = self.validated_request

        # All validation already done by Dispatcher:
        # - session_id exists
        # - start_turn and end_turn are valid
        # - turn range is correct
        # - target_length is positive
        return get_session_optimization_service().run_compression(
            req.session_id,
            req.policy,
            req.target_length,
            req.start_turn,
            req.end_turn,
        )
