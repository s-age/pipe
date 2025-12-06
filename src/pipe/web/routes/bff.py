"""BFF (Backend for Frontend) routes.

These endpoints aggregate multiple API calls to optimize frontend performance.
Handles all /api/v1/bff/* endpoints.
"""

from flask import Blueprint, jsonify, request

from pipe.web.service_container import get_session_detail_controller

bff_bp = Blueprint("bff", __name__, url_prefix="/api/v1/bff")


@bff_bp.route("/start_session", methods=["GET"])
def get_start_session():
    """
    BFF endpoint for start session page.
    Aggregates settings and session tree in a single request.
    """
    try:
        controller = get_session_detail_controller()
        response_data, status_code = controller.get_settings_with_tree(
            request_data=request
        )
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@bff_bp.route("/session_management", methods=["GET"])
def get_session_management():
    """
    BFF endpoint for session management page.
    Aggregates session tree and archives in a single request.
    """
    try:
        controller = get_session_detail_controller()
        response_data, status_code = controller.get_session_management_dashboard(
            request_data=request
        )
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@bff_bp.route("/chat_history", methods=["GET"])
def get_chat_history():
    """
    BFF endpoint for chat history page.
    Returns session tree, optionally current session details if session_id provided.
    """
    try:
        controller = get_session_detail_controller()
        session_id = request.args.get("session_id")
        response_data, status_code = controller.get_chat_history(session_id, request)
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500
