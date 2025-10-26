import argparse
import os
import sys
import json
import warnings

# Ignore specific warnings from the genai library
warnings.filterwarnings("ignore", message=".*there are non-text parts in the response.*")

from pipe.core.utils.file import read_yaml_file, read_text_file
from dotenv import load_dotenv
from datetime import datetime, timezone
import zoneinfo
import importlib
import inspect

from pipe.core.services.session_service import SessionService
from pipe.core.models.session import Session, Reference
from pipe.core.models.turn import UserTaskTurn, ModelResponseTurn, FunctionCallingTurn, ToolResponseTurn, Turn
from pipe.core.agents.gemini_api import call_gemini_api, load_tools
from pipe.core.agents.gemini_cli import call_gemini_cli
from pipe.core.token_manager import TokenManager
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.dispatcher import dispatch_run
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings

def check_and_show_warning(project_root: str) -> bool:
    """Checks for the warning file, displays it, and gets user consent."""
    sealed_path = os.path.join(project_root, "sealed.txt")
    unsealed_path = os.path.join(project_root, "unsealed.txt")

    if os.path.exists(unsealed_path):
        return True

    warning_content = read_text_file(sealed_path)
    if not warning_content:
        return True

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

def _run(session_service: SessionService, args: TaktArgs):
    session_id = session_service.current_session_id
    
    if session_id:
        pool = session_service.get_pool(session_id)
        if pool and len(pool) >= 7:
            print(f"Warning: The number of items in the session pool ({len(pool)}) has reached the limit (7). Halting further processing to prevent potential infinite loops.", file=sys.stderr)
            return

    model_response_text = ""
    
    try:
        _, token_count, turns_to_save = dispatch_run(session_service, args)
        if turns_to_save is None and token_count is None:
            return

    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return
    
    for turn in turns_to_save:
        session_service.add_turn_to_session(session_id, turn)

    if token_count is not None:
        session_service.update_token_count(session_id, token_count)

    print(f"\nSuccessfully added response to session {session_id}.", file=sys.stderr)
    # Signal the end of the stream to the web UI, ensuring it's on a new line.
    print("\n", flush=True)
    print("event: end", flush=True)

def _help(parser):
    parser.print_help()

def _parse_arguments():
    parser = argparse.ArgumentParser(description="A task-oriented chat agent for context engineering.")
    parser.add_argument('--dry-run', action='store_true', help='Build and print the prompt without executing.')
    parser.add_argument('--session', type=str, help='The ID of the session to continue, edit, or compress.')
    parser.add_argument('--purpose', type=str, help='The overall purpose of the new session.')
    parser.add_argument('--background', type=str, help='The background context for the new session.')
    parser.add_argument('--roles', type=str, help='Comma-separated paths to role files for the new session.')
    parser.add_argument('--parent', type=str, help='The ID of the parent session.')
    parser.add_argument('--instruction', type=str, help='The specific instruction for the current task.')
    parser.add_argument('--references', type=str, help='Comma-separated paths to reference files.')
    parser.add_argument('--multi-step-reasoning', action='store_true', help='Include multi-step reasoning process in the prompt.')
    parser.add_argument('--fork', type=str, metavar='SESSION_ID', help='The ID of the session to fork.')
    parser.add_argument('--at-turn', type=int, metavar='TURN_INDEX', help='The 1-based turn number to fork from. Required with --fork.')
    parser.add_argument('--api-mode', type=str, help='Specify the API mode (e.g., gemini-api, gemini-cli).')
    
    args = parser.parse_args()
    return args, parser

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if not check_and_show_warning(project_root):
        sys.exit(1)

    load_dotenv()
    config_path = os.path.join(project_root, 'setting.yml')
    if not os.path.exists(config_path):
        config_path = os.path.join(project_root, 'setting.default.yml')
    
    settings_dict = read_yaml_file(config_path)
    settings = Settings(**settings_dict)
    
    parsed_args, parser = _parse_arguments()
    args = TaktArgs.from_parsed_args(parsed_args)

    if args.api_mode:
        settings.api_mode = args.api_mode
    
    session_service = SessionService(project_root, settings)

    if args.fork:
        if not args.at_turn:
            print("Error: --at-turn is required when using --fork.", file=sys.stderr)
            sys.exit(1)
        try:
            fork_index = args.at_turn - 1
            new_session_id = session_service.fork_session(args.fork, fork_index)
            print(f"Successfully forked session {args.fork} at turn {args.at_turn}.")
            print(f"New session created: {new_session_id}")
        except (FileNotFoundError, IndexError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.instruction:
        session_service.prepare_session_for_takt(args)
        _run(session_service, args)

    else:
        _help(parser)

if __name__ == "__main__":
    main()