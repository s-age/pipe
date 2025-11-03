import json
import os
import sys
import zoneinfo

from flask import Flask, abort, jsonify, render_template, request
from flask_cors import CORS
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.utils.file import read_text_file, read_yaml_file
from pipe.web.requests.sessions.edit_reference_persist import (
    EditReferencePersistRequest,
)
from pipe.web.requests.sessions.edit_reference_ttl import EditReferenceTtlRequest
from pipe.web.requests.sessions.edit_references import EditReferencesRequest
from pipe.web.requests.sessions.edit_session_meta import EditSessionMetaRequest
from pipe.web.requests.sessions.edit_todos import EditTodosRequest
from pipe.web.requests.sessions.fork_session import ForkSessionRequest
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest
from pipe.web.requests.sessions.start_session import StartSessionRequest
from pydantic import ValidationError


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
    except FileNotFoundError:
        return {}


# Correctly determine the project root, which is three levels up from the current script
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

# Define paths for templates and static assets relative to the corrected project root
template_dir = os.path.join(project_root, "templates")
assets_dir = os.path.join(project_root, "assets")

app = Flask(__name__, template_folder=template_dir, static_folder=assets_dir)
CORS(app)

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


@app.route("/api/session/start", methods=["POST"])
def create_new_session_api():
    try:
        # Validate request body using the Pydantic model
        request_data = StartSessionRequest(**request.get_json())

        session = session_service.create_new_session(
            purpose=request_data.purpose,
            background=request_data.background,
            roles=request_data.roles,
            multi_step_reasoning_enabled=request_data.multi_step_reasoning_enabled,
            hyperparameters=request_data.hyperparameters,
            parent_id=request_data.parent,
            artifacts=request_data.artifacts,
            procedure=request_data.procedure,
        )
        session_id = session.session_id

        import subprocess

        command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--session",
            session_id,
            "--instruction",
            request_data.instruction,
        ]
        if request_data.references:
            command.extend(
                ["--references", ",".join([r.path for r in request_data.references])]
            )
        if request_data.artifacts:
            command.extend(["--artifacts", ",".join(request_data.artifacts)])
        if request_data.procedure:
            command.extend(["--procedure", request_data.procedure])
        if request_data.multi_step_reasoning_enabled:
            command.append("--multi-step-reasoning")

        subprocess.run(
            command, capture_output=True, text=True, check=True, encoding="utf-8"
        )

        return jsonify({"session_id": session_id}), 200

    except ValidationError as e:
        # Pydantic validation failed
        return jsonify({"message": str(e)}), 422
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Stderr from takt command: {e.stderr}", file=sys.stderr)
        return jsonify(
            {
                "message": (
                    "Conductor script failed during initial instruction processing."
                ),
                "details": e.stderr,
            }
        ), 500
    except Exception as e:
        return jsonify({"message": str(e)}), 500


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


@app.route("/api/sessions", methods=["GET"])
def get_sessions_api():
    try:
        sessions_collection = session_service.list_sessions()
        sorted_sessions = sessions_collection.get_sorted_by_last_updated()
        return jsonify({"sessions": sorted_sessions}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>", methods=["GET", "DELETE"])
def session_api(session_id):
    if request.method == "GET":
        try:
            session_data = session_service.get_session(session_id)
            if not session_data:
                return jsonify({"message": "Session not found."}), 404

            return jsonify({"session": session_data.to_dict()}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    if request.method == "DELETE":
        try:
            session_service.delete_session(session_id)
            return jsonify({"message": f"Session {session_id} deleted."}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>/turn/<int:turn_index>", methods=["DELETE"])
def delete_turn_api(session_id, turn_index):
    try:
        session_service.delete_turn(session_id, turn_index)
        return jsonify(
            {
                "message": (f"Turn {turn_index} from session {session_id} deleted."),
            }
        ), 200
    except FileNotFoundError:
        return jsonify({"message": "Session not found."}), 404
    except IndexError:
        return jsonify({"message": "Turn index out of range."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>/turns/<int:turn_index>", methods=["PATCH"])
def edit_turn_api(session_id, turn_index):
    try:
        new_data = request.get_json()
        if not new_data:
            return jsonify({"message": "No data provided."}), 400

        session_service.edit_turn(session_id, turn_index, new_data)
        return jsonify(
            {
                "message": f"Turn {turn_index + 1} from session {session_id} updated.",
            }
        ), 200
    except FileNotFoundError:
        return jsonify({"message": "Session not found."}), 404
    except IndexError:
        return jsonify({"message": "Turn index out of range."}), 400
    except ValueError as e:
        return jsonify({"message": str(e)}), 403
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>/meta", methods=["PATCH"])
def edit_session_meta_api(session_id):
    try:
        request_data = EditSessionMetaRequest(**request.get_json())
        session_service.edit_session_meta(
            session_id, request_data.model_dump(exclude_unset=True)
        )
        return jsonify({"message": f"Session {session_id} metadata updated."}), 200
    except ValidationError as e:
        return jsonify({"message": str(e)}), 422
    except FileNotFoundError:
        return jsonify({"message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>/todos", methods=["PATCH"])
def edit_todos_api(session_id):
    try:
        request_data = EditTodosRequest(**request.get_json())
        session_service.update_todos(session_id, request_data.todos)
        return jsonify({"message": f"Session {session_id} todos updated."}), 200
    except ValidationError as e:
        return jsonify({"message": str(e)}), 422
    except FileNotFoundError:
        return jsonify({"message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>/references", methods=["PATCH"])
def edit_references_api(session_id):
    try:
        request_data = EditReferencesRequest(**request.get_json())
        session_service.update_references(session_id, request_data.references)
        return jsonify({"message": f"Session {session_id} references updated."}), 200
    except ValidationError as e:
        return jsonify({"message": str(e)}), 422
    except FileNotFoundError:
        return jsonify({"message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route(
    "/api/session/<path:session_id>/references/<int:reference_index>/persist",
    methods=["PATCH"],
)
def edit_reference_persist_api(session_id, reference_index):
    try:
        request_data = EditReferencePersistRequest(**request.get_json())
        new_persist_state = request_data.persist

        session = session_service.get_session(session_id)
        if not session:
            return jsonify({"message": "Session not found."}), 404

        if not (0 <= reference_index < len(session.references)):
            return jsonify({"message": "Reference index out of range."}), 400

        file_path = session.references[reference_index].path
        session_service.update_reference_persist_in_session(
            session_id, file_path, new_persist_state
        )

        return jsonify(
            {
                "message": f"Persist state for reference {reference_index} updated.",
            }
        ), 200
    except ValidationError as e:
        return jsonify({"message": str(e)}), 422
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route(
    "/api/session/<path:session_id>/references/<int:reference_index>/ttl",
    methods=["PATCH"],
)
def edit_reference_ttl_api(session_id, reference_index):
    try:
        request_data = EditReferenceTtlRequest(**request.get_json())
        new_ttl = request_data.ttl

        session = session_service.get_session(session_id)
        if not session:
            return jsonify({"message": "Session not found."}), 404

        if not (0 <= reference_index < len(session.references)):
            return jsonify({"message": "Reference index out of range."}), 400

        file_path = session.references[reference_index].path
        session_service.update_reference_ttl_in_session(session_id, file_path, new_ttl)

        return jsonify(
            {
                "message": f"TTL for reference {reference_index} updated.",
            }
        ), 200
    except ValidationError as e:
        return jsonify({"message": str(e)}), 422
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>/todos", methods=["DELETE"])
def delete_todos_api(session_id):
    try:
        session_service.delete_todos(session_id)
        return jsonify({"message": f"Todos deleted from session {session_id}."}), 200
    except FileNotFoundError:
        return jsonify({"message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/fork/<int:fork_index>", methods=["POST"])
def fork_session_api(fork_index):
    try:
        request_data = ForkSessionRequest(**request.get_json())
        session_id = request_data.session_id

        new_session_id = session_service.fork_session(session_id, fork_index)
        if new_session_id:
            return jsonify({"new_session_id": new_session_id}), 200
        else:
            return jsonify({"message": "Failed to fork session."}), 500
    except ValidationError as e:
        return jsonify({"message": str(e)}), 422
    except FileNotFoundError:
        return jsonify({"message": "Session not found."}), 404
    except IndexError:
        return jsonify({"message": "Fork turn index out of range."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>/instruction", methods=["POST"])
def send_instruction_api(session_id):
    import json
    import subprocess

    from flask import Response, stream_with_context

    try:
        request_data = SendInstructionRequest(**request.get_json())
        instruction = request_data.instruction

        session_data = session_service.get_session(session_id)
        if not session_data:
            return jsonify({"message": "Session not found."}), 404

        # Pre-flight check for pool size before starting the subprocess
        if session_data.pools and len(session_data.pools) >= 7:
            error_message = (
                "Too many tasks in the processing pool (limit is 7). Please wait for "
                "the current tasks to complete before adding a new one."
            )

            def error_generate():
                yield f"data: {json.dumps({'error': error_message})}\n\n"

            return Response(
                stream_with_context(error_generate()),
                mimetype="text/event-stream",
                status=400,
            )

        enable_multi_step_reasoning = session_data.multi_step_reasoning_enabled

        # Use sys.executable to ensure the command runs with the same Python interpreter
        # that is running the Flask app. Use the 'takt' entry point.
        command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--session",
            session_id,
            "--instruction",
            instruction,
        ]
        if enable_multi_step_reasoning:
            command.append("--multi-step-reasoning")

        def generate():
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                bufsize=1,
            )

            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    yield f"data: {json.dumps({'content': line})}\n\n"
                process.stdout.close()

            stderr_output = ""
            if process.stderr:
                stderr_output = process.stderr.read()
                process.stderr.close()

            return_code = process.wait()

            if return_code != 0:
                yield f"data: {json.dumps({'error': stderr_output})}\n\n"

        return Response(stream_with_context(generate()), mimetype="text/event-stream")
    except ValidationError as e:
        return jsonify({"message": str(e)}), 422
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/session/<path:session_id>/turns", methods=["GET"])
def get_session_turns_api(session_id):
    try:
        since_index = request.args.get("since", 0, type=int)
        session_data = session_service.get_session(session_id)
        if not session_data:
            return jsonify({"message": "Session not found."}), 404

        all_turns = [turn.model_dump() for turn in session_data.turns]
        new_turns = all_turns[since_index:]

        return jsonify({"turns": new_turns}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/api/settings", methods=["GET"])
def get_settings_api():
    try:
        return jsonify({"settings": settings.model_dump()}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == "__main__":
    project_root_for_check = os.path.dirname(os.path.abspath(__file__))
    if check_and_show_warning(project_root_for_check):
        app.run(host="0.0.0.0", port=5001, debug=False)
    else:
        sys.exit(1)
