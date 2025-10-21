import json
import os
from typing import Dict, Any

from src.gemini_api import call_gemini_api
from src.gemini_cli import call_gemini_cli

def verify_summary(
    session_id: str, # This is the ID of the session being summarized
    start_turn: int,
    end_turn: int,
    summary_text: str,
    settings: dict,
    project_root: str,
    session_manager=None
) -> Dict[str, Any]:
    """
    Verifies a summary by creating a new temporary session for a sub-agent,
    and returns the verification status and the ID of the temporary session.
    """
    if not session_manager:
        return {"error": "This tool requires a session_manager."}

    language = settings.get('language', 'english')
    api_mode = settings.get('api_mode', 'gemini-api')

    try:
        # === Step 1: Prepare the data for the verifier agent ===
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

        # === Step 2: Create a new, temporary session for verification ===
        verifier_purpose = f"Verification of summary for session {session_id}"
        verifier_background = "A sub-agent will review a conversation history where a summary has been inserted. The agent must judge if the summary is a good replacement and respond with 'Approved:' or 'Rejected:'."
        
        verifier_session_id = session_manager.history_manager.create_new_session(
            purpose=verifier_purpose,
            background=verifier_background,
            roles=["roles/reviewer.md"] # Using a dedicated reviewer role
        )

        # Add the prepared history to the new verifier session
        session_manager.history_manager.update_turns(verifier_session_id, temp_turns)

        # === Step 3: Call the verifier agent ===
        approved_text = "Please approve the summary."
        rejected_text = "Verification failed. Please modify the summary policy."
        lang_instruction = f"You must generate the response in {language}."
        verifier_instruction = (
            f"## TASK\n"
            f"You are a verification agent. Your task is to review the provided conversation history and generate a final, formatted response based on your verification.\n\n"
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
            f"[Explain the reason for rejection here]"
        )

        verifier_session_data = session_manager.history_manager.get_session(verifier_session_id)
        verifier_session_data['turns'].append({"type": "user_task", "instruction": verifier_instruction})

        if api_mode == 'gemini-api':
            response = call_gemini_api(settings=settings, session_data=verifier_session_data, project_root=project_root, instruction=verifier_instruction, api_mode=api_mode, multi_step_reasoning_enabled=True)
            response_text = response.text.strip()
        elif api_mode == 'gemini-cli':
            response_text = call_gemini_cli(settings=settings, session_data=verifier_session_data, project_root=project_root, instruction=verifier_instruction, api_mode=api_mode, multi_step_reasoning_enabled=True, session_id=verifier_session_id).strip()
        else:
            raise ValueError(f"Unsupported api_mode: {api_mode}")

        # === Step 4: Process result and construct the final turn content ===
        status = "rejected"
        final_turn_content = ""
        if response_text.startswith(f'Approved: {approved_text}'):
            status = "approved"
            final_turn_content = f"Approved: {approved_text}\n\n## SUMMARY CONTENTS\n\n{summary_text}"
        elif response_text.startswith(f'Rejected: {rejected_text}'):
            reason_parts = response_text.split('## REJECTED REASON\n\n', 1)
            reason = reason_parts[1] if len(reason_parts) > 1 else "No reason provided."
            final_turn_content = f"Rejected: {rejected_text}\n\n## REJECTED REASON\n\n{reason}"
        else:
            final_turn_content = f"Rejected: {rejected_text}\n\n## REJECTED REASON\n\nVerification response was not in the expected format:\n{response_text}"

        # Create the turn with the complete content
        final_turn = {"type": "model_response", "content": final_turn_content}
        
        # Add to the verifier session for logging
        session_manager.history_manager.add_turn_to_session(verifier_session_id, final_turn)

        # Also add the result to the original session's pool so the calling agent can see it.
        session_manager.history_manager.add_to_pool(session_id, final_turn)

        # === Step 5: Return the result and the verifier session ID ===
        return {
            "status": status,
            "verifier_session_id": verifier_session_id,
            "message": f"Verification process completed in session {verifier_session_id}. Status: {status}."
        }

    except Exception as e:
        import traceback
        return {"error": f"An unexpected error occurred during summary verification: {e}\n{traceback.format_exc()}"}
