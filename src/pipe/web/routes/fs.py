"""File system and search-related API routes.

Handles search, file indexing, roles, and procedures endpoints.
"""

from flask import Blueprint, jsonify, request
from pipe.web.actions import GetProceduresAction, GetRolesAction
from pipe.web.actions.fs import (
    IndexFilesAction,
    LsAction,
    SearchL2Action,
    SearchSessionsAction,
)
from pipe.web.dispatcher import dispatch_action

fs_bp = Blueprint("fs", __name__, url_prefix="/api/v1/fs")


@fs_bp.route("/search", methods=["POST"])
def search_sessions():
    """Search sessions."""
    response_data, status_code = dispatch_action(
        action=SearchSessionsAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/browse_l2", methods=["POST"])
def browse_l2():
    """L2 file search."""
    response_data, status_code = dispatch_action(
        action=SearchL2Action, params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/browse", methods=["POST"])
def browse():
    """List directory contents."""
    response_data, status_code = dispatch_action(
        action=LsAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/index_files", methods=["POST"])
def index_files():
    """Index files for search."""
    response_data, status_code = dispatch_action(
        action=IndexFilesAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/roles", methods=["GET"])
def get_roles():
    """Get available roles."""
    response_data, status_code = dispatch_action(
        action=GetRolesAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code


@fs_bp.route("/procedures", methods=["GET"])
def get_procedures():
    """Get available procedures."""
    response_data, status_code = dispatch_action(
        action=GetProceduresAction, params={}, request_data=request
    )
    return jsonify(response_data), status_code
