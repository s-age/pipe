import argparse
import os
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv
from datetime import datetime, timezone
import zoneinfo
import importlib
from google.generativeai import types as genai_types

from src.history_manager import HistoryManager
from src.gemini_api import call_gemini_api
from src.gemini_cli import call_gemini_cli

def load_settings(config_path: Path) -> dict:
    if config_path.exists():
        with config_path.open('r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def execute_tool_call(tool_call):
    """Dynamically imports and executes a tool function."""
    tool_name = tool_call.name
    tool_args = dict(tool_call.args)
    
    print(f"Tool call: {tool_name}({tool_args})")

    try:
        tool_module = importlib.import_module(f"tools.{tool_name}")
        tool_function = getattr(tool_module, tool_name)
        result = tool_function(**tool_args)
        return result
    except Exception as e:
        return {"error": f"Failed to execute tool {tool_name}: {e}"}

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
        print("Compression logic not fully implemented in this refactor.")
        pass

    elif args.instruction:
        session_id = args.session

        if session_id:
            session_data_for_prompt = history_manager.get_session(session_id)
            if not session_data_for_prompt:
                print(f"Error: Session ID '{session_id}' not found.", file=sys.stderr)
                return
            enable_multi_step_reasoning = args.multi_step_reasoning or session_data_for_prompt.get('multi_step_reasoning_enabled', False)
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
        
        session_data_for_prompt['turns'].append({"type": "user_task", "instruction": args.instruction})

        model_response_text = ""
        try:
            if api_mode == 'gemini-api':
                print("\nExecuting with Gemini API...")
                
                while True:
                    response = call_gemini_api(
                        settings=settings,
                        session_data=session_data_for_prompt,
                        project_root=project_root,
                        instruction=args.instruction, # This is used by the builder, not directly by the API call
                        api_mode=api_mode,
                        multi_step_reasoning_enabled=enable_multi_step_reasoning
                    )

                    try:
                        part = response.candidates[0].content.parts[0]
                        function_call = part.function_call if hasattr(part, 'function_call') and part.function_call else None
                    except (IndexError, AttributeError):
                        function_call = None

                    if not function_call:
                        model_response_text = response.text
                        break # No function call, so this is the final answer

                    # --- Function Call Execution ---
                    model_turn = {
                        "type": "model_response",
                        "function_call": {'name': function_call.name, 'args': dict(function_call.args)}
                    }
                    session_data_for_prompt['turns'].append(model_turn)

                    tool_result = execute_tool_call(function_call)
                    
                    tool_turn = {
                        "type": "tool_response",
                        "name": function_call.name,
                        "response": tool_result
                    }
                    session_data_for_prompt['turns'].append(tool_turn)

            elif api_mode == 'gemini-cli':
                # This mode does not support function calling loop
                response = call_gemini_cli(
                    settings=settings,
                    session_data=session_data_for_prompt,
                    project_root=project_root,
                    instruction=args.instruction,
                    api_mode=api_mode,
                    multi_step_reasoning_enabled=enable_multi_step_reasoning
                )
                model_response_text = response.text

            else:
                print(f"Error: Unknown api_mode '{api_mode}'. Please check setting.yml", file=sys.stderr)
                return

        except (ValueError, RuntimeError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            session_data_for_prompt['turns'].pop() # Remove the user_task turn we added
            return

        if args.dry_run:
            print("\n--- Dry Run Mode: No files were written. ---")
            return

        # Pop the initial user_task, as it will be saved properly below
        session_data_for_prompt['turns'].pop(0)

        task_data = {"type": "user_task", "instruction": args.instruction}
        if not session_id:
            roles = args.roles.split(',') if args.roles else []
            session_id = history_manager.create_new_session(
                purpose=args.purpose, background=args.background, roles=roles, 
                multi_step_reasoning_enabled=enable_multi_step_reasoning
            )
            print(f"Conductor Agent: Creating new session...\nNew session created: {session_id}")
        else:
            print(f"Conductor Agent: Continuing session: {session_id}")

        # Save the full history of the interaction (user_task, model_function_calls, tool_responses)
        for turn in session_data_for_prompt['turns']:
            history_manager.add_turn_to_session(session_id, turn)

        # Save the final text response separately
        final_response_data = {"type": "model_response", "content": model_response_text}
        history_manager.add_turn_to_session(session_id, final_response_data)

        print("--- Response Received ---")
        print(model_response_text)
        print("-------------------------\n")
        print(f"Successfully added response to session {session_id}.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()