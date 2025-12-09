"""
Dispatches commands to the appropriate delegates based on arguments.
"""

import argparse
import os
import sys

from pipe.core.agents import get_agent_class
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

    # For gemini-api mode, treat stream-json as json since API already streams
    if api_mode == "gemini-api" and args.output_format == "stream-json":
        args.output_format = "json"

    settings = session_service.settings
    service_factory = ServiceFactory(
        session_service.project_root, session_service.settings
    )
    prompt_service = service_factory.create_prompt_service()
    reference_service = service_factory.create_session_reference_service()
    turn_service = service_factory.create_session_turn_service()
    meta_service = service_factory.create_session_meta_service()

    # Calculate token count for text output
    try:
        prompt_model = prompt_service.build_prompt(session_service)
        from jinja2 import Environment, FileSystemLoader
        from pipe.core.agents.gemini_api import load_tools
        from pipe.core.services.token_service import TokenService

        token_service = TokenService(settings=settings)
        tools = load_tools(session_service.project_root)
        template_env = Environment(
            loader=FileSystemLoader(
                os.path.join(session_service.project_root, "templates", "prompt")
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = template_env.get_template("gemini_api_prompt.j2")
        context = prompt_model.model_dump()
        api_contents_string = template.render(session=context)
        prompt_token_count = token_service.count_tokens(
            api_contents_string, tools=tools
        )
        is_within_limit, message = token_service.check_limit(prompt_token_count)
        if not is_within_limit:
            raise ValueError("Prompt exceeds context window limit. Aborting.")

        if args.output_format == "text":
            print(f"Token Count: {message}", file=sys.stderr)
    except Exception:
        # Skip token count calculation if template not found (e.g., in tests)
        pass

    if args.dry_run:
        from .delegates import dry_run_delegate

        dry_run_delegate.run(session_service, prompt_service)
        return

    # Decrement TTL for all active references before calling the delegate
    reference_service.decrement_all_references_ttl_in_session(session_id)
    turn_service.expire_old_tool_responses(session_id)

    # ----------------------------------------------------
    # NEW REGISTRY-BASED DISPATCH LOGIC
    # ----------------------------------------------------

    # 1. Get the agent class from the registry based on api_mode
    AgentClass = get_agent_class(api_mode)

    # 2. Instantiate and execute (polymorphism - no branching needed)
    agent_instance = AgentClass()
    model_response_text, token_count, turns_to_save = agent_instance.run(
        args, session_service, prompt_service
    )

    # ----------------------------------------------------

    for turn in turns_to_save:
        turn_service.add_turn_to_session(session_id, turn)

    if token_count is not None:
        meta_service.update_token_count(session_id, token_count)

    if args.output_format == "json":
        import json

        output = {
            "session_id": session_id,
            "response": model_response_text,
            "token_count": token_count,
        }
        print(json.dumps(output, ensure_ascii=False))
    elif args.output_format == "text":
        print(model_response_text)
        print(
            f"\nSuccessfully added response to session {session_id}.\n", file=sys.stderr
        )


def dispatch(
    args: TaktArgs, session_service: SessionService, parser: argparse.ArgumentParser
):
    """
    Acts as the main router for the application's command flow.
    """
    if args.fork:
        from .delegates import fork_delegate

        fork_delegate.run(args, session_service.project_root, session_service.settings)

    elif args.therapist:
        # Run therapist diagnosis
        result = session_service.run_takt_for_therapist(args.therapist)
        import json

        print(json.dumps(result, ensure_ascii=False))

    elif args.instruction:
        session_service.prepare(args, is_dry_run=args.dry_run)
        _dispatch_run(args, session_service)

    else:
        from .delegates import help_delegate

        help_delegate.run(parser)
