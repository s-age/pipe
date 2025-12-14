"""Session tree API routes.

Handles /api/v1/session_tree endpoint.
"""

from flask import Blueprint, jsonify, request
from pipe.web.actions.session_tree import SessionTreeAction
from pipe.web.dispatcher import dispatch_action

session_tree_bp = Blueprint("session_tree", __name__, url_prefix="/api/v1")


@session_tree_bp.route("/session_tree", methods=["GET"])
def get_session_tree():
    """Get session tree data."""
    try:
        response_data, status_code = dispatch_action(
            action=SessionTreeAction, params={}, request_data=request
        )
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500
