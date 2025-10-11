import argparse
import os
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv
from datetime import datetime, timezone
import zoneinfo

from src.history_manager import HistoryManager
from src.gemini_api import call_gemini_api
from src.gemini_cli import call_gemini_cli

def load_settings(config_path: Path) -> dict:
    if config_path.exists():
        with config_path.open('r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def main():
    load_dotenv()
    project_root = Path(__file__).parent
    config_path = project_root / 'setting.yml'
    settings = load_settings(config_path)
    
    api_mode = settings.get('api_mode')
    if not api_mode:
        raise ValueError("'api_mode' not found in setting.yml")

    tz_name = os.getenv('TIMEZONE', 'UTC')
    try:
        local_tz = zoneinfo.ZoneInfo(tz_name)
    except zoneinfo.ZoneInfoNotFoundError:
        print(f"Warning: Timezone '{tz_name}' not found. Using UTC.", file=sys.stderr)
        local_tz = timezone.utc

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
    
    history_manager = HistoryManager(project_root / 'sessions', timezone_obj=local_tz)

    if args.compress:
        # This part of the logic can be implemented separately.
        print("Compression logic not fully implemented in this refactor.")
        pass

    elif args.instruction:
        session_id = args.session

        # 1. Load or create session data in memory
        if session_id:
            session_data_for_prompt = history_manager.get_session(session_id)
            if not session_data_for_prompt:
                print(f"Error: Session ID '{session_id}' not found.", file=sys.stderr)
                return
            if not args.multi_step_reasoning:
                enable_multi_step_reasoning = session_data_for_prompt.get('multi_step_reasoning_enabled', False)
            else:
                enable_multi_step_reasoning = True
            session_data_for_prompt['multi_step_reasoning_enabled'] = enable_multi_step_reasoning
        else:
            if not all([args.purpose, args.background]):
                parser.error("A new session requires --purpose and --background.")
            roles = args.roles.split(',') if args.roles else []
            enable_multi_step_reasoning = args.multi_step_reasoning
            session_data_for_prompt = {
                "purpose": args.purpose,
                "background": args.background,
                "roles": roles,
                "multi_step_reasoning_enabled": enable_multi_step_reasoning,
                "turns": []
            }
        
        # Add the current instruction to the turns for prompt building
        session_data_for_prompt['turns'].append({"type": "user_task", "instruction": args.instruction})

        model_response_text = ""
        try:
            if api_mode == 'gemini-api':
                print("\nExecuting with Gemini API...")
                model_response_text = call_gemini_api(
                    settings=settings,
                    session_data=session_data_for_prompt,
                    project_root=project_root,
                    instruction=args.instruction,
                    multi_step_reasoning_enabled=enable_multi_step_reasoning
                )
            elif api_mode == 'gemini-cli':
                print("\nExecuting with Gemini CLI...")
                model_response_text = call_gemini_cli(
                    settings=settings,
                    session_data=session_data_for_prompt,
                    project_root=project_root,
                    instruction=args.instruction,
                    multi_step_reasoning_enabled=enable_multi_step_reasoning
                )
            else:
                print(f"Error: Unknown api_mode '{api_mode}'. Please check setting.yml", file=sys.stderr)
                return

        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            session_data_for_prompt['turns'].pop() # Remove the turn we just added before exiting
            return
        except RuntimeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            session_data_for_prompt['turns'].pop() # Remove the turn we just added before exiting
            return

        # 3. Handle Dry Run (if applicable, this should be handled within the call functions)
        if args.dry_run:
            print("\n--- Dry Run Mode: No files were written. ---")
            return

        # 4. Save the user's turn and the new token count (token count is now handled within gemini_api)
        task_data = {"type": "user_task", "instruction": args.instruction}
        if not session_id:
            roles = args.roles.split(',') if args.roles else []
            session_id = history_manager.create_new_session(
                purpose=args.purpose, background=args.background, roles=roles, 
                multi_step_reasoning_enabled=enable_multi_step_reasoning
            )
            history_manager.add_turn_to_session(session_id, task_data)
            print(f"Conductor Agent: Creating new session...\nNew session created: {session_id}")
        else:
            history_manager.add_turn_to_session(session_id, task_data)
            print(f"Conductor Agent: Continuing session: {session_id}")

        print("--- Response Received ---")
        print(model_response_text)
        print("-------------------------\n")

        # 5. Save the model's response
        response_data = {"type": "model_response", "content": model_response_text}
        history_manager.add_turn_to_session(session_id, response_data)
        print(f"Successfully added response to session {session_id}.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
