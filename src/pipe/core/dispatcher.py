import sys

from pipe.core.models.session import Session
from pipe.core.services.session_service import SessionService
from pipe.core.models.args import TaktArgs

def dispatch_run(session_service: SessionService, args: TaktArgs):
    """
    Dispatches the execution to the correct delegate based on the api_mode.
    """
    api_mode = session_service.settings.api_mode
    settings = session_service.settings
    session_data = session_service.current_session
    project_root = session_service.project_root
    enable_multi_step_reasoning = session_data.multi_step_reasoning_enabled

    if args.dry_run:
        from .delegates import dry_run_delegate
        dry_run_delegate.run(
            settings,
            session_data,
            project_root,
            api_mode,
            enable_multi_step_reasoning
        )
        return None, None, []

    if api_mode == 'gemini-api':
        from .delegates import gemini_api_delegate
        return gemini_api_delegate.run(
            args,
            settings,
            session_data,
            project_root,
            api_mode,
            session_service.timezone_obj,
            enable_multi_step_reasoning,
            session_service,
            session_service.current_session_id
        )
    elif api_mode == 'gemini-cli':
        from .delegates import gemini_cli_delegate
        model_response_text = gemini_cli_delegate.run(
            args,
            settings,
            session_data,
            project_root,
            api_mode,
            enable_multi_step_reasoning
        )
        return model_response_text, None, []
    else:
        print(f"Error: Unknown api_mode '{api_mode}'. Please check setting.yml", file=sys.stderr)
        return None, None, []
