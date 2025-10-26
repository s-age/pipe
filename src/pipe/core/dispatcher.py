import sys

from pipe.core.models.session import Session
from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService
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

    # Instantiate the PromptService
    prompt_service = PromptService(project_root)

    if args.dry_run:
        from .delegates import dry_run_delegate
        dry_run_delegate.run(
            session_service,
            prompt_service
        )
        return None, None, []

    if api_mode == 'gemini-api':
        from .delegates import gemini_api_delegate
        return gemini_api_delegate.run(
            args,
            session_service,
            prompt_service
        )
    elif api_mode == 'gemini-cli':
        from .delegates import gemini_cli_delegate
        model_response_text = gemini_cli_delegate.run(
            args,
            session_service
        )
        return model_response_text, None, []
