import sys

from pipe.core.models.session import Session

def dispatch_run(api_mode, args, settings, session_data: Session, project_root, enable_multi_step_reasoning, session_service):
    """
    Dispatches the execution to the correct delegate based on the api_mode.
    """
    if args.dry_run:
        from .delegates import dry_run_delegate
        dry_run_delegate.run(
            settings,
            session_data,
            project_root,
            api_mode,
            enable_multi_step_reasoning
        )
        return None, None # Dry run execution stops here

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
            args.session
        )
    elif api_mode == 'gemini-cli':
        from .delegates import gemini_cli_delegate
        # The CLI delegate returns only the response text, not a token count tuple.
        model_response_text = gemini_cli_delegate.run(
            args,
            settings,
            session_data,
            project_root,
            api_mode,
            enable_multi_step_reasoning
        )
        return model_response_text, None, [] # Return as a tuple of three to match the api delegate's signature
    else:
        print(f"Error: Unknown api_mode '{api_mode}'. Please check setting.yml", file=sys.stderr)
        # Return a tuple to avoid unpacking errors in the calling function
        return None, None
