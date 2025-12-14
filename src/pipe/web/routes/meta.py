"""Meta-related API routes.

Handles all /api/v1/session/<session_id>/meta/* endpoints.
"""

from flask import Blueprint, jsonify, request
from pipe.web.actions import (
    HyperparametersEditAction,
    MultiStepReasoningEditAction,
    ReferencePersistEditAction,
    ReferencesEditAction,
    ReferenceToggleDisabledAction,
    ReferenceTtlEditAction,
    SessionMetaEditAction,
    TodosDeleteAction,
    TodosEditAction,
)
from pipe.web.dispatcher import dispatch_action

meta_bp = Blueprint("meta", __name__, url_prefix="/api/v1/session/<path:session_id>")


@meta_bp.route("/meta", methods=["PATCH"])
def edit_session_meta(session_id):
    """Edit session metadata."""
    response_data, status_code = dispatch_action(
        action=SessionMetaEditAction,
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@meta_bp.route("/hyperparameters", methods=["PATCH", "POST"])
def edit_hyperparameters(session_id):
    """Edit session hyperparameters."""
    response_data, status_code = dispatch_action(
        action=HyperparametersEditAction,
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@meta_bp.route("/hyperparameters", methods=["OPTIONS"])
def edit_hyperparameters_options(session_id):
    """Handle CORS preflight for hyperparameters."""
    from flask import make_response

    resp = make_response(("", 200))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = (
        "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    )
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp


@meta_bp.route("/multi_step_reasoning", methods=["PATCH"])
def edit_multi_step_reasoning_underscore(session_id):
    """Alternative endpoint with underscore naming (matches OpenAPI spec)."""
    response_data, status_code = dispatch_action(
        action=MultiStepReasoningEditAction,
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@meta_bp.route("/multi_step_reasoning", methods=["OPTIONS"])
def edit_multi_step_reasoning_underscore_options(session_id):
    """Handle CORS preflight for multi-step reasoning (underscore naming)."""
    from flask import make_response

    resp = make_response(("", 200))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = (
        "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    )
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp


@meta_bp.route("/todos", methods=["PATCH"])
def edit_todos(session_id):
    """Edit session todos."""
    response_data, status_code = dispatch_action(
        action=TodosEditAction,
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@meta_bp.route("/todos", methods=["DELETE"])
def delete_todos(session_id):
    """Delete session todos."""
    response_data, status_code = dispatch_action(
        action=TodosDeleteAction,
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@meta_bp.route("/references", methods=["PATCH"])
def edit_references(session_id):
    """Edit session references."""
    response_data, status_code = dispatch_action(
        action=ReferencesEditAction,
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@meta_bp.route("/references/<int:reference_index>/persist", methods=["PATCH"])
def edit_reference_persist(session_id, reference_index):
    """Edit reference persist setting."""
    response_data, status_code = dispatch_action(
        action=ReferencePersistEditAction,
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@meta_bp.route("/references/<int:reference_index>/toggle", methods=["PATCH"])
def toggle_reference_disabled(session_id, reference_index):
    """Toggle reference disabled state."""
    response_data, status_code = dispatch_action(
        action=ReferenceToggleDisabledAction,
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@meta_bp.route("/references/<int:reference_index>/ttl", methods=["PATCH"])
def edit_reference_ttl(session_id, reference_index):
    """Edit reference TTL."""
    response_data, status_code = dispatch_action(
        action=ReferenceTtlEditAction,
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code
