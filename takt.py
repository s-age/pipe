import argparse
import os
import sys
import json
import warnings
from pydantic.warnings import ArbitraryTypeWarning

warnings.filterwarnings("ignore", category=ArbitraryTypeWarning)
from src.utils import read_yaml_file, read_text_file
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
from src.utils.datetime import get_current_timestamp
from src.dispatcher import dispatch_run

def check_and_show_warning(project_root: str) -> bool:
    """Checks for the warning file, displays it, and gets user consent."""
    sealed_path = os.path.join(project_root, "sealed.txt")
    unsealed_path = os.path.join(project_root, "unsealed.txt")

    if os.path.exists(unsealed_path):
        return True  # Already agreed

    warning_content = read_text_file(sealed_path)
    if not warning_content:
        return True  # No warning file or empty file, proceed

    print("--- IMPORTANT NOTICE ---")
    print(warning_content)
    print("------------------------")

    while True:
        try:
            response = input("Do you agree to the terms above? (yes/no): ").lower().strip()
            if response == "yes":
                os.rename(sealed_path, unsealed_path)
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



def _run(args, settings, session_manager, session_data_for_prompt, project_root, api_mode, enable_multi_step_reasoning):
    model_response_text = ""
    # The index of the user_task turn just added.
    new_turns_start_index = len(session_data_for_prompt['turns']) - 1

    try:
        model_response_text, token_count = dispatch_run(
            api_mode,
            args,
            settings,
            session_data_for_prompt,
            project_root,
            enable_multi_step_reasoning,
            session_manager
        )
        if model_response_text is None and token_count is None: # Error case from dispatcher
            return

        # The empty response check is now universal for any delegate that might return empty text
        if not model_response_text or not model_response_text.strip():
            model_response_text = "API Error: Model stream ended with empty response text."

    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        session_data_for_prompt['turns'].pop()
        return

    session_id = args.session

    # Collect all pieces of the turn history for this run
    # 1. The user_task from the in-memory session data
    all_new_turns_in_memory = session_data_for_prompt['turns'][new_turns_start_index:]
    user_turn = next((t for t in all_new_turns_in_memory if t.get('type') == 'user_task'), None)

    # 2. The tool-related turns from the pool on disk
    pooled_turns = session_manager.history_manager.get_and_clear_pool(session_id)
    
    # 3. The final model response
    final_model_turn = {"type": "model_response", "content": model_response_text, "timestamp": get_current_timestamp(session_manager.local_tz)}

    # Filter and order the turns according to the desired sequence
    turns_to_save = []
    if user_turn:
        turns_to_save.append(user_turn)

    # Add tool calls from the pool
    tool_call_turns = [t for t in pooled_turns if t.get('type') in ['function_calling', 'tool_response']]
    turns_to_save.extend(tool_call_turns)

    # Add the final model response
    turns_to_save.append(final_model_turn)

    # Add any model responses from the pool (e.g., from verify_summary)
    pooled_model_turns = [t for t in pooled_turns if t.get('type') == 'model_response']
    turns_to_save.extend(pooled_model_turns)

    # Now, save all the collected and ordered turns to the session file
    for turn in turns_to_save:
        # The final model turn is the only one that should update the token count
        current_token_count = token_count if turn is final_model_turn else None
        session_manager.add_turn_to_session(session_id, turn, current_token_count)

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
    parser.add_argument('--fork', type=str, metavar='SESSION_ID', help='The ID of the session to fork.')
    parser.add_argument('--at-turn', type=int, metavar='TURN_INDEX', help='The 1-based turn number to fork from. Required with --fork.')
    parser.add_argument('--api-mode', type=str, help='Specify the API mode (e.g., gemini-api, gemini-cli).')
    
    args = parser.parse_args()
    return args, parser

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    if not check_and_show_warning(project_root):
        sys.exit(1)

    load_dotenv()
    config_path = os.path.join(project_root, 'setting.yml')
    settings = read_yaml_file(config_path)
    
    args, parser = _parse_arguments()

    api_mode = settings.get('api_mode')
    if not api_mode:
        raise ValueError("'api_mode' not found in setting.yml")
    
    session_manager = SessionManager(os.path.join(project_root, 'sessions'))

    if args.fork:
        if not args.at_turn:
            print("Error: --at-turn is required when using --fork.", file=sys.stderr)
            sys.exit(1)
        try:
            # Convert 1-based turn number to 0-based index
            fork_index = args.at_turn - 1
            new_session_id = session_manager.history_manager.fork_session(args.fork, fork_index)
            print(f"Successfully forked session {args.fork} at turn {args.at_turn}.")
            print(f"New session created: {new_session_id}")
        except (FileNotFoundError, IndexError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

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
