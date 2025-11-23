import json
import os
import subprocess
import sys
from typing import Any

import google.genai as genai
from pipe.core.models.settings import Settings
from pipe.core.tools.verify_summary import verify_summary


def create_verified_summary(
    session_id: str,  # This is the ID of the session to be summarized.
    start_turn: int,
    end_turn: int,
    policy: str,
    target_length: int,
    settings: Settings,
    project_root: str,
    session_service=None,
) -> dict[str, Any]:
    """
    Generates a summary and then calls the verify_summary tool to perform
    verification and handle subsequent actions.
    """
    api_mode = settings.api_mode
    if not session_service:
        return {"error": "This tool requires a session_service."}

    # === Role Check ===
    current_session_id = os.environ.get("PIPE_SESSION_ID")
    if not current_session_id:
        return {"error": "No current session ID found."}
    session_data = session_service.get_session(current_session_id)
    if not session_data:
        return {"error": f"Session with ID {current_session_id} not found."}
    active_roles = session_data.roles
    # The role file might be 'roles/compressor.md', so we check for the
    # substring 'compressor'
    if not any("compressor" in role for role in active_roles):
        return {
            "error": (
                "This tool can only be executed by an agent with the 'compressor' "
                "role."
            )
        }
    # === End of Role Check ===

    try:
        # === Step 1: Generate Summary ===
        start_index = start_turn - 1
        end_index = end_turn - 1

        session_to_summarize = session_service.get_session(session_id)
        if not session_to_summarize:
            return {"error": f"Session with ID {session_id} not found."}

        turns_to_summarize = session_to_summarize.turns[start_index : end_index + 1]
        if not turns_to_summarize:
            return {"error": "No turns found in the specified range."}

        # Convert turns to text for summarization
        conversation_text = ""
        for turn in turns_to_summarize:
            if turn.type == "user_task":
                conversation_text += f"User: {turn.instruction}\n"
            elif turn.type == "model_response":
                conversation_text += f"Assistant: {turn.content}\n"
            elif turn.type == "function_calling":
                conversation_text += f"Function Call: {turn.response}\n"
            elif turn.type == "tool_response":
                conversation_text += f"Tool Response: {turn.response}\n"
            # Add other turn types as needed

        summarizer_instruction = (
            f"Please summarize the following conversation according to the policy: "
            f"'{policy}'. "
            f"The summary should be approximately {target_length} characters long.\n\n"
            f"Conversation:\n{conversation_text}"
        )

        if api_mode == "gemini-api":
            client = genai.Client()
            response = client.models.generate_content(
                model=settings.model,
                contents=summarizer_instruction,
            )
            summary_text = response.text
        elif api_mode == "gemini-cli":
            prompt_json = json.dumps({"contents": summarizer_instruction}, indent=2)
            command = [
                "gemini",
                "-y",
                "-m",
                settings.model,
                "-p",
                prompt_json,
            ]
            cli_result = subprocess.run(command, capture_output=True, text=True)
            if cli_result.returncode != 0:
                raise RuntimeError(f"Gemini CLI failed: {cli_result.stderr}")
            summary_text = cli_result.stdout.strip()
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
            session_service=session_service,
        )

        # Include the summary and parameters in the result
        result = {
            "status": verification_result.get("status"),
            "verifier_session_id": verification_result.get("verifier_session_id"),
            "message": verification_result.get("message"),
            "session_id": session_id,
            "start_turn": start_turn,
            "end_turn": end_turn,
            "summary": summary_text,
        }

        # Add the result to the pool for the compressor agent to see
        from pipe.core.models.turn import ToolResponseTurn
        from pipe.core.utils.datetime import get_current_timestamp

        result_turn = ToolResponseTurn(
            name="create_verified_summary",
            response=result,
            timestamp=get_current_timestamp(),
        )
        session_service.add_to_pool(session_id, result_turn)

        return {"content": result}

    except Exception as e:
        import traceback

        print(
            f"ERROR in create_verified_summary: {e}\n{traceback.format_exc()}",
            file=sys.stderr,
        )
        error_result = {
            "status": "rejected",
            "message": f"Summary generation failed: {e}",
            "verifier_session_id": None,
            "session_id": session_id,
            "start_turn": start_turn,
            "end_turn": end_turn,
            "summary": "",
        }
        # Add the error result to the pool
        from pipe.core.models.turn import ToolResponseTurn
        from pipe.core.utils.datetime import get_current_timestamp

        error_turn = ToolResponseTurn(
            name="create_verified_summary",
            response=error_result,
            timestamp=get_current_timestamp(),
        )
        session_service.add_to_pool(session_id, error_turn)

        return {"content": error_result}
