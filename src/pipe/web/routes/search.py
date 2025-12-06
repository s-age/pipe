"""Search-related API routes.

Handles search and file indexing endpoints.
"""

from flask import Blueprint, jsonify, request
from pipe.web.dispatcher import dispatch_action

search_bp = Blueprint("search", __name__, url_prefix="/api/v1")


@search_bp.route("/search", methods=["POST"])
def search_sessions():
    """Search sessions."""
    response_data, status_code = dispatch_action(
        action="search", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@search_bp.route("/search_l2", methods=["POST"])
def search_l2():
    """L2 file search."""
    response_data, status_code = dispatch_action(
        action="search_l2", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@search_bp.route("/ls", methods=["POST"])
def ls():
    """List directory contents."""
    response_data, status_code = dispatch_action(
        action="ls", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@search_bp.route("/index_files", methods=["POST"])
def index_files():
    """Index files for search."""
    response_data, status_code = dispatch_action(
        action="index_files", params={}, request_data=request
    )
    return jsonify(response_data), status_code
