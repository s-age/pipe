"""Approve compressor action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.compress_requests import ApproveCompressorRequest


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
        from pipe.web.service_container import get_session_optimization_service

        req = self.validated_request

        get_session_optimization_service().approve_compression(req.session_id)

        return {"message": "Compression approved"}
