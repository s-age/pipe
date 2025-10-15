import json
import subprocess
from typing import Dict, Any
from src.gemini_api import call_gemini_api

def create_verified_summary(
    session_id: str,
    start_turn: int,
    end_turn: int,
    policy: str,
    target_length: int,
    settings: dict,
    project_root: str,
    session_manager=None
) -> Dict[str, Any]:
    """
    Creates a verified summary of a range of turns from a target session.
    It internally generates a summary, then creates a new persistent session 
    to have a sub-agent verify it, and returns the verification result
    along with the verifier's session ID.
    """
    if not session_manager:
        return {"error": "This tool requires a session_manager."}

    try:
        # Convert 1-based turn numbers to 0-based indices
        start_index = start_turn - 1
        end_index = end_turn - 1

        # === Step 1: Generate Summary (1st LLM Call, ephemeral) ===
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
        
        summary_response = call_gemini_api(
            settings=settings,
            session_data=summarizer_session_data,
            project_root=project_root,
            instruction=summarizer_instruction,
            api_mode='gemini-api',
            multi_step_reasoning_enabled=False
        )
        summary_text = summary_response.text.strip()

        # === Step 2: Verify Summary (2nd LLM Call, persistent session) ===
        original_session_data = session_manager.history_manager.get_session(session_id)
        original_turns = original_session_data.get("turns", [])
        temp_turns = list(original_turns)

        summary_turn = {
            "type": "compressed_history",
            "content": summary_text,
            "original_turns_range": [start_turn, end_turn]
        }
        
        if not (0 <= start_index < len(temp_turns) and 0 <= end_index < len(temp_turns) and start_index <= end_index):
             return {"error": "Turn indices are out of range for creating verification context."}
        
        del temp_turns[start_index:end_index + 1]
        temp_turns.insert(start_index, summary_turn)

        verifier_purpose = f"Verify summary for session {session_id} (range {start_turn}-{end_turn})"
        verifier_background = "A sub-agent to verify a conversation summary. The history contains the original conversation with a 'compressed_history' turn replacing the summarized part."
        verifier_session_id = session_manager.history_manager.create_new_session(
            purpose=verifier_purpose,
            background=verifier_background,
            roles=[],
            multi_step_reasoning_enabled=True
        )

        session_manager.history_manager.update_turns(verifier_session_id, temp_turns)

        verifier_instruction = (
            "You are a verification agent. Review the conversation history provided. A portion has been replaced by a summary (marked 'compressed_history'). "
            "Does the conversation still flow logically? Is critical information likely missing? "
            "You MUST answer with only 'Yes' or 'No', followed by a brief explanation. 'Yes' means the summary is good."
        )

        command = [
            'python3', 'takt.py', '--session', verifier_session_id,
            '--instruction', verifier_instruction, '--multi-step-reasoning'
        ]
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8'
        )
        
        verifier_turns = session_manager.history_manager.get_session_turns(verifier_session_id)
        verification_response_text = verifier_turns[-1]['content'] if verifier_turns else ""
        verification_text_lower = verification_response_text.strip().lower()

        # === Step 3: Return Result ===
        if verification_text_lower.startswith('yes'):
            return {
                "status": "approved",
                "summary": summary_text,
                "verification_reasoning": verification_response_text,
                "verifier_session_id": verifier_session_id
            }
        else:
            return {
                "status": "rejected",
                "summary": summary_text,
                "verification_reasoning": verification_response_text,
                "verifier_session_id": verifier_session_id
            }

    except Exception as e:
        return {"error": f"An unexpected error occurred during summary creation/verification: {e}"}
