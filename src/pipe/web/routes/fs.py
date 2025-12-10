"""File system and search-related API routes.

Handles search, file indexing, roles, and procedures endpoints.
"""

from flask import Blueprint, jsonify, request
from pipe.web.dispatcher import dispatch_action

fs_bp = Blueprint("fs", __name__, url_prefix="/api/v1/fs")


@fs_bp.route("/search", methods=["POST"])
def search_sessions():
    """Search sessions."""
    response_data, status_code = dispatch_action(
        action="fs/search", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/browse_l2", methods=["POST"])
def browse_l2():
    """L2 file search."""
    response_data, status_code = dispatch_action(
        action="fs/search_l2", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/browse", methods=["POST"])
def browse():
    """List directory contents."""
    response_data, status_code = dispatch_action(
        action="fs/ls", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/index_files", methods=["POST"])
def index_files():
    """Index files for search."""
    response_data, status_code = dispatch_action(
        action="fs/index_files", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/roles", methods=["GET"])
def get_roles():
    """Get available roles."""
    response_data, status_code = dispatch_action(
        action="fs/roles", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/procedures", methods=["GET"])
def get_procedures():
    """Get available procedures."""
    response_data, status_code = dispatch_action(
        action="fs/procedures", params={}, request_data=request
    )
    return jsonify(response_data), status_code
