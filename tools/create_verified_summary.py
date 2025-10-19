import json
import subprocess
import sys
import os
from typing import Dict, Any
from src.gemini_api import call_gemini_api
from src.gemini_cli import call_gemini_cli
from tools.verify_summary import verify_summary

def create_verified_summary(
    session_id: str, # This is the ID of the session to be summarized.
    start_turn: int,
    end_turn: int,
    policy: str,
    target_length: int,
    settings: dict,
    project_root: str,
    session_manager=None
) -> Dict[str, Any]:
    """
    Generates a summary and then calls the verify_summary tool to perform
    verification and handle subsequent actions.
    """
    api_mode = settings.get('api_mode', 'gemini-api')
    if not session_manager:
        return {"error": "This tool requires a session_manager."}

    try:
        # === Step 1: Generate Summary ===
        start_index = start_turn - 1
        end_index = end_turn - 1
        turns_to_summarize = session_manager.history_manager.get_session_turns_range(session_id, start_index, end_index)
        if not turns_to_summarize:
            return {"error": "No turns found in the specified range."}

        summarizer_instruction = (
            f"You are a summarization agent. Based on the provided conversation turns and policy, create a concise summary.\n\n"
            f"Policy: {policy}\n"
            f"Target Length: Approximately {target_length} characters.\n\n"
            "--- CONVERSATION TURNS ---\n"
            f"{json.dumps(turns_to_summarize, indent=2, ensure_ascii=False)}"
        )
        summarizer_session_data = {"turns": [{"type": "user_task", "instruction": summarizer_instruction}]}
        
        if api_mode == 'gemini-api':
            summary_response = call_gemini_api(settings=settings, session_data=summarizer_session_data, project_root=project_root, instruction=summarizer_instruction, api_mode=api_mode, multi_step_reasoning_enabled=False)
            summary_text = summary_response.text.strip()
        elif api_mode == 'gemini-cli':
            summary_response = call_gemini_cli(settings=settings, session_data=summarizer_session_data, project_root=project_root, instruction=summarizer_instruction, api_mode=api_mode, multi_step_reasoning_enabled=False)
            summary_text = summary_response.strip()
        else:
            raise ValueError(f"Unsupported api_mode: {api_mode}")

        # === Step 2: Call verify_summary tool to handle verification and next steps ===
        verification_result = verify_summary(
            session_id=session_id,
            start_turn=start_turn,
            end_turn=end_turn,
            summary_text=summary_text,
            settings=settings,
            project_root=project_root,
            session_manager=session_manager
        )

        return verification_result

    except Exception as e:
        import traceback
        print(f"ERROR in create_verified_summary: {e}\n{traceback.format_exc()}", file=sys.stderr)
        return {"error": f"An unexpected error occurred: {e}"}
