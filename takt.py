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

from src.session_manager import SessionManager
from src.gemini_api import call_gemini_api
from src.gemini_cli import call_gemini_cli
from src.prompt_builder import PromptBuilder

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



def execute_tool_call(tool_call):
    """Dynamically imports and executes a tool function."""
    tool_name = tool_call.name
    tool_args = dict(tool_call.args)
    
    print(f"Tool call: {tool_name}({tool_args})")

    try:
        tool_module = importlib.import_module(f"tools.{tool_name}")
        importlib.reload(tool_module)  # Force reload to get the latest code
        tool_function = getattr(tool_module, tool_name)
        result = tool_function(**tool_args)
        return result
    except Exception as e:
        return {"error": f"Failed to execute tool {tool_name}: {e}"}

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
    
    session_manager = SessionManager(project_root / 'sessions', timezone_obj=local_tz)

    if args.compress:
        print("Compression logic not fully implemented in this refactor.")
        pass

    elif args.instruction:
        session_id = args.session
        roles = args.roles.split(',') if args.roles else []
        enable_multi_step_reasoning = args.multi_step_reasoning

        session_data_for_prompt = session_manager.get_or_create_session_data(
            session_id=session_id,
            purpose=args.purpose,
            background=args.background,
            roles=roles,
            multi_step_reasoning_enabled=enable_multi_step_reasoning
        )
        
        session_data_for_prompt['turns'].append({"type": "user_task", "instruction": args.instruction, "timestamp": datetime.now(local_tz).isoformat()})

        if args.dry_run:
            print("\n--- Dry Run Mode ---")
            builder = PromptBuilder(
                settings=settings,
                session_data=session_data_for_prompt,
                project_root=project_root,
                api_mode=api_mode,
                multi_step_reasoning_enabled=enable_multi_step_reasoning
            )
            
            prompt_obj = builder.build()
            print(json.dumps(prompt_obj, indent=2, ensure_ascii=False))
            
            print("\n--- End of Dry Run ---")
            return

        model_response_text = ""
        try:
            if api_mode == 'gemini-api':
                print("\nExecuting with Gemini API...")
                
                while True:
                    response = call_gemini_api(
                        settings=settings,
                        session_data=session_data_for_prompt,
                        project_root=project_root,
                        instruction=args.instruction,
                        api_mode=api_mode,
                        multi_step_reasoning_enabled=enable_multi_step_reasoning
                    )

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

                    model_turn = {
                        "type": "model_response",
                        "function_call": {'name': function_call.name, 'args': dict(function_call.args)},
                        "timestamp": datetime.now(local_tz).isoformat()
                    }
                    session_data_for_prompt['turns'].append(model_turn)

                    tool_result = execute_tool_call(function_call)
                    
                    tool_turn = {
                        "type": "tool_response",
                        "name": function_call.name,
                        "response": tool_result,
                        "timestamp": datetime.now(local_tz).isoformat()
                    }
                    session_data_for_prompt['turns'].append(tool_turn)

            elif api_mode == 'gemini-cli':
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
            session_data_for_prompt['turns'].pop()
            return



        if not session_id:
            session_id = session_manager.create_new_session(
                purpose=args.purpose, background=args.background, roles=roles, 
                multi_step_reasoning_enabled=enable_multi_step_reasoning
            )
            print(f"Conductor Agent: Creating new session...\nNew session created: {session_id}")
        else:
            print(f"Conductor Agent: Continuing session: {session_id}")

        for turn in session_data_for_prompt['turns']:
            session_manager.add_turn_to_session(session_id, turn)

        final_response_data = {"type": "model_response", "content": model_response_text, "timestamp": datetime.now(local_tz).isoformat()}
        session_manager.add_turn_to_session(session_id, final_response_data)

        print("--- Response Received ---")
        print(model_response_text)
        print("-------------------------\n")
        print(f"Successfully added response to session {session_id}.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()