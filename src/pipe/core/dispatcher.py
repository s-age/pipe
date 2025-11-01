"""
Dispatches commands to the appropriate delegates based on arguments.
"""

import argparse
import sys

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService


def _dispatch_run(args: TaktArgs, session_service: SessionService):
    """
    Private function to handle the actual run dispatch based on api_mode.
    This logic was previously in the old dispatch_run and _run functions.
    """
    session_id = session_service.current_session_id

    api_mode = session_service.settings.api_mode
    service_factory = ServiceFactory(
        session_service.project_root, session_service.settings
    )
    prompt_service = service_factory.create_prompt_service()

    if args.dry_run:
        from .delegates import dry_run_delegate

        dry_run_delegate.run(session_service, prompt_service)
        return

    # Decrement TTL for all active references before calling the delegate
    session_service.decrement_all_references_ttl_in_session(session_id)
    session_service.expire_old_tool_responses(session_id)

    token_count = 0
    turns_to_save = []

    if api_mode == "gemini-api":
        from .delegates import gemini_api_delegate

        _, token_count, turns_to_save = gemini_api_delegate.run(
            args, session_service, prompt_service
        )
    elif api_mode == "gemini-cli":
        from pipe.core.models.turn import ModelResponseTurn
        from pipe.core.utils.datetime import get_current_timestamp

        from .delegates import gemini_cli_delegate

        # Explicitly merge any tool calls from the pool into the main turns history
        # before calling the agent.
        session_service.merge_pool_into_turns(session_id)

        model_response_text = gemini_cli_delegate.run(args, session_service)
        print(model_response_text)
        final_turn = ModelResponseTurn(
            type="model_response",
            content=model_response_text,
            timestamp=get_current_timestamp(session_service.timezone_obj),
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


def dispatch(
    args: TaktArgs, session_service: SessionService, parser: argparse.ArgumentParser
):
    """
    Acts as the main router for the application's command flow.
    """
    if args.fork:
        from .delegates import fork_delegate

        fork_delegate.run(args, session_service)

    elif args.instruction:
        session_service.prepare(args, is_dry_run=args.dry_run)
        _dispatch_run(args, session_service)

    else:
        from .delegates import help_delegate

        help_delegate.run(parser)
