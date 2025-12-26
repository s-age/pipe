from pipe.core.agents.gemini_cli import call_gemini_cli
from pipe.core.domains import gemini_token_count
from pipe.core.domains.gemini_cli_payload import GeminiCliPayloadBuilder
from pipe.core.models.args import TaktArgs
from pipe.core.services.gemini_tool_service import GeminiToolService
from pipe.core.services.session_service import SessionService
from pipe.core.services.session_turn_service import SessionTurnService


def run(
    args: TaktArgs,
    session_service: SessionService,
    session_turn_service: SessionTurnService,
) -> tuple[str, int, dict | None]:
    """
    Handles the logic for the 'gemini-cli' mode by delegating to call_gemini_cli.
    This function is now only responsible for getting the model's response text.
    """
    # Build the prompt once using GeminiCliPayloadBuilder
    # This prompt will be used for both token counting and the API call
    payload_builder = GeminiCliPayloadBuilder(
        project_root=session_service.project_root,
        api_mode=session_service.settings.api_mode,
    )
    rendered_prompt = payload_builder.build(session_service)

    # Calculate token count from the complete prompt (including all turns)
    # Load tools
    tool_service = GeminiToolService()
    tools = tool_service.load_tools(session_service.project_root)

    # Create tokenizer and count tokens
    tokenizer = gemini_token_count.create_local_tokenizer(
        session_service.settings.model.name
    )
    token_count = gemini_token_count.count_tokens(
        rendered_prompt, tools=tools, tokenizer=tokenizer
    )

    # Call the agent with the pre-built prompt
    # This eliminates redundant prompt construction
    result = call_gemini_cli(
        session_service, args.output_format, prompt=rendered_prompt
    )
    response_text = result.get("response", "")
    stats = result.get("stats")

    # For stream-json, response_text is empty, collect from the streamed output
    if args.output_format == "stream-json":
        # The response is already streamed, collect the assistant messages
        # For simplicity, assume response_text is collected in call_gemini_cli
        pass

    # Merge any tool calls that occurred during the subprocess execution from the pool
    # into the main turns history before the final model response is added.
    if session_service.current_session_id:
        # CRITICAL: Reload the session from disk. The 'gemini' subprocess, running
        # mcp_server, has modified the session file by adding tool calls to the pool.
        # We must reload it here to get the latest state before merging.
        session_id = session_service.current_session_id
        session_service.current_session = session_service.get_session(session_id)

        session_turn_service.merge_pool_into_turns(session_id)

    return response_text, token_count, stats
