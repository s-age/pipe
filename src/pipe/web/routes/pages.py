"""HTML page routes.

Handles all HTML page rendering endpoints.
"""

import json

from flask import Blueprint, abort, render_template

from pipe.web.service_container import get_session_service, get_settings

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Render the index page."""
    session_service = get_session_service()
    settings = get_settings()

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


@pages_bp.route("/start_session")
def start_session_form():
    """Render the start session form page."""
    session_service = get_session_service()
    settings = get_settings()

    sessions_collection = session_service.list_sessions()
    sorted_sessions = sessions_collection.get_sorted_by_last_updated()
    return render_template(
        "html/start_session.html",
        settings=settings.model_dump(),
        sessions=sorted_sessions,
    )


@pages_bp.route("/session/<path:session_id>")
def view_session(session_id):
    """Render the session view page."""
    session_service = get_session_service()
    settings = get_settings()

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
