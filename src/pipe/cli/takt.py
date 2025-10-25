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
from pipe.core.gemini_api import call_gemini_api, load_tools
from pipe.core.gemini_cli import call_gemini_cli
from pipe.core.prompt_builder import PromptBuilder
from pipe.core.token_manager import TokenManager
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.dispatcher import dispatch_run

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

def _run(args, settings, session_service, session_data: Session, project_root, api_mode, enable_multi_step_reasoning):
    session_id = args.session
    if session_id:
        pool = session_service.get_pool(session_id)
        if pool and len(pool) >= 7:
            print(f"Warning: The number of items in the session pool ({len(pool)}) has reached the limit (7). Halting further processing to prevent potential infinite loops.", file=sys.stderr)
            return

    model_response_text = ""
    
    try:
        model_response_text, token_count, intermediate_turns = dispatch_run(
            api_mode,
            args,
            settings,
            session_data,
            project_root,
            enable_multi_step_reasoning,
            session_service
        )
        if model_response_text is None and token_count is None:
            return

        if not model_response_text or not model_response_text.strip():
            model_response_text = "API Error: Model stream ended with empty response text."

    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return

    session_id = args.session
    
    final_model_turn = ModelResponseTurn(
        type="model_response",
        content=model_response_text,
        timestamp=get_current_timestamp(session_service.timezone_obj)
    )

    turns_to_save = intermediate_turns + [final_model_turn]

    for turn in turns_to_save:
        session_service.add_turn_to_session(session_id, turn)

    if token_count is not None:
        session_service.update_token_count(session_id, token_count)

    print(f"\nSuccessfully added response to session {session_id}.")

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
    settings = read_yaml_file(config_path)
    
    args, parser = _parse_arguments()

    api_mode = settings.get('api_mode')
    if not api_mode:
        raise ValueError("'api_mode' not found in setting.yml")
    
    session_service = SessionService(os.path.join(project_root, 'sessions'))

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
        session_id = args.session
        if session_id:
            session_id = session_id.strip().rstrip('.')
            args.session = session_id
            
        roles = args.roles.split(',') if args.roles else []
        enable_multi_step_reasoning = args.multi_step_reasoning

        session_or_dict = session_service.get_or_create_session_data(
            session_id=session_id,
            purpose=args.purpose,
            background=args.background,
            roles=roles,
            multi_step_reasoning_enabled=enable_multi_step_reasoning,
            instruction=args.instruction
        )
        
        if isinstance(session_or_dict, dict):
            session = Session(
                session_id="temp_session",
                created_at=get_current_timestamp(session_service.timezone_obj),
                token_count=0,
                hyperparameters={},
                references=[],
                **session_or_dict
            )
        else:
            session = session_or_dict

        if args.references:
            references = [Reference(path=ref.strip(), disabled=False) for ref in args.references.split(',') if ref.strip()]
            existing_paths = {ref.path for ref in session.references}
            new_references = [ref for ref in references if ref.path not in existing_paths]
            session.references.extend(new_references)

            if not args.dry_run and new_references and session_id:
                session_service.add_references(session_id, [ref.path for ref in new_references])
                print(f"Added {len(new_references)} new references to session {session_id}.", file=sys.stderr)

        if args.dry_run:
            from pipe.core.delegates import dry_run_delegate
            dry_run_delegate.run(
                settings,
                session,
                project_root,
                api_mode,
                enable_multi_step_reasoning
            )
            return

        if not session_id:
            if not all([args.purpose, args.background]):
                raise ValueError("A new session requires --purpose and --background for the first instruction.")
            session_id = session_service.create_new_session(
                purpose=args.purpose,
                background=args.background,
                roles=roles,
                multi_step_reasoning_enabled=enable_multi_step_reasoning,
                parent_id=args.parent
            )
            args.session = session_id
            
            first_turn = UserTaskTurn(type="user_task", instruction=args.instruction, timestamp=get_current_timestamp(session_service.timezone_obj))
            session_service.add_turn_to_session(session_id, first_turn)
            
            print(f"Conductor Agent: Creating new session...\nNew session created: {session_id}", file=sys.stderr)
        else:
            new_turn = UserTaskTurn(type="user_task", instruction=args.instruction, timestamp=get_current_timestamp(session_service.timezone_obj))
            session_service.add_turn_to_session(session_id, new_turn)
            print(f"Conductor Agent: Continuing session: {session_id}", file=sys.stderr)

        _run(args, settings, session_service, session, project_root, api_mode, enable_multi_step_reasoning)

    else:
        _help(parser)

if __name__ == "__main__":
    main()