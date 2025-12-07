"""
Service for session optimization operations.

Handles compression, therapist diagnosis, and doctor modifications.
These operations create shadow sessions to analyze and optimize target sessions.
"""

from typing import TYPE_CHECKING, Any

from pipe.core.agents.takt_agent import TaktAgent
from pipe.core.domains.session_optimization import (
    DiagnosisData,
    build_compressor_instruction,
    build_doctor_instruction,
    build_therapist_instruction,
    extract_summary_from_compressor_response,
    filter_valid_modifications,
    parse_doctor_result,
    parse_therapist_diagnosis,
)
from pipe.core.models.turn import CompressedHistoryTurn
from pipe.core.utils.datetime import get_current_timestamp
from pydantic import BaseModel

if TYPE_CHECKING:
    from pipe.core.services.session_service import SessionService


class TherapistResult(BaseModel):
    session_id: str
    diagnosis: DiagnosisData


class CompressorResult(BaseModel):
    session_id: str
    summary: str
    verifier_session_id: str


class SessionOptimizationService:
    """Service for session optimization workflows.

    This service orchestrates:
    - Compression: Summarize turn ranges to reduce token usage
    - Therapist: Diagnose sessions and suggest optimizations
    - Doctor: Apply approved modifications from therapist

    All operations create shadow sessions that are deleted after use.
    """

    def __init__(
        self,
        project_root: str,
        session_service: "SessionService",
    ):
        """Initialize the service.

        Args:
            project_root: Path to the project root directory
            session_service: Session service for session operations
        """
        self.project_root = project_root
        self.session_service = session_service
        self.takt_agent = TaktAgent(project_root)

    # =========================================================================
    # Compression Operations
    # =========================================================================

    def run_compression(
        self,
        session_id: str,
        policy: str,
        target_length: int,
        start_turn: int,
        end_turn: int,
    ) -> CompressorResult:
        """Create compressor session and run initial takt command.

        Args:
            session_id: Target session ID to compress
            policy: Compression policy
            target_length: Target length after compression
            start_turn: Start turn index (1-based)
            end_turn: End turn index (1-based)

        Returns:
            Dict with session_id, summary, and verifier_session_id
        """
        instruction = build_compressor_instruction(
            session_id, policy, target_length, start_turn, end_turn
        )

        compressor_session_id, _, _ = self.takt_agent.run_new_session(
            purpose=(
                "Act as a compression agent to summarize the target session "
                "according to the specified request"
            ),
            background=(
                "Responsible for compressing conversation history and creating "
                "summaries based on the specified policy and target length"
            ),
            roles="roles/compressor.md",
            instruction=instruction,
        )

        # Reload the session to get the summary
        session = self.session_service.get_session(compressor_session_id)
        if not session or not session.turns:
            raise ValueError("Session or turns not found after creation")

        # Find the last model_response
        last_model_response = None
        for turn in reversed(session.turns):
            if turn.type == "model_response":
                last_model_response = turn
                break

        summary = ""
        verifier_session_id = None
        if last_model_response:
            summary, verifier_session_id = extract_summary_from_compressor_response(
                last_model_response.content
            )

        return CompressorResult(
            session_id=compressor_session_id,
            summary=summary,
            verifier_session_id=verifier_session_id or "",
        )

    def approve_compression(self, compressor_session_id: str) -> None:
        """Approve the compression by running takt with approval instruction.

        Args:
            compressor_session_id: The compressor session ID
        """
        approval_instruction = (
            "The user has approved the compression. "
            "Proceed with replacing the session turns using the "
            "replace_session_turns tool."
        )

        self.takt_agent.run_existing_session(
            compressor_session_id, approval_instruction
        )

        # Delete the compressor session after approval
        self.session_service.delete_session(compressor_session_id)

    def deny_compression(self, compressor_session_id: str) -> None:
        """Deny the compression and clean up the compressor session.

        Args:
            compressor_session_id: The compressor session ID
        """
        self.session_service.delete_session(compressor_session_id)

    def replace_turn_range_with_summary(
        self, session_id: str, summary: str, start_index: int, end_index: int
    ) -> None:
        """Replace a range of turns with a summary.

        Args:
            session_id: Target session ID
            summary: Summary content to replace turns with
            start_index: Start turn index (0-based)
            end_index: End turn index (0-based)
        """
        session = self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if (
            start_index < 0
            or end_index >= len(session.turns)
            or start_index > end_index
        ):
            raise ValueError("Invalid turn range")

        compressed_turn = CompressedHistoryTurn(
            type="compressed_history",
            content=summary,
            original_turns_range=[start_index + 1, end_index + 1],  # 1-based
            timestamp=get_current_timestamp(),
        )

        # Replace the range with the compressed turn
        session.turns = (
            session.turns[:start_index]
            + [compressed_turn]
            + session.turns[end_index + 1 :]
        )

        # Save the session
        self.session_service.repository.save(session)

    # =========================================================================
    # Therapist Operations
    # =========================================================================

    def run_therapist(self, session_id: str) -> TherapistResult:
        """Create therapist session and run initial takt command.

        Args:
            session_id: Target session ID to diagnose

        Returns:
            TherapistResult with session_id and diagnosis
        """
        # Get turns count
        session = self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        turns_count = len(session.turns)

        instruction = build_therapist_instruction(session_id, turns_count)

        therapist_session_id = None
        try:
            therapist_session_id, stdout, stderr = self.takt_agent.run_new_session(
                purpose=(
                    "Act as a therapist agent to diagnose the target session "
                    "and suggest optimizations"
                ),
                background=(
                    "Responsible for analyzing conversation sessions, identifying "
                    "issues, and providing actionable advice for edits, deletions, "
                    "and compressions"
                ),
                roles="roles/therapist.md",
                instruction=instruction,
                multi_step_reasoning=True,
            )

            # Reload the session to get the diagnosis
            session = self.session_service.get_session(therapist_session_id)
            if not session or not session.turns:
                raise ValueError("Session or turns not found after creation")

            # Find the last model_response
            last_model_response = None
            for turn in reversed(session.turns):
                if turn.type == "model_response":
                    last_model_response = turn
                    break

            diagnosis_data = {}
            if last_model_response:
                diagnosis_data = parse_therapist_diagnosis(last_model_response.content)

            return TherapistResult(
                session_id=therapist_session_id,
                diagnosis=diagnosis_data,
            )
        finally:
            # Delete the therapist session as it's a shadow session
            if therapist_session_id:
                self.session_service.delete_session(therapist_session_id)

    # =========================================================================
    # Doctor Operations
    # =========================================================================

    def run_doctor(
        self, session_id: str, modifications: dict[str, Any]
    ) -> dict[str, Any]:
        """Create doctor session and run modifications.

        Args:
            session_id: Target session ID to modify
            modifications: Dict containing deletions, edits, compressions

        Returns:
            Dict with session_id and result
        """
        # Get session to validate turn numbers
        session = self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        turns_count = len(session.turns)

        # Filter invalid modifications
        valid_modifications = filter_valid_modifications(modifications, turns_count)

        instruction = build_doctor_instruction(session_id, valid_modifications)

        doctor_session_id = None
        try:
            doctor_session_id, stdout, stderr = self.takt_agent.run_new_session(
                purpose=(
                    "Act as a doctor agent to apply approved modifications "
                    "to the target session"
                ),
                background=(
                    "Responsible for executing deletions, edits, and compressions "
                    "approved by the therapist"
                ),
                roles="roles/doctor.md",
                instruction=instruction,
                multi_step_reasoning=True,
            )

            # Reload the session to get the result
            session = self.session_service.get_session(doctor_session_id)
            if not session or not session.turns:
                raise ValueError("Session or turns not found after creation")

            # Find the last model_response
            last_model_response = None
            for turn in reversed(session.turns):
                if turn.type == "model_response":
                    last_model_response = turn
                    break

            result = {"status": "Failed", "reason": "No response"}
            if last_model_response:
                result = parse_doctor_result(last_model_response.content)

            return {
                "session_id": doctor_session_id,
                "result": result,
            }
        finally:
            # Delete the doctor session as it's a shadow session
            if doctor_session_id:
                self.session_service.delete_session(doctor_session_id)
