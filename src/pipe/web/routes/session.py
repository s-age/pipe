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


@session_bp.route("/session/<path:session_id>/raw", methods=["GET"])
def get_session_raw_file(session_id):
    """Get raw session file."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/raw",
        params={"session_id": session_id},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
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


@session_bp.route(
    "/session/<path:session_id>/turn/<int:turn_index>", methods=["DELETE"]
)
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


@session_bp.route("/session/<path:session_id>/turn/<int:turn_index>", methods=["PATCH"])
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


@session_bp.route("/session/<path:session_id>/meta", methods=["PATCH"])
def edit_session_meta(session_id):
    """Edit session metadata."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/meta",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route(
    "/session/<path:session_id>/hyperparameters", methods=["PATCH", "POST"]
)
def edit_hyperparameters(session_id):
    """Edit session hyperparameters."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/hyperparameters",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>/hyperparameters", methods=["OPTIONS"])
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


@session_bp.route(
    "/session/<path:session_id>/multi-step-reasoning", methods=["PATCH", "POST"]
)
def edit_multi_step_reasoning(session_id):
    """Edit multi-step reasoning settings."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/multi-step-reasoning",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>/multi_step_reasoning", methods=["PATCH"])
def edit_multi_step_reasoning_underscore(session_id):
    """Alternative endpoint with underscore naming (matches OpenAPI spec)."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/multi-step-reasoning",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route(
    "/session/<path:session_id>/multi-step-reasoning", methods=["OPTIONS"]
)
def edit_multi_step_reasoning_options(session_id):
    """Handle CORS preflight for multi-step reasoning."""
    from flask import make_response

    resp = make_response(("", 200))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = (
        "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    )
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp


@session_bp.route(
    "/session/<path:session_id>/multi_step_reasoning", methods=["OPTIONS"]
)
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


@session_bp.route("/session/<path:session_id>/todos", methods=["PATCH"])
def edit_todos(session_id):
    """Edit session todos."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/todos",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>/todos", methods=["DELETE"])
def delete_todos(session_id):
    """Delete session todos."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/todos",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>/references", methods=["PATCH"])
def edit_references(session_id):
    """Edit session references."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/references",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route(
    "/session/<path:session_id>/references/<int:reference_index>/persist",
    methods=["PATCH"],
)
def edit_reference_persist(session_id, reference_index):
    """Edit reference persist setting."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/references/{reference_index}/persist",
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route(
    "/session/<path:session_id>/references/<int:reference_index>/toggle",
    methods=["PATCH"],
)
def toggle_reference_disabled(session_id, reference_index):
    """Toggle reference disabled state."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/references/{reference_index}/toggle",
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route(
    "/session/<path:session_id>/references/<int:reference_index>/ttl",
    methods=["PATCH"],
)
def edit_reference_ttl(session_id, reference_index):
    """Edit reference TTL."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/references/{reference_index}/ttl",
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@session_bp.route("/session/<path:session_id>/fork/<int:fork_index>", methods=["POST"])
def fork_session(session_id, fork_index):
    """Fork a session at a specific index."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/fork/{fork_index}",
        params={"session_id": session_id, "fork_index": fork_index},
        request_data=request,
    )
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


@session_bp.route("/session_tree", methods=["GET"])
def get_session_tree():
    """Get session tree data."""
    try:
        response_data, status_code = dispatch_action(
            action="session_tree", params={}, request_data=request
        )
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@session_bp.route("/sessions/archives", methods=["GET", "POST", "DELETE"])
def sessions_archives():
    """List, create, or delete session archives."""
    response_data, status_code = dispatch_action(
        action="sessions/archives", params={}, request_data=request
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


@session_bp.route("/roles", methods=["GET"])
def get_roles():
    """Get available roles."""
    response_data, status_code = dispatch_action(
        action="roles", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@session_bp.route("/procedures", methods=["GET"])
def get_procedures():
    """Get available procedures."""
    response_data, status_code = dispatch_action(
        action="procedures", params={}, request_data=request
    )
    return jsonify(response_data), status_code
