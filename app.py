from flask import Flask, render_template, abort, jsonify, request
from datetime import timezone
import zoneinfo

import sys
import yaml
from src.history_manager import HistoryManager
from src.utils import read_text_file, read_yaml_file
import os

def check_and_show_warning(project_root: str) -> bool:
    """Checks for the warning file, displays it, and gets user consent."""
    sealed_path = os.path.join(project_root, "sealed.txt")
    unsealed_path = os.path.join(project_root, "unsealed.txt")

    if os.path.exists(unsealed_path):
        return True  # Already agreed

    warning_content = read_text_file(sealed_path)
    if not warning_content:
        return True  # No warning file or empty file, proceed

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

app = Flask(__name__)
project_root = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(project_root, 'setting.yml')
settings = load_settings(config_path)
# Timezone initialization from setting.yml
tz_name = settings.get('timezone', 'UTC')
try:
    local_tz = zoneinfo.ZoneInfo(tz_name)
except zoneinfo.ZoneInfoNotFoundError:
    print(f"Warning: Timezone '{tz_name}' from setting.yml not found. Using UTC.", file=sys.stderr)
    local_tz = timezone.utc
history_manager = HistoryManager(os.path.join(project_root, 'sessions'), local_tz, default_hyperparameters=settings.get('parameters', {}))

@app.route('/')
def index():
    """
    Serves the main HTML page for viewing conversation history.
    """
    sessions_index = history_manager.list_sessions()
    # 最終更新日時でセッションをソート
    sorted_sessions = sorted(
        sessions_index.items(),
        key=lambda item: item[1].get('last_updated', ''),
        reverse=True
    )
    return render_template('html/index.html', sessions=sorted_sessions, current_session_id=None, session_data={}, expert_mode=settings.get('expert_mode', False))

@app.route('/new_session')
def new_session_form():
    return render_template('html/new_session.html', settings=settings)

@app.route('/api/session/new', methods=['POST'])
def create_new_session_api():
    try:
        data = request.get_json()
        purpose = data.get('purpose')
        background = data.get('background')
        roles_str = data.get('roles', '')
        instruction = data.get('instruction')
        multi_step_reasoning_enabled = data.get('multi_step_reasoning_enabled', False)
        hyperparameters = data.get('hyperparameters')

        if not all([purpose, background, instruction]):
            return jsonify({"success": False, "message": "Purpose, background, and first instruction are required."}), 400
        
        roles = [r.strip() for r in roles_str.split(',') if r.strip()]

        session_id = history_manager.create_new_session(purpose, background, roles, multi_step_reasoning_enabled, hyperparameters=hyperparameters)
        
        import subprocess # Moved import here to be within the function scope if not already global
        command = ['python3', 'takt.py', '--session', session_id, '--instruction', instruction]
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

@app.route('/session/<session_id>')
def view_session(session_id):
    sessions_index = history_manager.list_sessions()
    if session_id not in sessions_index:
        abort(404)

    sorted_sessions = sorted(
        sessions_index.items(),
        key=lambda item: item[1].get('last_updated', ''),
        reverse=True
    )
    
    session_data = history_manager.get_session(session_id)
    if not session_data:
        abort(404)

    # Ensure hyperparameters key exists for older sessions
    if 'hyperparameters' not in session_data or not session_data['hyperparameters']:
        session_data['hyperparameters'] = settings.get('parameters', {})
        history_manager.edit_session_meta(session_id, {'hyperparameters': session_data['hyperparameters']})

    # Migrate references from list[str] to list[dict] if necessary
    if session_data.get('references') and isinstance(session_data['references'][0], str):
        session_data['references'] = [{'path': ref, 'disabled': False} for ref in session_data['references']]
        history_manager.update_references(session_id, session_data['references'])

    turns = session_data.get("turns", [])
    # Reverse the turns for display
    turns.reverse()
    
    current_session_purpose = session_data.get('purpose', 'Session')
    multi_step_reasoning_enabled = session_data.get('multi_step_reasoning_enabled', False)
    token_count = session_data.get('token_count', 0)
    context_limit = settings.get('context_limit', 1000000)

    expert_mode = settings.get('expert_mode', False)

    return render_template('html/index.html',
                           sessions=sorted_sessions,
                           current_session_id=session_id,
                           current_session_purpose=current_session_purpose,
                           session_data=session_data,
                           turns=turns,
                           multi_step_reasoning_enabled=multi_step_reasoning_enabled,
                           token_count=token_count,
                           context_limit=context_limit,
                           expert_mode=expert_mode)

# --- API Endpoints for Deletion ---

@app.route('/api/session/<session_id>', methods=['DELETE'])
def delete_session_api(session_id):
    try:
        history_manager.delete_session(session_id)
        return jsonify({"success": True, "message": f"Session {session_id} deleted."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/session/<session_id>/turn/<int:turn_index>', methods=['DELETE'])
def delete_turn_api(session_id, turn_index):
    try:
        # Since we reverse the turns for display, we need to convert the index back
        session_data = history_manager.get_session(session_id)
        if not session_data:
            return jsonify({"success": False, "message": "Session not found."}), 404
        
        original_length = len(session_data.get("turns", []))
        # The index from the frontend is for the reversed list
        index_to_delete = original_length - 1 - turn_index

        history_manager.delete_turn(session_id, index_to_delete)
        return jsonify({"success": True, "message": f"Turn {turn_index} from session {session_id} deleted."}), 200
    except IndexError:
        return jsonify({"success": False, "message": "Turn index out of range."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/<session_id>/turn/<int:turn_index>/edit', methods=['POST'])
def edit_turn_api(session_id, turn_index):
    try:
        new_data = request.get_json()
        if not new_data:
            return jsonify({"success": False, "message": "No data provided."}), 400

        # Since we reverse the turns for display, we need to convert the index back
        session_data = history_manager.get_session(session_id)
        if not session_data:
            return jsonify({"success": False, "message": "Session not found."}), 404
        
        original_length = len(session_data.get("turns", []))
        index_to_edit = original_length - 1 - turn_index

        history_manager.edit_turn(session_id, index_to_edit, new_data)
        return jsonify({"success": True, "message": f"Turn {turn_index} from session {session_id} updated."}), 200
    except IndexError:
        return jsonify({"success": False, "message": "Turn index out of range."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/<session_id>/meta/edit', methods=['POST'])
def edit_session_meta_api(session_id):
    try:
        new_meta_data = request.get_json()
        if not new_meta_data or not any(k in new_meta_data for k in ['purpose', 'background', 'multi_step_reasoning_enabled', 'token_count', 'hyperparameters']):
            return jsonify({"success": False, "message": "No data provided."}), 400

        history_manager.edit_session_meta(session_id, new_meta_data)
        return jsonify({"success": True, "message": f"Session {session_id} metadata updated."}), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/<session_id>/todos/edit', methods=['POST'])
def edit_todos_api(session_id):
    try:
        data = request.get_json()
        if 'todos' not in data:
            return jsonify({"success": False, "message": "No todos data provided."}), 400

        history_manager.update_todos(session_id, data['todos'])
        return jsonify({"success": True, "message": f"Session {session_id} todos updated."}), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/<session_id>/references/edit', methods=['POST'])
def edit_references_api(session_id):
    try:
        data = request.get_json()
        if 'references' not in data:
            return jsonify({"success": False, "message": "No references data provided."}), 400

        history_manager.update_references(session_id, data['references'])
        return jsonify({"success": True, "message": f"Session {session_id} references updated."}), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/<session_id>/todos', methods=['DELETE'])
def delete_todos_api(session_id):
    try:
        history_manager.delete_todos(session_id)
        return jsonify({"success": True, "message": f"Todos deleted from session {session_id}."}), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/<session_id>/fork/<int:fork_index>', methods=['POST'])
def fork_session_api(session_id, fork_index):
    try:
        new_session_id = history_manager.fork_session(session_id, fork_index)
        if new_session_id:
            return jsonify({"success": True, "new_session_id": new_session_id}), 200
        else:
            return jsonify({"success": False, "message": "Failed to fork session."}), 500
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Session not found."}), 404
    except IndexError:
        return jsonify({"success": False, "message": "Fork turn index out of range."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/<session_id>/instruction', methods=['POST'])
def send_instruction_api(session_id):
    from flask import Response, stream_with_context
    import subprocess
    import json

    try:
        new_data = request.get_json()
        instruction = new_data.get('instruction')
        if not instruction:
            return jsonify({"success": False, "message": "No instruction provided."}), 400

        session_data = history_manager.get_session(session_id)
        if not session_data:
            return jsonify({"success": False, "message": "Session not found."}), 404
        
        enable_multi_step_reasoning = session_data.get('multi_step_reasoning_enabled', False)

        command = ['python3', '-u', 'takt.py', '--session', session_id, '--instruction', instruction]
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

            # Stream stdout
            for line in iter(process.stdout.readline, ''):
                # SSE format: data: <content>\n\n
                yield f"data: {json.dumps({'content': line})}\n\n"
            
            process.stdout.close()
            stderr_output = process.stderr.read()
            process.stderr.close()
            
            return_code = process.wait()

            if return_code != 0:
                yield f"data: {json.dumps({'error': stderr_output})}\n\n"
            
            # Signal the end of the stream
            yield "event: end\ndata: \n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        # This part will catch errors before the stream starts
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    project_root_for_check = os.path.dirname(os.path.abspath(__file__))
    if check_and_show_warning(project_root_for_check):
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        sys.exit(1)
