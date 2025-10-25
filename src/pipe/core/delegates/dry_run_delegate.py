from pipe.core.token_manager import TokenManager
from pipe.core.prompt_builder import PromptBuilder
from pipe.core.gemini_api import load_tools

from pipe.core.models.session import Session

def run(settings, session_data: Session, project_root, api_mode, enable_multi_step_reasoning):
    """The delegate function for running in dry-run mode."""
    print("\n--- Dry Run Mode ---")
    token_manager = TokenManager(settings=settings)
    builder = PromptBuilder(
        settings=settings,
        session_data=session_data,
        project_root=project_root,
        api_mode=api_mode,
        multi_step_reasoning_enabled=enable_multi_step_reasoning
    )
    
    json_prompt_str = builder.build()

    tools = load_tools(project_root)

    token_count = token_manager.count_tokens(json_prompt_str, tools=tools)
    is_within_limit, message = token_manager.check_limit(token_count)
    print(f"Token Count: {message}")
    if not is_within_limit:
        print("WARNING: Prompt exceeds context window limit.")

    # For dry run, we print the JSON string that would be sent to the API
    print(json_prompt_str)
    
    print("\n--- End of Dry Run ---")

