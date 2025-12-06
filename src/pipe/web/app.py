import os
import sys
import zoneinfo

import yaml
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.utils.file import read_text_file, read_yaml_file
from pipe.web.actions.file_search_actions import (
    IndexFilesAction,
    LsAction,
    SearchL2Action,
)
from pipe.web.controllers import SessionDetailController
from pipe.web.dispatcher import dispatch_action, init_dispatcher
from pipe.web.routes import bff_bp, pages_bp, search_bp, session_bp, settings_bp
from pipe.web.service_container import get_container


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


def create_app(
    init_index: bool = True,
) -> Flask:
    """Create and configure the Flask application.

    This factory function initializes all services and registers blueprints.
    Flask will auto-detect this function when running `flask run`.

    Args:
        init_index: Whether to initialize the Whoosh index on startup.

    Returns:
        The configured Flask application.
    """
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

    # Load settings
    config_path = os.path.join(project_root, "setting.yml")
    settings_dict = load_settings(config_path)
    settings = Settings(**settings_dict)

    tz_name = settings.timezone
    try:
        zoneinfo.ZoneInfo(tz_name)
    except zoneinfo.ZoneInfoNotFoundError:
        print(
            f"Warning: Timezone '{tz_name}' from setting.yml not found. Using UTC.",
            file=sys.stderr,
        )

    # Initialize services
    session_service = ServiceFactory(project_root, settings).create_session_service()
    session_management_service = ServiceFactory(
        project_root, settings
    ).create_session_management_service()
    file_indexer_service = ServiceFactory(
        project_root, settings
    ).create_file_indexer_service()

    # BFF (Backend for Frontend) Controllers
    session_detail_controller = SessionDetailController(session_service, settings)

    # Initialize service container for dependency injection
    get_container().init(
        session_service=session_service,
        session_management_service=session_management_service,
        session_detail_controller=session_detail_controller,
        file_indexer_service=file_indexer_service,
        settings=settings,
        project_root=project_root,
    )

    # Initialize dispatcher with file indexer actions
    search_l2_action = SearchL2Action(file_indexer_service, {})
    ls_action = LsAction(file_indexer_service, {})
    index_files_action = IndexFilesAction(file_indexer_service, {})
    init_dispatcher(search_l2_action, ls_action, index_files_action)

    # Register blueprints (like Laravel route groups with prefixes)
    app.register_blueprint(pages_bp)      # HTML pages (no prefix)
    app.register_blueprint(session_bp)    # /api/v1/session/*
    app.register_blueprint(bff_bp)        # /api/v1/bff/*
    app.register_blueprint(search_bp)     # /api/v1/search*, /api/v1/ls, etc.
    app.register_blueprint(settings_bp)   # /api/v1/settings

    # Catch-all dispatcher for any unmatched /api/v1/* routes
    @app.route(
        "/api/v1/<path:action>", methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
    )
    def dispatch_action_endpoint(action: str):
        """
        Central dispatcher for v1 API endpoints not handled by specific blueprints.
        Routes actions to appropriate handlers via dispatch_action().
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

    # Optionally rebuild Whoosh index on startup
    if init_index:
        try:
            print("Rebuilding Whoosh index...")
            print(f"  Base path: {file_indexer_service.repository.base_path}")
            print(f"  Index dir: {file_indexer_service.repository.index_dir}")
            file_indexer_service.create_index()
            print("Whoosh index rebuilt successfully")
            test_entries = file_indexer_service.get_ls_data([])
            print(f"  Verified: {len(test_entries)} entries at root")
        except Exception as e:
            print(f"WARNING: Failed to rebuild Whoosh index: {e}")
            import traceback
            traceback.print_exc()

    return app


if __name__ == "__main__":
    # Create application with index initialization
    app = create_app(init_index=True)

    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
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

            from pipe.web.service_container import get_session_service

            print(f"DEBUG: module project_root = {project_root}")
            print(f"DEBUG: current working dir = {_os.getcwd()}")
            # session_service created at module import; print its repository path
            session_service = get_session_service()
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
