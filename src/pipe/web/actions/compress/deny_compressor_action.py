"""Deny compressor action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.compress_requests import DenyCompressorRequest


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
        from pipe.web.service_container import get_session_optimization_service

        req = self.validated_request

        get_session_optimization_service().deny_compression(req.session_id)

        return None
