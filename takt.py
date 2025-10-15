import argparse
import os
import sys
import json
from pathlib import Path
from src.utils import read_yaml_file
from dotenv import load_dotenv
from datetime import datetime, timezone
import zoneinfo
import importlib
import inspect

from src.session_manager import SessionManager
from src.gemini_api import call_gemini_api, load_tools
from src.gemini_cli import call_gemini_cli
from src.prompt_builder import PromptBuilder
from src.token_manager import TokenManager

def check_and_show_warning(project_root: Path) -> bool:
    """Checks for the warning file, displays it, and gets user consent."""
    sealed_path = project_root / "sealed.txt"
    unsealed_path = project_root / "unsealed.txt"

    if unsealed_path.exists():
        return True  # Already agreed

    if not sealed_path.exists():
        return True  # No warning file, proceed

    print("--- IMPORTANT NOTICE ---")
    print(sealed_path.read_text(encoding="utf-8"))
    print("------------------------")

    while True:
        try:
            response = input("Do you agree to the terms above? (yes/no): ").lower().strip()
            if response == "yes":
                sealed_path.rename(unsealed_path)
                print("Thank you. Proceeding...")
                return True
            elif response == "no":
                print("You must agree to the terms to use this tool. Exiting.")
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled. Exiting.")
            return False



def execute_tool_call(tool_call, session_manager, session_id):
    """Dynamically imports and executes a tool function, passing context if needed."""
    tool_name = tool_call.name
    tool_args = dict(tool_call.args)
    
    print(f"Tool call: {tool_name}({tool_args})")

    try:
        tool_module = importlib.import_module(f"tools.{tool_name}")
        importlib.reload(tool_module)  # Force reload to get the latest code
        tool_function = getattr(tool_module, tool_name)
        
        # Inspect the tool function's signature
        sig = inspect.signature(tool_function)
        params = sig.parameters
        
        # Prepare the arguments to pass
        final_args = tool_args.copy()
        
        if 'session_manager' in params:
            final_args['session_manager'] = session_manager
        if 'session_id' in params and 'session_id' not in tool_args:
            final_args['session_id'] = session_id

        result = tool_function(**final_args)
        return result
    except Exception as e:
        return {"error": f"Failed to execute tool {tool_name}: {e}"}

def _compress(session_manager, args):
    print("Compression logic not fully implemented in this refactor.")
    pass

def _dry_run(settings, session_data_for_prompt, project_root, api_mode, enable_multi_step_reasoning):
    print("\n--- Dry Run Mode ---")
    token_manager = TokenManager(settings=settings)
    builder = PromptBuilder(
        settings=settings,
        session_data=session_data_for_prompt,
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

def _run_api(args, settings, session_data_for_prompt, project_root, api_mode, local_tz, enable_multi_step_reasoning, session_manager, session_id):
    model_response_text = ""
    token_count = 0  # Initialize token_count
    while True:
        response = call_gemini_api(
            settings=settings,
            session_data=session_data_for_prompt,
            project_root=project_root,
            instruction=args.instruction,
            api_mode=api_mode,
            multi_step_reasoning_enabled=enable_multi_step_reasoning
        )

        # Capture token_count from the API call
        token_count = response.usage_metadata.prompt_token_count + response.usage_metadata.candidates_token_count

        function_call = None
        try:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    break  # Found the first function call
        except (IndexError, AttributeError):
            function_call = None

        if not function_call:
            model_response_text = response.text
            break

        # Format the function call into a readable string
        args_json_string = json.dumps(dict(function_call.args), ensure_ascii=False)
        response_string = f"{function_call.name}({args_json_string})"

        model_turn = {
            "type": "function_calling",
            "response": response_string,
            "timestamp": datetime.now(local_tz).isoformat()
        }
        session_data_for_prompt['turns'].append(model_turn)

        tool_result = execute_tool_call(function_call, session_manager, session_id)
        
        # After a tool call, session data on disk (like references) might have changed.
        # We need to update our in-memory session_data_for_prompt to reflect those changes
        # before building the next prompt.
        reloaded_session_data = session_manager.history_manager.get_session(session_id)
        if reloaded_session_data:
            # Update references if they exist in the reloaded data
            if 'references' in reloaded_session_data:
                session_data_for_prompt['references'] = reloaded_session_data['references']
            # Potentially update other session state modified by tools in the future

        # Reformat the tool_result to include a status
        if isinstance(tool_result, dict) and 'error' in tool_result:
            formatted_response = {
                "status": "failed",
                "message": tool_result['error']
            }
        else:
            # If the result is a dict and has a 'message' key, use that.
            if isinstance(tool_result, dict) and 'message' in tool_result:
                message_content = tool_result['message']
            # Otherwise, use the whole tool_result as the content.
            else:
                message_content = tool_result

            formatted_response = {
                "status": "succeeded",
                "message": message_content
            }

        tool_turn = {
            "type": "tool_response",
            "name": function_call.name,
            "response": formatted_response,
            "timestamp": datetime.now(local_tz).isoformat()
        }
        session_data_for_prompt['turns'].append(tool_turn)
    return model_response_text, token_count

def _run_cli(args, settings, session_data_for_prompt, project_root, api_mode, enable_multi_step_reasoning):
    response = call_gemini_cli(
        settings=settings,
        session_data=session_data_for_prompt,
        project_root=project_root,
        instruction=args.instruction,
        api_mode=api_mode,
        multi_step_reasoning_enabled=enable_multi_step_reasoning
    )
    return response.text

def _run(args, settings, session_manager, session_data_for_prompt, project_root, api_mode, enable_multi_step_reasoning):
    model_response_text = ""
    # The index of the user_task turn just added.
    new_turns_start_index = len(session_data_for_prompt['turns']) - 1

    try:
        if api_mode == 'gemini-api':
            print("\nExecuting with Gemini API...")
            model_response_text, token_count = _run_api(args, settings, session_data_for_prompt, project_root, api_mode, session_manager.local_tz, enable_multi_step_reasoning, session_manager, args.session)
        elif api_mode == 'gemini-cli':
            model_response_text = _run_cli(args, settings, session_data_for_prompt, project_root, api_mode, enable_multi_step_reasoning)
            token_count = None # CLI mode doesn't track token count in the same way
        else:
            print(f"Error: Unknown api_mode '{api_mode}'. Please check setting.yml", file=sys.stderr)
            return

    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        session_data_for_prompt['turns'].pop()
        return

    session_id = args.session
    
    # Get the new turns generated during this run (user_task + api_turns)
    new_turns = session_data_for_prompt['turns'][new_turns_start_index:]

    # Save only the new turns
    for turn in new_turns:
        session_manager.add_turn_to_session(session_id, turn)

    final_response_data = {"type": "model_response", "content": model_response_text, "timestamp": datetime.now(session_manager.local_tz).isoformat()}
    session_manager.add_turn_to_session(session_id, final_response_data, token_count)

    print("--- Response Received ---")
    print(model_response_text)
    print("-------------------------\n")
    print(f"Successfully added response to session {session_id}.")

def _help(parser):
    parser.print_help()

def _parse_arguments():
    parser = argparse.ArgumentParser(description="A task-oriented chat agent for context engineering.")
    parser.add_argument('--compress', action='store_true', help='Compress the history of a session into a summary.')
    parser.add_argument('--dry-run', action='store_true', help='Build and print the prompt without executing.')
    parser.add_argument('--session', type=str, help='The ID of the session to continue, edit, or compress.')
    parser.add_argument('--purpose', type=str, help='The overall purpose of the new session.')
    parser.add_argument('--background', type=str, help='The background context for the new session.')
    parser.add_argument('--roles', type=str, help='Comma-separated paths to role files for the new session.')
    parser.add_argument('--instruction', type=str, help='The specific instruction for the current task.')
    parser.add_argument('--multi-step-reasoning', action='store_true', help='Include multi-step reasoning process in the prompt.')
    
    args = parser.parse_args()
    return args, parser

def main():
    project_root = Path(__file__).parent
    if not check_and_show_warning(project_root):
        sys.exit(1)

    load_dotenv()
    config_path = project_root / 'setting.yml'
    settings = read_yaml_file(config_path)
    
    api_mode = settings.get('api_mode')
    if not api_mode:
        raise ValueError("'api_mode' not found in setting.yml")



    args, parser = _parse_arguments()
    
    session_manager = SessionManager(project_root / 'sessions')

    if args.compress:
        _compress(session_manager, args)

    elif args.instruction:
        session_id = args.session
        roles = args.roles.split(',') if args.roles else []
        enable_multi_step_reasoning = args.multi_step_reasoning

        session_data_for_prompt = session_manager.get_or_create_session_data(
            session_id=session_id,
            purpose=args.purpose,
            background=args.background,
            roles=roles,
            multi_step_reasoning_enabled=enable_multi_step_reasoning,
            instruction=args.instruction,
            local_tz=session_manager.local_tz
        )

        if args.dry_run:
            _dry_run(settings, session_data_for_prompt, project_root, api_mode, enable_multi_step_reasoning)
            return

        # If not a dry run, proceed with session creation/continuation and execution
        if not session_id:
            # Create new session first if it doesn't exist
            if not all([args.purpose, args.background]):
                raise ValueError("A new session requires --purpose and --background for the first instruction.")
            session_id = session_manager.create_new_session(
                purpose=args.purpose,
                background=args.background,
                roles=roles,
                multi_step_reasoning_enabled=enable_multi_step_reasoning
            )
            args.session = session_id # Ensure args is updated for subsequent calls
            print(f"Conductor Agent: Creating new session...\nNew session created: {session_id}")
        else:
            print(f"Conductor Agent: Continuing session: {session_id}")

        _run(args, settings, session_manager, session_data_for_prompt, project_root, api_mode, enable_multi_step_reasoning)

    else:
        _help(parser)

if __name__ == "__main__":
    main()
