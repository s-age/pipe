"""
Dispatches commands to the appropriate delegates based on arguments.
"""

import argparse
import json
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

    Transaction Flow:
    1. start_transaction(): user_instruction added to pools
    2. add_to_transaction(): agent outputs added to pools
    3. commit_transaction(): all changes persisted to turns
    4. rollback_transaction(): discard all changes on error
    """
    session_id = session_service.current_session_id

    api_mode = session_service.settings.api_mode
    settings = session_service.settings
    service_factory = ServiceFactory(
        session_service.project_root, session_service.settings
    )
    prompt_service = service_factory.create_prompt_service()
    reference_service = service_factory.create_session_reference_service()
    turn_service = service_factory.create_session_turn_service()
    meta_service = service_factory.create_session_meta_service()

    # 1. Concurrent execution check
    from pipe.core.services.process_manager_service import ProcessManagerService

    process_manager = ProcessManagerService(session_service.project_root)
    if process_manager.is_running(session_id):
        raise RuntimeError(f"Session {session_id} is already running")

    # 2. Register process
    process_manager.register_process(
        session_id, os.getpid(), args.instruction
    )

    # 3. Start streaming logger
    logger = service_factory.create_streaming_logger_service(session_id)
    logger.start_logging(args.instruction)

    # 4. Clean up old streaming logs
    from pipe.core.repositories.streaming_log_repository import StreamingLogRepository
    StreamingLogRepository.cleanup_old_logs(session_service.project_root)

    # For stream-json, also output to stdout
    stream_to_stdout = args.output_format == "stream-json"
    if stream_to_stdout:
        # Send initial instruction event
        print(
            json.dumps(
                {"type": "instruction", "content": args.instruction}, ensure_ascii=False
            ),
            flush=True,
        )

    try:
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
            logger.close()
            process_manager.cleanup_process(session_id)
            return

        # Decrement TTL for all active references before calling the delegate
        reference_service.decrement_all_references_ttl_in_session(session_id)
        turn_service.expire_old_tool_responses(session_id)

        # 5. Start transaction (add user_instruction to pools)
        turn_service.start_transaction(session_id, args.instruction)
        logger.log_event({"type": "transaction", "action": "start"})

        # 6. Execute agent
        AgentClass = get_agent_class(api_mode)
        agent_instance = AgentClass()

        # Use streaming mode for stream-json output format
        used_stream_mode = False
        if stream_to_stdout and hasattr(agent_instance, "run_stream"):
            # Stream mode: yield chunks in real-time
            used_stream_mode = True
            model_response_text = ""
            token_count = None
            turns_to_save = []

            for stream_item in agent_instance.run_stream(
                args, session_service, prompt_service
            ):
                # Check if this is the final tuple (ends with "end")
                if isinstance(stream_item, tuple) and stream_item[0] == "end":
                    _, model_response_text, token_count, turns_to_save = stream_item
                else:
                    # Intermediate string chunk - output to stdout
                    print(
                        json.dumps(
                            {"type": "chunk", "content": str(stream_item)},
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
        else:
            # Non-streaming mode: get complete response
            model_response_text, token_count, turns_to_save = agent_instance.run(
                args, session_service, prompt_service
            )

        # 7. Add all turns to transaction (temporary storage in pools)
        for turn in turns_to_save:
            turn_service.add_to_transaction(session_id, turn)
            # Log chunks for streaming visibility (truncate if too long)
            if hasattr(turn, "content") and turn.content:
                content_preview = turn.content[:200]
                if len(turn.content) > 200:
                    content_preview += "..."
                logger.log_chunk(content_preview)

                # Stream to stdout if stream-json mode (only if not already streamed)
                if stream_to_stdout and not used_stream_mode:
                    print(
                        json.dumps(
                            {"type": "content", "content": turn.content},
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )

        # 8. Commit transaction (merge pools into turns for persistence)
        turn_service.commit_transaction(session_id)
        logger.log_event({"type": "transaction", "action": "commit"})

        # 9. Update token count
        if token_count is not None:
            meta_service.update_token_count(session_id, token_count)

        # 10. Cleanup
        logger.close()
        process_manager.cleanup_process(session_id)

        # 11. Output
        if args.output_format == "json":
            output = {
                "session_id": session_id,
                "response": model_response_text,
                "token_count": token_count,
            }
            print(json.dumps(output, ensure_ascii=False))
        elif args.output_format == "stream-json":
            # Send completion event (without response text, already streamed)
            output = {
                "type": "complete",
                "session_id": session_id,
                "token_count": token_count,
            }
            print(json.dumps(output, ensure_ascii=False), flush=True)
        elif args.output_format == "text":
            print(model_response_text)
            print(
                f"\nSuccessfully added response to session {session_id}.\n",
                file=sys.stderr,
            )

    except Exception as e:
        # Rollback transaction on error (discard all changes in pools)
        logger.log_error(str(e))
        logger.log_event({"type": "transaction", "action": "rollback"})
        logger.close()

        turn_service.rollback_transaction(session_id)
        process_manager.cleanup_process(session_id)

        # Stream error if stream-json mode
        if stream_to_stdout:
            print(
                json.dumps({"type": "error", "error": str(e)}, ensure_ascii=False),
                flush=True,
            )

        raise


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
        print(json.dumps(result, ensure_ascii=False))

    elif args.instruction:
        session_service.prepare(args, is_dry_run=args.dry_run)
        _dispatch_run(args, session_service)

    else:
        from .delegates import help_delegate

        help_delegate.run(parser)
