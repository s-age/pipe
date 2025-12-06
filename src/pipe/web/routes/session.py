"""Session-related API routes.

Handles all /api/v1/session/* endpoints.
"""

from flask import Blueprint, Response, jsonify, request
from pipe.web.dispatcher import dispatch_action

session_bp = Blueprint("session", __name__, url_prefix="/api/v1")


@session_bp.route("/session/start", methods=["POST"])
def create_new_session():
    """Create a new session."""
    response_data, status_code = dispatch_action(
        action="session/start", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>", methods=["GET", "DELETE"])
def session_api(session_id):
    """Get or delete a session."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}",
        params={"session_id": session_id},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>/instruction", methods=["POST"])
def send_instruction(session_id):
    """Send an instruction to a session."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/instruction",
        params={"session_id": session_id},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>/turns", methods=["GET"])
def get_session_turns(session_id):
    """Get turns for a session."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/turns",
        params={"session_id": session_id, "since": request.args.get("since", 0)},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/compress", methods=["POST"])
def create_compressor_session():
    """Create a compressor session."""
    response_data, status_code = dispatch_action(
        action="compress", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@session_bp.route("/therapist", methods=["POST"])
def create_therapist_session():
    """Create a therapist session."""
    response_data, status_code = dispatch_action(
        action="therapist", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@session_bp.route("/doctor", methods=["POST"])
def apply_doctor_modifications():
    """Apply doctor modifications."""
    response_data, status_code = dispatch_action(
        action="doctor", params={}, request_data=request
    )
    return jsonify(response_data), status_code
