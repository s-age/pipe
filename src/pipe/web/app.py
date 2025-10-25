from flask import Flask, render_template, abort, jsonify, request
from datetime import timezone
import zoneinfo
import json
import sys
import yaml
from pipe.core.services.session_service import SessionService
from pipe.core.utils.file import read_text_file, read_yaml_file
import os

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
            response = input("Do you agree to the terms above? (yes/no): ").lower().strip()
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
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Define paths for templates and static assets relative to the corrected project root
template_dir = os.path.join(project_root, 'templates')
assets_dir = os.path.join(project_root, 'assets')

app = Flask(__name__, template_folder=template_dir, static_folder=assets_dir)

config_path = os.path.join(project_root, 'setting.yml')
settings = load_settings(config_path)
tz_name = settings.get('timezone', 'UTC')
try:
    local_tz = zoneinfo.ZoneInfo(tz_name)
except zoneinfo.ZoneInfoNotFoundError:
    print(f"Warning: Timezone '{tz_name}' from setting.yml not found. Using UTC.", file=sys.stderr)
    local_tz = timezone.utc
session_service = SessionService(os.path.join(project_root, 'sessions'), default_hyperparameters=settings.get('parameters', {}))

@app.route('/')
def index():
    sessions_index = session_service.list_sessions()
    sorted_sessions = sorted(sessions_index.items())
    return render_template('html/index.html', sessions=sorted_sessions, current_session_id=None, session_data=json.dumps({}), expert_mode=settings.get('expert_mode', False), settings=settings)

@app.route('/new_session')
def new_session_form():
    sessions_index = session_service.list_sessions()
    sorted_sessions = sorted(sessions_index.items())
    return render_template('html/new_session.html', settings=settings, sessions=sorted_sessions)

@app.route('/api/session/new', methods=['POST'])
def create_new_session_api():
    try:
        data = request.get_json()
        purpose = data.get('purpose')
        background = data.get('background')
        roles_str = data.get('roles', '')
        parent_id = data.get('parent')
        references_str = data.get('references', '')
        instruction = data.get('instruction')
        multi_step_reasoning_enabled = data.get('multi_step_reasoning_enabled', False)
        hyperparameters = data.get('hyperparameters')

        if not all([purpose, background, instruction]):
            return jsonify({"success": False, "message": "Purpose, background, and first instruction are required."}), 400
        
        roles = [r.strip() for r in roles_str.split(',') if r.strip()]

        session_id = session_service.create_new_session(
            purpose=purpose,
            background=background,
            roles=roles,
            multi_step_reasoning_enabled=multi_step_reasoning_enabled,
            hyperparameters=hyperparameters,
            parent_id=parent_id
        )
        
        import subprocess
        command = [sys.executable, '-m', 'pipe.cli.takt', '--session', session_id, '--instruction', instruction]
        if references_str:
            command.extend(['--references', references_str])
        if multi_step_reasoning_enabled:
            command.append('--multi-step-reasoning')
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8'
        )
        
        return jsonify({"success": True, "session_id": session_id}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": "Conductor script failed during initial instruction processing.", "details": e.stderr}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/session/<path:session_id>')
def view_session(session_id):
    sessions_index = session_service.list_sessions()
    if session_id not in sessions_index:
        abort(404)

    sorted_sessions = sorted(
        sessions_index.items(),
        key=lambda item: item[1].get('last_updated', ''),
        reverse=True
    )
    
    session_data = session_service.get_session(session_id)
    if not session_data:
        abort(404)

    # Populate missing hyperparameters with defaults from settings
    defaults = settings.get('parameters', {})
    if not session_data.hyperparameters:
        from pipe.core.models.hyperparameters import Hyperparameters
        session_data.hyperparameters = Hyperparameters()

    for param_name in ['temperature', 'top_p', 'top_k']:
        if getattr(session_data.hyperparameters, param_name) is None:
            if default_value := defaults.get(param_name):
                from pipe.core.models.hyperparameters import HyperparameterValue
                setattr(session_data.hyperparameters, param_name, HyperparameterValue(**default_value))

    if session_data.references and isinstance(session_data.references[0], str):
        from pipe.core.models.reference import Reference
        session_data.references = [Reference(path=ref, disabled=False) for ref in session_data.references]
        session_service.update_references(session_id, session_data.references)

    turns = session_data.turns
    
    current_session_purpose = session_data.purpose
    multi_step_reasoning_enabled = session_data.multi_step_reasoning_enabled
    token_count = session_data.token_count
    context_limit = settings.get('context_limit', 1000000)
    expert_mode = settings.get('expert_mode', False)

    return render_template('html/index.html',
                           sessions=sorted_sessions,
                           current_session_id=session_id,
                           current_session_purpose=current_session_purpose,
                           session_data=session_data.model_dump(),
                           turns=turns,
                           multi_step_reasoning_enabled=multi_step_reasoning_enabled,
                           token_count=token_count,
                           context_limit=context_limit,
                           expert_mode=expert_mode,
                           settings=settings)

@app.route('/api/sessions', methods=['GET'])
def get_sessions_api():
    try:
        sessions_index = session_service.list_sessions()
        sorted_sessions = sorted(
            sessions_index.items(),
            key=lambda item: item[1].get('last_updated', ''),
            reverse=True
        )
        return jsonify({"success": True, "sessions": sorted_sessions}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>', methods=['GET', 'DELETE'])
def session_api(session_id):
    if request.method == 'GET':
        try:
            session_data = session_service.get_session(session_id)
            if not session_data:
                return jsonify({"success": False, "message": "Session not found."} ), 404
            return jsonify({"success": True, "session": session_data.model_dump()}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
            
    if request.method == 'DELETE':
        try:
            session_service.delete_session(session_id)
            return jsonify({"success": True, "message": f"Session {session_id} deleted."} ), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>/turn/<int:turn_index>', methods=['DELETE'])
def delete_turn_api(session_id, turn_index):
    try:
        session = session_service.get_session(session_id)
        if not session:
            return jsonify({"success": False, "message": "Session not found."}), 404
        
        if 0 <= turn_index < len(session.turns):
            del session.turns[turn_index]
            session_service._save_session(session)
            return jsonify({"success": True, "message": f"Turn {turn_index} from session {session_id} deleted."}), 200
        else:
            return jsonify({"success": False, "message": "Turn index out of range."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>/turn/<int:turn_index>/edit', methods=['POST'])
def edit_turn_api(session_id, turn_index):
    try:
        new_data = request.get_json()
        if not new_data:
            return jsonify({"success": False, "message": "No data provided."}), 400

        session = session_service.get_session(session_id)
        if not session:
            return jsonify({"success": False, "message": "Session not found."}), 404

        if 0 <= turn_index < len(session.turns):
            original_turn = session.turns[turn_index]
            if original_turn.type not in ["user_task", "tool_response"]:
                return jsonify({"success": False, "message": f"Editing turns of type '{original_turn.type}' is not allowed."}), 403

            turn_as_dict = original_turn.model_dump()
            turn_as_dict.update(new_data)
            
            from pipe.core.models.turn import UserTaskTurn, ToolResponseTurn
            if original_turn.type == "user_task":
                session.turns[turn_index] = UserTaskTurn(**turn_as_dict)
            elif original_turn.type == "tool_response":
                session.turns[turn_index] = ToolResponseTurn(**turn_as_dict)

            session_service._save_session(session)
            return jsonify({"success": True, "message": f"Turn {turn_index + 1} from session {session_id} updated."}), 200
        else:
            return jsonify({"success": False, "message": "Turn index out of range."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>/meta/edit', methods=['POST'])
def edit_session_meta_api(session_id):
    try:
        new_meta_data = request.get_json()
        if not new_meta_data or not any(k in new_meta_data for k in ['purpose', 'background', 'multi_step_reasoning_enabled', 'token_count', 'hyperparameters']):
            return jsonify({"success": False, "message": "No data provided."} ), 400

        session_service.edit_session_meta(session_id, new_meta_data)
        return jsonify({"success": True, "message": f"Session {session_id} metadata updated."} ), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."} ), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>/todos/edit', methods=['POST'])
def edit_todos_api(session_id):
    try:
        data = request.get_json()
        if 'todos' not in data:
            return jsonify({"success": False, "message": "No todos data provided."} ), 400

        session_service.update_todos(session_id, data['todos'])
        return jsonify({"success": True, "message": f"Session {session_id} todos updated."} ), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."} ), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>/references/edit', methods=['POST'])
def edit_references_api(session_id):
    try:
        data = request.get_json()
        if 'references' not in data:
            return jsonify({"success": False, "message": "No references data provided."} ), 400

        session_service.update_references(session_id, data['references'])
        return jsonify({"success": True, "message": f"Session {session_id} references updated."} ), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."} ), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>/todos', methods=['DELETE'])
def delete_todos_api(session_id):
    try:
        session_service.delete_todos(session_id)
        return jsonify({"success": True, "message": f"Todos deleted from session {session_id}."} ), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."} ), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/fork/<int:fork_index>', methods=['POST'])
def fork_session_api(fork_index):
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({"success": False, "message": "session_id not provided in request body."} ), 400

        new_session_id = session_service.fork_session(session_id, fork_index)
        if new_session_id:
            return jsonify({"success": True, "new_session_id": new_session_id}), 200
        else:
            return jsonify({"success": False, "message": "Failed to fork session."} ), 500
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."} ), 404
    except IndexError:
        return jsonify({"success": False, "message": "Fork turn index out of range."} ), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>/instruction', methods=['POST'])
def send_instruction_api(session_id):
    from flask import Response, stream_with_context
    import subprocess
    import json

    try:
        new_data = request.get_json()
        instruction = new_data.get('instruction')
        if not instruction:
            return jsonify({"success": False, "message": "No instruction provided."} ), 400

        session_data = session_service.get_session(session_id)
        if not session_data:
            return jsonify({"success": False, "message": "Session not found."} ), 404
        
        enable_multi_step_reasoning = session_data.multi_step_reasoning_enabled

        # Use sys.executable to ensure the command runs with the same Python interpreter
        # that is running the Flask app. Use the 'takt' entry point.
        command = [sys.executable, '-m', 'pipe.cli.takt', '--session', session_id, '--instruction', instruction]
        if enable_multi_step_reasoning:
            command.append('--multi-step-reasoning')

        def generate():
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding='utf-8',
                bufsize=1
            )

            for line in iter(process.stdout.readline, ''):
                yield f"data: {json.dumps({'content': line})}\n\n"
            
            process.stdout.close()
            stderr_output = process.stderr.read()
            process.stderr.close()
            
            return_code = process.wait()

            if return_code != 0:
                yield f"data: {json.dumps({'error': stderr_output})}\n\n"
            
            yield "event: end\ndata: \n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<path:session_id>/turns', methods=['GET'])
def get_session_turns_api(session_id):
    try:
        since_index = request.args.get('since', 0, type=int)
        session_data = session_service.get_session(session_id)
        if not session_data:
            return jsonify({"success": False, "message": "Session not found."} ), 404
        
        all_turns = [turn.model_dump() for turn in session_data.turns]
        new_turns = all_turns[since_index:]
        
        return jsonify({"success": True, "turns": new_turns}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    project_root_for_check = os.path.dirname(os.path.abspath(__file__))
    if check_and_show_warning(project_root_for_check):
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        sys.exit(1)
