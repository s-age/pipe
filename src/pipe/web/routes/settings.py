"""Settings-related API routes.

Handles all /api/v1/settings/* endpoints.
"""

from flask import Blueprint, jsonify, request

from pipe.web.dispatcher import dispatch_action

settings_bp = Blueprint("settings", __name__, url_prefix="/api/v1")


@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    """Get application settings."""
    response_data, status_code = dispatch_action(
        action="settings", params={}, request_data=request
    )
    return jsonify(response_data), status_code
