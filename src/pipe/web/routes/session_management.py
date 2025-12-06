"""Session management-related API routes.

Handles all /api/v1/session_management/* endpoints.
"""

from flask import Blueprint, jsonify, request
from pipe.web.dispatcher import dispatch_action

session_management_bp = Blueprint("session_management", __name__, url_prefix="/api/v1")


@session_management_bp.route(
    "/session_management/archives", methods=["GET", "POST", "DELETE"]
)
def session_management_archives():
    """List, create, or delete session archives."""
    response_data, status_code = dispatch_action(
        action="session_management/archives", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@session_management_bp.route("/session_management/sessions", methods=["DELETE"])
def delete_sessions():
    """Delete multiple sessions."""
    response_data, status_code = dispatch_action(
        action="session_management/sessions", params={}, request_data=request
    )
    return jsonify(response_data), status_code
