import json
import os
from typing import Dict, Any
from src.gemini_api import call_gemini_api
from src.gemini_cli import call_gemini_cli
from datetime import datetime

def get_latest_session_id(sessions_dir: str) -> str:
    """
    Scans the sessions directory and returns the most recently modified session ID.
    """
    try:
        files = [os.path.join(sessions_dir, f) for f in os.listdir(sessions_dir) if f.endswith('.json') and not f.startswith('index')]
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        return os.path.splitext(os.path.basename(latest_file))[0]
    except FileNotFoundError:
        return None

def verify_summary(
    session_id: str,
    start_turn: int,
    end_turn: int,
    summary_text: str,
    settings: dict,
    project_root: str,
    session_manager=None
) -> Dict[str, Any]:
    """
    Verifies a summary and then writes the result (either the summary itself or a rejection reason)
    to the current active session under a specific header.
    """
    if not session_manager:
        return {"error": "This tool requires a session_manager."}

    language = settings.get('language', 'english')

    try:
        # Per user instruction, use hardcoded English text and dynamic lang_instruction
        approved_text = "Please approve the summary."
        rejected_text = "Verification failed. Please modify the summary policy."
        lang_instruction = f"You must generate the response in {language}."

        # === Step 1: Construct the verifier instruction with formatting rules ===
        verifier_instruction = (
            f"## TASK\n"
            f"You are a verification agent. Your task is to review a conversation history where a summary has been inserted, and then generate a final, formatted response based on your verification.\n\n"
            f"## STEP-BY-STEP INSTRUCTIONS\n"
            f"1.  **Analyze**: Read the entire conversation history provided. A part of it is replaced by a summary marked as 'compressed_history'. Judge if this summary is a good replacement (i.e., preserves context, flows logically).\n"
            f"2.  **Generate Response**: Based on your judgment, you MUST generate a response that starts with ONE of the following two prefixes: `Approved:` or `Rejected:`. Do not add any other text, explanation, or markdown fences before the prefix.\n\n"
            f"## OUTPUT FORMATS\n\n"
            f"### Format 1: If your judgment is 'Yes' (Approved)\n"
            f"Your entire response must start with the exact phrase below.\n"
            f"`Approved: {approved_text}`\n\n"
            f"### Format 2: If your judgment is 'No' (Rejected)\n"
            f"Your entire response must start with the exact phrase below, followed by a clear explanation of the reason for rejection.\n"
            f"`Rejected: {rejected_text}`\n"
            f"## REJECTED REASON\n\n"
            f"[Explain the reason for rejection here]\n\n"
            f"## LANGUAGE\n"
            f"{lang_instruction}"
        )

        original_session_data = session_manager.history_manager.get_session(session_id)
        if not original_session_data:
            return {"error": f"Session with ID {session_id} not found."}

        original_turns = original_session_data.get("turns", [])
        temp_turns = list(original_turns)
        summary_turn = {"type": "compressed_history", "content": summary_text, "original_turns_range": [start_turn, end_turn]}
        
        start_index = start_turn - 1
        end_index = end_turn - 1
        if not (0 <= start_index < len(temp_turns) and 0 <= end_index < len(temp_turns) and start_index <= end_index):
             return {"error": "Turn indices are out of range for creating verification context."}

        del temp_turns[start_index:end_index + 1]
        temp_turns.insert(start_index, summary_turn)

        verifier_session_data = {
            "purpose": f"Verify summary for session {session_id}",
            "background": "A portion of the original conversation has been replaced by a summary.",
            "turns": temp_turns + [{"type": "user_task", "instruction": verifier_instruction}]
        }

        api_mode = settings.get('api_mode', 'gemini-api')
        if api_mode == 'gemini-api':
            response = call_gemini_api(settings=settings, session_data=verifier_session_data, project_root=project_root, instruction=verifier_instruction, api_mode=api_mode, multi_step_reasoning_enabled=True)
            response_text = response.text.strip()
        elif api_mode == 'gemini-cli':
            response_text = call_gemini_cli(settings=settings, session_data=verifier_session_data, project_root=project_root, instruction=verifier_instruction, api_mode=api_mode, multi_step_reasoning_enabled=True, session_id=session_id).strip()
        else:
            raise ValueError(f"Unsupported api_mode: {api_mode}")

        # === Step 2: Construct the final content based on verification ===
        if response_text.startswith(f'Approved: {approved_text}'):
            new_turn_content = f"Approved: {approved_text}\n\n## SUMMARY CONTENTS\n\n{summary_text}"
        elif response_text.startswith(f'Rejected: {rejected_text}'):
            # Extract the reason part from the response
            reason_parts = response_text.split('## REJECTED REASON\n\n', 1)
            reason = reason_parts[1] if len(reason_parts) > 1 else "No reason provided."
            new_turn_content = f"Rejected: {rejected_text}\n\n## REJECTED REASON\n\n{reason}"
        else:
            # Handle cases where the response is not in the expected format
            new_turn_content = f"Rejected: {rejected_text}\n\n## REJECTED REASON\n\nVerification response was not in the expected format:\n{response_text}"

        # === Step 3: Add the new turn to the current active session ===
        writing_session_id = get_latest_session_id(session_manager.history_manager.sessions_dir)
        if not writing_session_id:
            return {"error": "Could not determine the current session to write to."}
        
        new_turn = {
            "type": "model_response",
            "content": new_turn_content
        }
        session_manager.add_turn_to_session(writing_session_id, new_turn)

        return {"status": "succeeded", "message": f"Result turn added to session {writing_session_id}."}

    except Exception as e:
        return {"error": f"An unexpected error occurred during summary verification: {e}"}