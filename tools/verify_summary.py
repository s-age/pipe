import json
from typing import Dict, Any
from src.gemini_api import call_gemini_api
from datetime import datetime

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
    Asks a sub-agent to verify a summary for consistency and completeness
    within the full context of the conversation.
    """
    if not session_manager:
        return {"error": "This tool requires a session_manager."}

    try:
        # 1. Get the full session data
        original_session_data = session_manager.history_manager.get_session(session_id)
        if not original_session_data:
            return {"error": f"Session with ID {session_id} not found."}

        original_turns = original_session_data.get("turns", [])
        
        # 2. Create the temporary, modified turn list
        temp_turns = list(original_turns) # Create a copy

        summary_turn = {
            "type": "compressed_history",
            "content": summary_text,
            "original_turns_range": [start_turn, end_turn]
            # No timestamp for this temporary turn
        }

        # Replace the range
        if not (0 <= start_turn < len(temp_turns) and 0 <= end_turn < len(temp_turns) and start_turn <= end_turn):
             return {"error": "Turn indices are out of range for creating verification context."}

        del temp_turns[start_turn:end_turn + 1]
        temp_turns.insert(start_turn, summary_turn)

        # 3. Construct the verifier session data
        verifier_instruction = (
            "You are a verification agent. Your task is to review a conversation history that has had a portion of it replaced by a summary (marked as 'compressed_history'). "
            "Read the entire conversation flow, paying close attention to the summary in its place. "
            "Does the conversation still flow logically? Does the summary seem to capture the essence of the surrounding context? Is critical information likely missing? "
            "You MUST answer with only 'Yes' or 'No', followed by a brief explanation of your reasoning. "
            "A 'Yes' means the summary is good and the context is preserved. A 'No' means it is flawed."
        )

        # We create a new session data object for the verifier, using the modified turns
        verifier_session_data = {
            "purpose": f"Verify summary for session {session_id}",
            "background": "A portion of the original conversation has been replaced by a summary. I need to know if the summary is a good replacement.",
            "turns": temp_turns + [{"type": "user_task", "instruction": verifier_instruction}]
        }

        # 4. Call the LLM API
        response = call_gemini_api(
            settings=settings,
            session_data=verifier_session_data,
            project_root=project_root,
            instruction=verifier_instruction,
            api_mode='gemini-api',
            multi_step_reasoning_enabled=True
        )

        response_text = response.text.strip().lower()

        # 5. Analyze the response
        if response_text.startswith('yes'):
            return {"approved": True, "reasoning": response.text}
        else:
            return {"approved": False, "reasoning": response.text}

    except Exception as e:
        return {"error": f"An unexpected error occurred during summary verification: {e}"}