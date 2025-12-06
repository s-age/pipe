"""Turn-related API routes."""

from flask import Blueprint, Response, jsonify, request
from pipe.web.dispatcher import dispatch_action

turn_bp = Blueprint("turn", __name__, url_prefix="/api/v1/session/<path:session_id>")


@turn_bp.route("/turn/<int:turn_index>", methods=["DELETE"])
def delete_turn(session_id, turn_index):
    """Delete a turn from a session."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/turn/{turn_index}",
        params={"session_id": session_id, "turn_index": turn_index},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@turn_bp.route("/turn/<int:turn_index>", methods=["PATCH"])
def edit_turn(session_id, turn_index):
    """Edit a turn in a session."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/turn/{turn_index}",
        params={"session_id": session_id, "turn_index": turn_index},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@turn_bp.route("/fork/<int:fork_index>", methods=["POST"])
def fork_session(session_id, fork_index):
    """Fork a session at a specific index."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/fork/{fork_index}",
        params={"session_id": session_id, "fork_index": fork_index},
        request_data=request,
    )
    return jsonify(response_data), status_code
