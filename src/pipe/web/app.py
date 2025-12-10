import logging
import os
import sys
import zoneinfo

import yaml
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.utils.file import read_text_file, read_yaml_file
from pipe.web.actions.fs import (
    IndexFilesAction,
    LsAction,
    SearchL2Action,
)
from pipe.web.controllers import (
    SessionChatController,
    SessionManagementController,
    StartSessionController,
)
from pipe.web.dispatcher import dispatch_action, init_dispatcher
from pipe.web.routes import (
    bff_bp,
    fs_bp,
    meta_bp,
    session_bp,
    session_management_bp,
    session_tree_bp,
    settings_bp,
    turn_bp,
)
from pipe.web.service_container import get_container

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
):
    """
    Create and configure the Flask application.

    This factory function initializes all services and registers blueprints.
    Flask will auto-detect this function when running `flask run`.

    Args:
        init_index: Whether to initialize the Whoosh index on startup.

    Returns:
        The configured Flask application.
    """
    # Correctly determine the project root, which is three levels up from the
    # current script
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    # Define paths for templates and static assets relative to the corrected
    # project root
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
        # Log incoming requests for debugging
        try:
            logger.debug(f"Incoming {request.method} {request.path}")
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
    service_factory = ServiceFactory(project_root, settings)
    session_service = service_factory.create_session_service()
    session_management_service = service_factory.create_session_management_service()
    session_tree_service = service_factory.create_session_tree_service()
    session_workflow_service = service_factory.create_session_workflow_service()
    session_optimization_service = service_factory.create_session_optimization_service()
    session_reference_service = service_factory.create_session_reference_service()
    session_turn_service = service_factory.create_session_turn_service()
    session_meta_service = service_factory.create_session_meta_service()
    session_todo_service = service_factory.create_session_todo_service()
    file_indexer_service = service_factory.create_file_indexer_service()
    procedure_service = service_factory.create_procedure_service()
    role_service = service_factory.create_role_service()

    # BFF (Backend for Frontend) Controllers
    start_session_controller = StartSessionController(session_service, settings)
    session_chat_controller = SessionChatController(session_service, settings)
    session_management_controller = SessionManagementController(
        session_service, settings
    )

    # Initialize service container for dependency injection
    get_container().init(
        session_service=session_service,
        session_management_service=session_management_service,
        session_tree_service=session_tree_service,
        session_workflow_service=session_workflow_service,
        session_optimization_service=session_optimization_service,
        session_reference_service=session_reference_service,
        session_turn_service=session_turn_service,
        session_meta_service=session_meta_service,
        session_todo_service=session_todo_service,
        start_session_controller=start_session_controller,
        session_chat_controller=session_chat_controller,
        session_management_controller=session_management_controller,
        file_indexer_service=file_indexer_service,
        procedure_service=procedure_service,
        role_service=role_service,
        settings=settings,
        project_root=project_root,
    )

    # Initialize dispatcher with file indexer actions
    search_l2_action = SearchL2Action(file_indexer_service, {})
    ls_action = LsAction(file_indexer_service, {})
    index_files_action = IndexFilesAction(file_indexer_service, {})
    init_dispatcher(search_l2_action, ls_action, index_files_action)

    # Register blueprints (like Laravel route groups with prefixes)
    app.register_blueprint(session_bp)  # /api/v1/session/*
    app.register_blueprint(session_management_bp)  # /api/v1/session_management/*
    app.register_blueprint(meta_bp)  # /api/v1/session/<session_id>/meta/*
    app.register_blueprint(session_tree_bp)  # /api/v1/session_tree
    app.register_blueprint(turn_bp)  # /api/v1/session/<session_id>/turn/*
    app.register_blueprint(bff_bp)  # /api/v1/bff/*
    app.register_blueprint(fs_bp)  # /api/v1/fs/*
    app.register_blueprint(settings_bp)  # /api/v1/settings

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
            logger.error("Error in dispatch_action_endpoint", exc_info=True)
            return jsonify({"message": str(e)}), 500

    # Optionally rebuild Whoosh index on startup
    if init_index:
        try:
            logger.info("Rebuilding Whoosh index...")
            logger.debug(f"Base path: {file_indexer_service.repository.base_path}")
            logger.debug(f"Index dir: {file_indexer_service.repository.index_dir}")
            file_indexer_service.create_index()
            logger.info("Whoosh index rebuilt successfully")
            test_entries = file_indexer_service.get_ls_data([])
            logger.debug(f"Verified: {len(test_entries)} entries at root")
        except Exception as e:
            logger.warning(f"Failed to rebuild Whoosh index: {e}", exc_info=True)

    return app


if __name__ == "__main__":
    # Create application with index initialization
    app = create_app(init_index=True)

    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    project_root_for_check = os.path.dirname(os.path.abspath(__file__))
    if check_and_show_warning(project_root_for_check):
        app.run(host="0.0.0.0", port=5001, debug=False)
    else:
        sys.exit(1)
