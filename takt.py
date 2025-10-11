import argparse
import os
import sys
import json
from pathlib import Path
import yaml
from dotenv import load_dotenv
from datetime import datetime, timezone
import zoneinfo
import copy

from src.prompt_builder import PromptBuilder
from src.history_manager import HistoryManager
from src.token_manager import TokenManager
import gemini_api
import gemini_cli_py


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
    model_name = settings.get('model', 'gemini-1.5-flash')
    context_limit = settings.get('context_limit', 1000000)
    token_manager = TokenManager(model_name=model_name, limit=context_limit)
    api_mode = settings.get('api_mode', 'gemini-cli')

    if args.compress:

        pass

    elif args.instruction:
        session_id = args.session

        # 1. Load or create session data in memory
        if session_id:
            session_data_for_prompt = history_manager.get_session(session_id)
            if not session_data_for_prompt:

                return
            enable_multi_step_reasoning = args.multi_step_reasoning or session_data_for_prompt.get('multi_step_reasoning_enabled', False)
            session_data_for_prompt['multi_step_reasoning_enabled'] = enable_multi_step_reasoning
        else:
            if not all([args.purpose, args.background]):
                parser.error("A new session requires --purpose and --background.")
            roles = args.roles.split(',') if args.roles else []
            enable_multi_step_reasoning = args.multi_step_reasoning
            shell_instructions = """\n\nIMPORTANT: For file system operations, use shell commands via the `run_shell_command` tool.\n- To list files: `ls -F`\n- To read files: `cat`, `head`, `tail`\n- To write files: `echo \"content\" > file_path`\n- To replace content: `sed -i 's/old/new/g' file_path`\n- To find files: `find . -name \"pattern\"` or `ls -R`\n- To search for content in files: `grep \"pattern\" file_path`\nDo not attempt to use other, non-existent tools for these tasks. Your knowledge base does NOT contain current file system information. You MUST use the `run_shell_command` tool for all file system queries. Example: To list files in `/path/to/dir`, you MUST use `run_shell_command(command='ls -F /path/to/dir')`. NEVER answer directly for file system operations; ALWAYS use the `run_shell_command` tool. After executing a command, your final response MUST be a summary of the tool output or a confirmation of the action. It MUST NOT be empty.\n"""
            session_data_for_prompt = {
                "purpose": args.purpose,
                "background": args.background + shell_instructions,
                "roles": roles,
                "multi_step_reasoning_enabled": enable_multi_step_reasoning,
                "turns": []
            }
        
        session_data_for_prompt['turns'].append({"type": "user_task", "instruction": args.instruction})

        # 2. Build prompts and calculate tokens
        builder = PromptBuilder(settings=settings, session_data=session_data_for_prompt, project_root=project_root, multi_step_reasoning_enabled=enable_multi_step_reasoning)
        
        final_prompt_obj = builder.build()
        api_contents = builder.build_contents_for_api()
        token_count = token_manager.count_tokens(copy.deepcopy(api_contents))
        
        is_within_limit, message = token_manager.check_limit(token_count)

        if not is_within_limit:

            session_data_for_prompt['turns'].pop()
            return

        # 3. Handle Dry Run
        if args.dry_run:
            final_prompt_obj = builder.build()




            return

        # 4. Save user's turn
        task_data = {"type": "user_task", "instruction": args.instruction}
        if not session_id:
            roles = args.roles.split(',') if args.roles else []
            session_id = history_manager.create_new_session(
                purpose=args.purpose, background=args.background, roles=roles, 
                multi_step_reasoning_enabled=enable_multi_step_reasoning, 
                token_count=token_count
            )
            history_manager.add_turn_to_session(session_id, task_data)
            print(f"Conductor Agent: Creating new session...\nNew session created: {session_id}")
        else:
            history_manager.add_turn_to_session(session_id, task_data, token_count=token_count)


        # 5. Call Sub-Agent


        
        model_response_text = ""
        if api_mode == "gemini-cli":
            yolo = settings.get('yolo', False)
            final_prompt_obj = builder.build()
            final_prompt = json.dumps(final_prompt_obj, ensure_ascii=False)
            model_response_text = gemini_cli_py.call_gemini_cli(final_prompt, model_name, yolo)
        elif api_mode == "gemini-api":
            model_response_text = gemini_api.call_gemini_api(api_contents, model_name, final_prompt_obj["available_tools_schema"]["definitions"], settings)
        else:

            return

        if "Error:" in model_response_text:

            return





        # 6. Save model's response
        response_data = {"type": "model_response", "content": model_response_text}
        history_manager.add_turn_to_session(session_id, response_data)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()