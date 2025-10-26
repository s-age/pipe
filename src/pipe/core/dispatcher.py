"""
Dispatches commands to the appropriate delegates based on arguments.
"""
import argparse
import sys
from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService

def _dispatch_run(args: TaktArgs, session_service: SessionService):
    """
    Private function to handle the actual run dispatch based on api_mode.
    This logic was previously in the old dispatch_run and _run functions.
    """
    session_id = session_service.current_session_id
    if session_id:
        pool = session_service.get_pool(session_id)
        if pool and len(pool) >= 7:
            print(f"Warning: The number of items in the session pool ({len(pool)}) has reached the limit (7). Halting further processing.", file=sys.stderr)
            return

    api_mode = session_service.settings.api_mode
    prompt_service = PromptService(session_service.project_root)

    if args.dry_run:
        from .delegates import dry_run_delegate
        dry_run_delegate.run(session_service, prompt_service)
        return

    # Decrement TTL for all active references before calling the delegate
    session_service.decrement_all_references_ttl_in_session(session_id)

    token_count = 0
    turns_to_save = []

    if api_mode == 'gemini-api':
        from .delegates import gemini_api_delegate
        _, token_count, turns_to_save = gemini_api_delegate.run(args, session_service, prompt_service)
    elif api_mode == 'gemini-cli':
        from .delegates import gemini_cli_delegate
        from pipe.core.models.turn import ModelResponseTurn
        from pipe.core.utils.datetime import get_current_timestamp
        model_response_text = gemini_cli_delegate.run(args, session_service)
        final_turn = ModelResponseTurn(
            type="model_response",
            content=model_response_text,
            timestamp=get_current_timestamp(session_service.timezone_obj)
        )
        turns_to_save = [final_turn]
    else:
        raise ValueError(f"Error: Unknown api_mode '{api_mode}'.")

    for turn in turns_to_save:
        session_service.add_turn_to_session(session_id, turn)

    if token_count is not None:
        session_service.update_token_count(session_id, token_count)

    print(f"\nSuccessfully added response to session {session_id}.\n", file=sys.stderr)
    print("\n", flush=True)
    print("event: end", flush=True)

def dispatch(args: TaktArgs, session_service: SessionService, parser: argparse.ArgumentParser):
    """
    Acts as the main router for the application's command flow.
    """
    if args.fork:
        from .delegates import fork_delegate
        fork_delegate.run(args, session_service)
    
    elif args.instruction:
        session_service.prepare_session_for_takt(args, is_dry_run=args.dry_run)
        _dispatch_run(args, session_service)

    else:
        from .delegates import help_delegate
        help_delegate.run(parser)