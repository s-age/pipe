import json
import os
import sys
import zoneinfo

import yaml
from flask import Flask, Request, Response, abort, jsonify, render_template, request
from flask_cors import CORS
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.utils.file import read_text_file, read_yaml_file
from pipe.web.actions import (
    ApproveCompressorAction,
    CreateCompressorSessionAction,
    CreateTherapistSessionAction,
    DenyCompressorAction,
    GetProceduresAction,
    GetRolesAction,
    HyperparametersEditAction,
    MultiStepReasoningEditAction,
    ReferencePersistEditAction,
    ReferencesEditAction,
    ReferenceToggleDisabledAction,
    ReferenceTtlEditAction,
    SessionDeleteAction,
    SessionForkAction,
    SessionGetAction,
    SessionInstructionAction,
    SessionMetaEditAction,
    SessionRawAction,
    SessionsDeleteAction,
    SessionStartAction,
    SessionTreeAction,
    SessionTurnsGetAction,
    SettingsGetAction,
    TodosDeleteAction,
    TodosEditAction,
    TurnDeleteAction,
    TurnEditAction,
)
from pipe.web.actions.file_search_actions import (
    IndexFilesAction,
    LsAction,
    SearchL2Action,
)
from pipe.web.actions.search_sessions_action import SearchSessionsAction
from pipe.web.actions.therapist_actions import ApplyDoctorModificationsAction
from pipe.web.controllers import SessionDetailController


def check_and_show_warning(project_root: str) -> bool:
    """Checks for the warning file, displays it, and gets user consent."""
    sealed_path = os.path.join(project_root, "sealed.txt")
    unsealed_path = os.path.join(project_root, "unsealed.txt")

    if os.path.exists(unsealed_path):
        return True

    warning_content = read_text_file(sealed_path)
    if not warning_content:
        return True

    print("--- IMPORTANT NOTICE ---")
    print(warning_content)
    print("------------------------")

    while True:
        try:
            response = (
                input("Do you agree to the terms above? (yes/no): ").lower().strip()
            )
            if response == "yes":
                os.rename(sealed_path, unsealed_path)
                print("Thank you. Proceeding...")
                return True
            elif response == "no":
                print("You must agree to the terms to use this tool. Exiting.")
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled. Exiting.")
            return False


def load_settings(config_path: str) -> dict:
    try:
        return read_yaml_file(config_path)
    except (FileNotFoundError, yaml.YAMLError):
        default_path = config_path.replace("setting.yml", "setting.default.yml")
        try:
            return read_yaml_file(default_path)
        except (FileNotFoundError, yaml.YAMLError):
            return {}


# Correctly determine the project root, which is three levels up from the current script
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

# Define paths for templates and static assets relative to the corrected project root
template_dir = os.path.join(project_root, "templates")
assets_dir = os.path.join(project_root, "assets")

app = Flask(__name__, template_folder=template_dir, static_folder=assets_dir)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": False,
            "max_age": 3600,
        }
    },
)


@app.before_request
def _log_incoming_request():
    # small debug logging so dev can see whether OPTIONS or PATCH actually reach Flask
    try:
        print(f"DEBUG: incoming {request.method} {request.path}")
    except Exception:
        pass


project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
config_path = os.path.join(project_root, "setting.yml")
settings_dict = load_settings(config_path)
settings = Settings(**settings_dict)

tz_name = settings.timezone
try:
    local_tz = zoneinfo.ZoneInfo(tz_name)
except zoneinfo.ZoneInfoNotFoundError:
    print(
        f"Warning: Timezone '{tz_name}' from setting.yml not found. Using UTC.",
        file=sys.stderr,
    )
    local_tz = zoneinfo.ZoneInfo("UTC")

session_service = ServiceFactory(project_root, settings).create_session_service()

# BFF (Backend for Frontend) Controllers
# BFF controllers aggregate multiple actions into optimized responses
# Naming convention: /api/v1/bff/<feature>-dashboard/{id}
# Example: /api/v1/bff/session-dashboard/{session_id} aggregates session data
session_detail_controller = SessionDetailController(session_service, settings)

file_indexer_service = ServiceFactory(
    project_root, settings
).create_file_indexer_service()
search_l2_action = SearchL2Action(file_indexer_service, {})
ls_action = LsAction(file_indexer_service, {})
index_files_action = IndexFilesAction(file_indexer_service, {})


def dispatch_action(
    action: str, params: dict, request_data: Request | None = None
) -> tuple[dict | Response, int]:
    method = request_data.method if request_data else "GET"

    route_map = [
        ("session_tree", "GET", SessionTreeAction),
        ("settings", "GET", SettingsGetAction),
        ("session/start", "POST", SessionStartAction),
        ("compress", "POST", CreateCompressorSessionAction),
        ("compress/{session_id}/approve", "POST", ApproveCompressorAction),
        ("compress/{session_id}/deny", "POST", DenyCompressorAction),
        ("therapist", "POST", CreateTherapistSessionAction),
        ("doctor", "POST", ApplyDoctorModificationsAction),
        ("sessions/delete", "POST", SessionsDeleteAction),
        ("session/{session_id}/raw", "GET", SessionRawAction),
        ("session/{session_id}/instruction", "POST", SessionInstructionAction),
        ("session/{session_id}/meta", "PATCH", SessionMetaEditAction),
        ("session/{session_id}/hyperparameters", "PATCH", HyperparametersEditAction),
        ("session/{session_id}/hyperparameters", "POST", HyperparametersEditAction),
        (
            "session/{session_id}/multi-step-reasoning",
            "PATCH",
            MultiStepReasoningEditAction,
        ),
        (
            "session/{session_id}/multi-step-reasoning",
            "POST",
            MultiStepReasoningEditAction,
        ),
        ("session/{session_id}/todos", "PATCH", TodosEditAction),
        ("session/{session_id}/todos", "DELETE", TodosDeleteAction),
        (
            "session/{session_id}/references/{reference_index}/persist",
            "PATCH",
            ReferencePersistEditAction,
        ),
        (
            "session/{session_id}/references/{reference_index}/toggle",
            "PATCH",
            ReferenceToggleDisabledAction,
        ),
        (
            "session/{session_id}/references/{reference_index}/ttl",
            "PATCH",
            ReferenceTtlEditAction,
        ),
        ("session/{session_id}/references", "PATCH", ReferencesEditAction),
        ("session/{session_id}/turn/{turn_index}", "PATCH", TurnEditAction),
        ("session/{session_id}/turns", "GET", SessionTurnsGetAction),
        ("session/{session_id}/turn/{turn_index}", "DELETE", TurnDeleteAction),
        ("session/{session_id}/fork/{fork_index}", "POST", SessionForkAction),
        ("session/{session_id}", "GET", SessionGetAction),
        ("session/{session_id}", "DELETE", SessionDeleteAction),
        ("roles", "GET", GetRolesAction),
        ("procedures", "GET", GetProceduresAction),
        ("search_l2", "POST", search_l2_action),
        ("search", "POST", SearchSessionsAction),
        ("ls", "POST", ls_action),
        ("index_files", "POST", index_files_action),
    ]

    for route_pattern, route_method, action_class in route_map:
        if route_method != method:
            continue

        pattern_parts = route_pattern.split("/")
        action_parts = action.split("/")

        # Flexible matching to allow path-like parameters
        # (e.g. session IDs containing '/').
        # We walk the pattern parts and action parts; when a pattern part is a
        # placeholder we capture one or more action parts into that parameter.
        # If a placeholder is followed by a literal in the pattern, we capture
        # until that literal appears in the action parts. If it's the last
        # pattern part, capture the rest of action_parts.
        match = True
        pi = 0
        ai = 0
        while pi < len(pattern_parts) and ai < len(action_parts):
            pp = pattern_parts[pi]
            if pp.startswith("{") and pp.endswith("}"):
                param_name = pp[1:-1]
                # If this is the last pattern part, capture the rest
                if pi == len(pattern_parts) - 1:
                    params[param_name] = "/".join(action_parts[ai:])
                    ai = len(action_parts)
                    pi += 1
                    break

                # Otherwise, find the next literal pattern part to know where to stop
                next_literal = None
                for nxt in pattern_parts[pi + 1 :]:
                    if not (nxt.startswith("{") and nxt.endswith("}")):
                        next_literal = nxt
                        break

                if next_literal is None:
                    # No following literal, capture the rest
                    params[param_name] = "/".join(action_parts[ai:])
                    ai = len(action_parts)
                    pi = len(pattern_parts)
                    break

                # Find the index in action_parts where next_literal appears
                found_index = None
                for look in range(ai, len(action_parts)):
                    if action_parts[look] == next_literal:
                        found_index = look
                        break

                if found_index is None:
                    match = False
                    break

                # Capture action parts from ai up to found_index as the param
                params[param_name] = "/".join(action_parts[ai:found_index])
                ai = found_index
                pi += 1
                continue

            # literal must match exactly
            if action_parts[ai] != pp:
                match = False
                break

            pi += 1
            ai += 1

        # If we've consumed pattern parts, ai should have consumed all action parts
        if pi != len(pattern_parts) or ai != len(action_parts):
            match = False

        if match:
            try:
                if isinstance(action_class, type):
                    action_instance = action_class(
                        params=params,
                        request_data=request_data,
                    )
                else:
                    action_instance = action_class
                    action_instance.params = params
                    action_instance.request_data = request_data
                return action_instance.execute()
            except Exception as e:
                return {"message": str(e)}, 500

    return {"message": f"Unknown action: {action} with method {method}"}, 404


@app.route("/")
def index():
    sessions_collection = session_service.list_sessions()
    sorted_sessions = sessions_collection.get_sorted_by_last_updated()
    return render_template(
        "html/index.html",
        sessions=sorted_sessions,
        current_session_id=None,
        session_data=json.dumps({}),
        expert_mode=settings.expert_mode,
        settings=settings.model_dump(),
    )


@app.route("/start_session")
def start_session_form():
    sessions_collection = session_service.list_sessions()
    sorted_sessions = sessions_collection.get_sorted_by_last_updated()
    return render_template(
        "html/start_session.html",
        settings=settings.model_dump(),
        sessions=sorted_sessions,
    )


@app.route("/api/v1/session/start", methods=["POST"])
def create_new_session_api_v1():
    response_data, status_code = dispatch_action(
        action="session/start", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/raw", methods=["GET"])
def get_session_raw_file(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/raw",
        params={"session_id": session_id},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@app.route("/session/<path:session_id>")
def view_session(session_id):
    sessions_collection = session_service.list_sessions()
    if session_id not in sessions_collection:
        abort(404)

    sorted_sessions = sessions_collection.get_sorted_by_last_updated()

    session_data = session_service.get_session(session_id)
    if not session_data:
        abort(404)

    # Populate missing hyperparameters with defaults from settings
    defaults = settings.parameters
    if not session_data.hyperparameters:
        from pipe.core.models.hyperparameters import Hyperparameters

        session_data.hyperparameters = Hyperparameters()

    for param_name in ["temperature", "top_p", "top_k"]:
        if getattr(session_data.hyperparameters, param_name) is None:
            if default_value := getattr(defaults, param_name, None):
                setattr(
                    session_data.hyperparameters,
                    param_name,
                    default_value,
                )

    if session_data.references and isinstance(session_data.references[0], str):
        from pipe.core.models.reference import Reference

        session_data.references = [
            Reference(path=ref, disabled=False) for ref in session_data.references
        ]
        session_service.update_references(session_id, session_data.references)

    # Use the model's own method to get a serializable dictionary
    session_data_for_template = session_data.to_dict()
    # Ensure artifacts are passed as a list of strings for the template
    session_data_for_template["artifacts"] = session_data.artifacts
    turns_list = session_data_for_template["turns"]

    current_session_purpose = session_data.purpose
    multi_step_reasoning_enabled = session_data.multi_step_reasoning_enabled
    token_count = session_data.token_count
    context_limit = settings.context_limit
    expert_mode = settings.expert_mode

    return render_template(
        "html/index.html",
        sessions=sorted_sessions,
        current_session_id=session_id,
        current_session_purpose=current_session_purpose,
        session_data=session_data_for_template,
        turns=turns_list,
        multi_step_reasoning_enabled=multi_step_reasoning_enabled,
        token_count=token_count,
        context_limit=context_limit,
        expert_mode=expert_mode,
        settings=settings.model_dump(),
    )


@app.route("/api/v1/session_tree", methods=["GET"])
def get_session_tree_api():
    """Get session tree data (v1 API)."""
    try:
        response_data, status_code = dispatch_action(
            action="session_tree", params={}, request_data=request
        )
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/v1/session/<path:session_id>", methods=["GET", "DELETE"])
def session_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}",
        params={"session_id": session_id},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@app.route("/api/v1/search", methods=["POST"])
def search_sessions_api():
    """Explicit v1 search endpoint forwarding to the search action.

    This keeps the `/api/v1` prefix explicit and avoids ambiguity with
    dev-server proxies or clients that expect the v1 path to be present.
    """
    response_data, status_code = dispatch_action(
        action="search", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/compress", methods=["POST"])
def create_compressor_session():
    response_data, status_code = dispatch_action(
        action="compress", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/therapist", methods=["POST"])
def create_therapist_session():
    response_data, status_code = dispatch_action(
        action="therapist", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/doctor", methods=["POST"])
def apply_doctor_modifications():
    response_data, status_code = dispatch_action(
        action="doctor", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@app.route(
    "/api/v1/session/<path:session_id>/turn/<int:turn_index>", methods=["DELETE"]
)
def delete_turn_api(session_id, turn_index):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/turn/{turn_index}",
        params={"session_id": session_id, "turn_index": turn_index},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/turn/<int:turn_index>", methods=["PATCH"])
def edit_turn_api(session_id, turn_index):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/turn/{turn_index}",
        params={"session_id": session_id, "turn_index": turn_index},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/meta", methods=["PATCH"])
def edit_session_meta_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/meta",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route(
    "/api/v1/session/<path:session_id>/hyperparameters", methods=["PATCH", "POST"]
)
def edit_hyperparameters_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/hyperparameters",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/hyperparameters", methods=["OPTIONS"])
def edit_hyperparameters_options(session_id):
    from flask import make_response

    resp = make_response(("", 200))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = (
        "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    )
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp


@app.route(
    "/api/v1/session/<path:session_id>/multi-step-reasoning", methods=["PATCH", "POST"]
)
def edit_multi_step_reasoning_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/multi-step-reasoning",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/multi_step_reasoning", methods=["PATCH"])
def edit_multi_step_reasoning_underscore_api(session_id):
    """Alternative endpoint with underscore naming (matches OpenAPI spec)."""
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/multi-step-reasoning",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route(
    "/api/v1/session/<path:session_id>/multi-step-reasoning", methods=["OPTIONS"]
)
def edit_multi_step_reasoning_options(session_id):
    from flask import make_response

    resp = make_response(("", 200))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = (
        "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    )
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp


@app.route(
    "/api/v1/session/<path:session_id>/multi_step_reasoning", methods=["OPTIONS"]
)
def edit_multi_step_reasoning_underscore_options(session_id):
    """Alternative OPTIONS endpoint with underscore naming (matches OpenAPI spec)."""
    from flask import make_response

    resp = make_response(("", 200))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = (
        "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    )
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp


@app.route("/api/v1/session/<path:session_id>/todos", methods=["PATCH"])
def edit_todos_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/todos",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/references", methods=["PATCH"])
def edit_references_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/references",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route(
    "/api/v1/session/<path:session_id>/references/<int:reference_index>/persist",
    methods=["PATCH"],
)
def edit_reference_persist_api(session_id, reference_index):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/references/{reference_index}/persist",
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route(
    "/api/v1/session/<path:session_id>/references/<int:reference_index>/toggle",
    methods=["PATCH"],
)
def toggle_reference_disabled_api(session_id, reference_index):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/references/{reference_index}/toggle",
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route(
    "/api/v1/session/<path:session_id>/references/<int:reference_index>/ttl",
    methods=["PATCH"],
)
def edit_reference_ttl_api(session_id, reference_index):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/references/{reference_index}/ttl",
        params={"session_id": session_id, "reference_index": reference_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/todos", methods=["DELETE"])
def delete_todos_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/todos",
        params={"session_id": session_id},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/fork/<int:fork_index>", methods=["POST"])
def fork_session_api(session_id, fork_index):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/fork/{fork_index}",
        params={"session_id": session_id, "fork_index": fork_index},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/instruction", methods=["POST"])
def send_instruction_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/instruction",
        params={"session_id": session_id},
        request_data=request,
    )
    if isinstance(response_data, Response):
        return response_data
    return jsonify(response_data), status_code


@app.route("/api/v1/session/<path:session_id>/turns", methods=["GET"])
def get_session_turns_api(session_id):
    response_data, status_code = dispatch_action(
        action=f"session/{session_id}/turns",
        params={"session_id": session_id, "since": request.args.get("since", 0)},
        request_data=request,
    )
    return jsonify(response_data), status_code


@app.route("/api/v1/settings", methods=["GET"])
def get_settings_api():
    response_data, status_code = dispatch_action(
        action="settings", params={}, request_data=request
    )
    return jsonify(response_data), status_code


# BFF (Backend for Frontend) Endpoints
# These endpoints aggregate multiple API calls to optimize frontend performance
# Naming: /api/v1/bff/<feature>-dashboard/{id}
# This endpoint aggregates: session_tree + session/{session_id} + settings
@app.route("/api/v1/bff/session-dashboard/<path:session_id>", methods=["GET"])
def get_session_dashboard(session_id):
    """
    BFF endpoint for session dashboard.
    Aggregates session tree, current session details, and settings in a single request.
    """
    try:
        response_data, status_code = session_detail_controller.get_session_with_tree(
            session_id=session_id, request_data=request
        )
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/v1/bff/start-session-settings", methods=["GET"])
def get_start_session_settings():
    """
    BFF endpoint for start session settings.
    Aggregates settings and session tree in a single request.
    """
    try:
        response_data, status_code = session_detail_controller.get_settings_with_tree(
            request_data=request
        )
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/v1/sessions/delete", methods=["POST"])
def delete_sessions_api():
    response_data, status_code = dispatch_action(
        action="sessions/delete", params={}, request_data=request
    )
    return jsonify(response_data), status_code


@app.route(
    "/api/v1/<path:action>", methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
)
def dispatch_action_endpoint(action: str):
    """
    Central dispatcher for v1 API endpoints.
    Routes actions to appropriate handlers via dispatch_action().

    BFF endpoints are handled separately before dispatch_action:
    - Pattern: bff/<feature>-dashboard/{id}
    - These aggregate multiple actions for optimized frontend responses
    """
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,PATCH,DELETE,OPTIONS"
        )
        return response, 200

    try:
        # Handle BFF endpoints (Backend for Frontend aggregated responses)
        # BFF endpoints bypass dispatch_action and use specialized controllers
        if action.startswith("bff/session-dashboard/"):
            session_id = action.replace("bff/session-dashboard/", "")
            response_data, status_code = (
                session_detail_controller.get_session_with_tree(
                    session_id=session_id, request_data=request
                )
            )
            return jsonify(response_data), status_code

        params = dict(request.view_args or {})
        params.update(request.args.to_dict())

        if action.startswith("session/"):
            parts = action.split("/")
            if len(parts) >= 2:
                params["session_id"] = parts[1]
                if len(parts) >= 3:
                    if parts[2] == "turn" and len(parts) >= 4:
                        params["turn_index"] = parts[3]
                    elif parts[2] == "references" and len(parts) >= 4:
                        params["reference_index"] = parts[3]
                    elif parts[2] == "fork" and len(parts) >= 4:
                        params["fork_index"] = parts[3]

        response_data, status_code = dispatch_action(
            action=action, params=params, request_data=request
        )

        if isinstance(response_data, Response):
            return response_data

        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == "__main__":
    # Rebuild Whoosh index on startup
    try:
        print("Rebuilding Whoosh index...")
        file_indexer_service.index_files()
        print("Whoosh index rebuilt successfully")
    except Exception as e:
        print(f"Failed to rebuild Whoosh index: {e}")

    project_root_for_check = os.path.dirname(os.path.abspath(__file__))
    if check_and_show_warning(project_root_for_check):
        # Debug: print URL map so we can inspect which methods are registered
        try:
            for rule in app.url_map.iter_rules():
                print(f"DEBUG: route {rule.rule} methods={sorted(rule.methods or [])}")
        except Exception:
            pass

        # Print runtime path diagnostics so we can detect mismatches between
        # the module-computed project_root and the runtime working directory.
        try:
            import os as _os

            print(f"DEBUG: module project_root = {project_root}")
            print(f"DEBUG: current working dir = {_os.getcwd()}")
            # session_service created at module import; print its repository path
            repo = getattr(session_service, "repository", None)
            if repo is not None:
                print(
                    f"DEBUG: session repository sessions_dir = "
                    f"{getattr(repo, 'sessions_dir', None)}"
                )
            else:
                print("DEBUG: session_service.repository not available")
        except Exception:
            pass
        app.run(host="0.0.0.0", port=5001, debug=False)
    else:
        sys.exit(1)
