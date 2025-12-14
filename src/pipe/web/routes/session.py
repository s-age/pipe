"""Session-related API routes.

Handles all /api/v1/session/* endpoints.
"""

from flask import Blueprint, Response, jsonify, request
from pipe.web.actions import (
    ApproveCompressorAction,
    CreateCompressorSessionAction,
    CreateTherapistSessionAction,
    DenyCompressorAction,
    SessionDeleteAction,
    SessionGetAction,
    SessionInstructionAction,
    SessionStartAction,
    SessionTurnsGetAction,
)
from pipe.web.actions.therapist import ApplyDoctorModificationsAction
from pipe.web.dispatcher import dispatch_action
from pipe.web.request_context import RequestContext
from pipe.web.streaming_dispatcher import dispatch_streaming_action

session_bp = Blueprint("session", __name__, url_prefix="/api/v1")


@session_bp.route("/session/start", methods=["POST"])
def create_new_session():
    """Create a new session."""
    response_data, status_code = dispatch_action(
        action=SessionStartAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>", methods=["GET", "DELETE"])
def session_api(session_id):
    """Get or delete a session."""
    action_class = (
        SessionDeleteAction if request.method == "DELETE" else SessionGetAction
    )

    response_data, status_code = dispatch_action(
        action=action_class,
        params={"session_id": session_id},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>/instruction", methods=["POST"])
def send_instruction(session_id):
    """Send an instruction to a session - returns streaming response."""
    try:
        request_context = RequestContext(
            path_params={"session_id": session_id}, request_data=request
        )

        response = dispatch_streaming_action(
            action_class=SessionInstructionAction,
            params={"session_id": session_id},
            request_data=request_context,
        )

        return response
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error("Error in send_instruction", exc_info=True)

        from pipe.web.exceptions import HttpException
        from pipe.web.responses import ApiResponse

        if isinstance(e, HttpException):
            return (
                jsonify(ApiResponse(success=False, message=e.message).model_dump()),
                e.status_code,
            )
        return (
            jsonify(ApiResponse(success=False, message=str(e)).model_dump()),
            500,
        )


@session_bp.route("/session/<path:session_id>/turns", methods=["GET"])
def get_session_turns(session_id):
    """Get turns for a session."""
    response_data, status_code = dispatch_action(
        action=SessionTurnsGetAction,
        params={"session_id": session_id, "since": request.args.get("since", 0)},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/compress", methods=["POST"])
def create_compressor_session():
    """Create a compressor session."""
    response_data, status_code = dispatch_action(
        action=CreateCompressorSessionAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code


@session_bp.route("/compress/<path:session_id>/approve", methods=["POST"])
def approve_compressor_session(session_id):
    """Approve compressor session."""
    response_data, status_code = dispatch_action(
        action=ApproveCompressorAction,
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/compress/<path:session_id>/deny", methods=["POST"])
def deny_compressor_session(session_id):
    """Deny compressor session."""
    response_data, status_code = dispatch_action(
        action=DenyCompressorAction,
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/therapist", methods=["POST"])
def create_therapist_session():
    """Create a therapist session."""
    response_data, status_code = dispatch_action(
        action=CreateTherapistSessionAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code


@session_bp.route("/doctor", methods=["POST"])
def apply_doctor_modifications():
    """Apply doctor modifications."""
    response_data, status_code = dispatch_action(
        action=ApplyDoctorModificationsAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code
