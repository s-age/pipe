"Service for verifying summaries using a sub-agent."

import subprocess
import traceback
from typing import TYPE_CHECKING

from pipe.core.models.turn import CompressedHistoryTurn
from pipe.core.utils.datetime import get_current_timestamp

if TYPE_CHECKING:
    from pipe.core.agents.takt_agent import TaktAgent
    from pipe.core.services.session_service import SessionService
    from pipe.core.services.session_turn_service import SessionTurnService


class VerificationService:
    """
    Handles the verification of session summaries by creating a temporary session
    and running a verifier agent.
    """

    def __init__(
        self,
        session_service: "SessionService",
        session_turn_service: "SessionTurnService",
        takt_agent: "TaktAgent",
    ):
        self.session_service = session_service
        self.session_turn_service = session_turn_service
        self.takt_agent = takt_agent

    def verify_summary(
        self,
        session_id: str,
        start_turn: int,
        end_turn: int,
        summary_text: str,
    ) -> dict:
        """
        Verifies a summary by creating a new temporary session for a sub-agent,
        and returns the verification status and the ID of the temporary session.

        Returns:            Dictionary containing verification result
        """
        verifier_session_id = None
        try:
            # === Step 1: Prepare the data for the verifier agent ===
            original_session_data = self.session_service.get_session(session_id)
            if not original_session_data:
                return {"error": f"Session with ID {session_id} not found."}

            original_turns = original_session_data.turns
            temp_turns = list(original_turns)

            summary_turn = CompressedHistoryTurn(
                type="compressed_history",
                content=summary_text,
                original_turns_range=[start_turn, end_turn],
                timestamp=get_current_timestamp(),
            )

            start_index = start_turn - 1
            end_index = end_turn - 1
            if not (
                0 <= start_index < len(temp_turns)
                and 0 <= end_index < len(temp_turns)
                and start_index <= end_index
            ):
                return {
                    "error": (
                        "Turn indices are out of range for creating "
                        "verification context."
                    )
                }

            del temp_turns[start_index : end_index + 1]
            temp_turns.insert(start_index, summary_turn)

            # === Step 2: Create a new, temporary session for verification ===
            verifier_purpose = f"Verification of summary for session {session_id}"
            verifier_background = (
                "A sub-agent will review a conversation history where a summary has "
                "been inserted. The agent must judge if the summary is a good "
                "replacement and respond with 'Approved:' or 'Rejected:'. "
                "The agent MUST strictly follow the rules in roles/verifier.md: "
                "Always return 'Approved:' or 'Rejected:' as the first line. "
                "If 'Rejected:', you MUST include the checklist and explicit "
                "reasons for each failed item as required by roles/verifier.md."
            )

            verifier_session = self.session_service.create_new_session(
                purpose=verifier_purpose,
                background=verifier_background,
                roles=["roles/verifier.md"],
                multi_step_reasoning_enabled=True,
            )
            verifier_session_id = verifier_session.session_id

            # Add the prepared history to the new verifier session
            verifier_session.turns = temp_turns
            self.session_service.repository.save(verifier_session)

            # === Step 3: Call the verifier agent using TaktAgent ===
            approved_text = "Please approve the summary."
            rejected_text = "Verification failed. Please modify the summary policy."
            verifier_instruction = (
                "## TASK\n"
                f"You are a verification agent. Your task is to verify the summary for "
                f"session {session_id} (turns {start_turn} to {end_turn}).\n\n"
                "You are reviewing a conversation history where a summary has been "
                "inserted. The summary marked as 'compressed_history' replaces the "
                f"original turns {start_turn} through {end_turn}.\n\n"
                "Judge if this summary is a good replacement (i.e., preserves "
                "context, flows logically).\n\n"
                "## STEP-BY-STEP INSTRUCTIONS\n"
                "1.  **Analyze**: Read the entire conversation history provided. A "
                "part of it is replaced by a summary marked as 'compressed_history'. "
                "Judge if this summary is a good replacement (i.e., preserves "
                "context, flows logically).\n"
                "2.  **Generate Response**: Based on your judgment, you MUST generate "
                "a response that starts with ONE of the following two prefixes: "
                "`Approved:` or `Rejected:`. Do not add any other text, explanation, "
                "or markdown fences before the prefix.\n\n"
                "## OUTPUT FORMATS\n\n"
                f"### Format 1: If your judgment is 'Yes' (Approved)\n"
                f"Your entire response must start with the exact phrase below.\n"
                f"`Approved: {approved_text}`\n\n"
                f"### Format 2: If your judgment is 'No' (Rejected)\n"
                "Your entire response must start with the exact phrase below, "
                "followed by a clear explanation of the reason for rejection.\n"
                f"`Rejected: {rejected_text}`\n"
                "## REJECTED REASON\n\n"
                "[Explain the reason for rejection here]"
            )

            try:
                stdout, stderr = self.takt_agent.run_existing_session(
                    session_id=verifier_session_id,
                    instruction=verifier_instruction,
                )
                # Log the output for debugging
                if stderr:
                    print(f"TaktAgent stderr: {stderr}", flush=True)
            except Exception as agent_error:
                # Extract stderr from CalledProcessError if available
                stderr_output = ""
                if isinstance(agent_error, subprocess.CalledProcessError):
                    stderr_output = agent_error.stderr or ""
                    stdout_output = agent_error.stdout or ""
                    error_detail = (
                        f"TaktAgent execution failed with exit code "
                        f"{agent_error.returncode}\n"
                        f"STDOUT:\n{stdout_output}\n"
                        f"STDERR:\n{stderr_output}"
                    )
                else:
                    error_detail = (
                        f"TaktAgent execution failed: {agent_error}\n"
                        f"{traceback.format_exc()}"
                    )

                return {"error": error_detail}

            # === Step 4: Get the response from verifier session ===
            verifier_session_data = self.session_service.get_session(
                verifier_session_id
            )
            response_text = ""
            if verifier_session_data and verifier_session_data.turns:
                # Find the last model_response turn
                for turn in reversed(verifier_session_data.turns):
                    if turn.type == "model_response":
                        response_text = turn.content.strip()
                        break

            # Check if we got a response
            if not response_text:
                turn_count = (
                    len(verifier_session_data.turns) if verifier_session_data else 0
                )
                return {
                    "error": (
                        f"No model_response found in verifier session "
                        f"{verifier_session_id}. "
                        f"Total turns: {turn_count}"
                    )
                }

            # === Step 5: Process result and construct the final turn content ===
            status = "rejected"
            final_turn_content = ""
            if response_text.startswith("Approved:"):
                status = "pending_approval"  # Force agent to wait for user
                final_turn_content = (
                    f"{response_text}\n\n## SUMMARY CONTENTS\n\n{summary_text}"
                )
            elif response_text.startswith("Rejected:"):
                final_turn_content = response_text
            else:
                final_turn_content = (
                    "Rejected: Verification failed. Please modify the summary "
                    "policy.\n\n"
                    "## REJECTED REASON\n\n"
                    "Verification response was not in the expected format:\n"
                    f"{response_text}"
                )

            # === Step 6: Return the result and the verifier session ID ===
            result = {
                "verification_status": status,
                "verifier_session_id": verifier_session_id,
                "message": (
                    f"Verification completed. Status: {status}. "
                    "Please follow the instruction in 'next_action'."
                ),
                "verifier_response": final_turn_content,
                "next_action": (
                    "STOP NOW. DO NOT EXECUTE COMPRESSION. "
                    "Report this result to the user and WAIT for their confirmation."
                ),
            }
            return result

        except Exception as e:
            return {
                "error": (
                    "An unexpected error occurred during summary verification: "
                    f"{e}\n{traceback.format_exc()}"
                )
            }
        finally:
            # Clean up the verifier session
            if verifier_session_id:
                self.session_service.delete_session(verifier_session_id)
