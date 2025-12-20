"""
Service for session optimization operations.

Handles compression, therapist diagnosis, and doctor modifications.
These operations create shadow sessions to analyze and optimize target sessions.
"""

from pipe.core.agents.takt_agent import TaktAgent
from pipe.core.domains.session_optimization import (
    DiagnosisData,
    DoctorResult,
    SessionModifications,
    build_compressor_instruction,
    build_doctor_instruction,
    build_therapist_instruction,
    extract_summary_from_compressor_response,
    filter_valid_modifications,
    parse_doctor_result,
    parse_therapist_diagnosis,
)
from pipe.core.models.base import CamelCaseModel
from pipe.core.models.turn import CompressedHistoryTurn
from pipe.core.utils.datetime import get_current_timestamp


class TherapistResult(CamelCaseModel):
    session_id: str
    diagnosis: DiagnosisData


class CompressorResult(CamelCaseModel):
    session_id: str
    summary: str
    verifier_session_id: str


class DoctorResultResponse(CamelCaseModel):
    session_id: str
    result: DoctorResult


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
        takt_agent: TaktAgent,
        repository=None,
    ):
        """Initialize the service.

        Args:
            project_root: Path to the project root directory
            takt_agent: Agent for running optimization sessions
            repository: SessionRepository for persistence
        """
        self.project_root = project_root
        self.repository = repository
        self.takt_agent = takt_agent

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

        # Embed compression parameters in background for later retrieval
        background = (
            f"Responsible for compressing conversation history and creating "
            f"summaries based on the specified policy and target length. "
            f"Target session: {session_id}, turns {start_turn}-{end_turn}"
        )

        compressor_session_id, _, _ = self.takt_agent.run_new_session(
            purpose=(
                "Act as a compression agent to summarize the target session "
                "according to the specified request"
            ),
            background=background,
            roles="roles/compressor.md",
            instruction=instruction,
        )

        # Reload the session to get the summary
        session = self.repository.find(compressor_session_id)
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
        # Retrieve the compressor session to extract original parameters
        compressor_session = self.repository.find(compressor_session_id)
        if not compressor_session or not compressor_session.turns:
            raise ValueError(
                f"Compressor session {compressor_session_id} not found or has no turns"
            )

        # Extract parameters from the session's background field
        import re

        if not compressor_session.background:
            raise ValueError(
                f"No background found in compressor session {compressor_session_id}"
            )

        # Parse the background to extract session_id, start_turn, end_turn
        # Format: "... Target session: {session_id}, turns {start_turn}-{end_turn}"
        match = re.search(
            r"Target session: (\S+), turns (\d+)-(\d+)",
            compressor_session.background,
        )
        if not match:
            raise ValueError(
                f"Could not parse compression parameters from background: "
                f"{compressor_session.background}"
            )

        target_session_id = match.group(1)
        start_turn = int(match.group(2))
        end_turn = int(match.group(3))

        # Extract the summary from the last model_response
        last_model_response = None
        for turn in reversed(compressor_session.turns):
            if turn.type == "model_response":
                last_model_response = turn
                break

        if not last_model_response:
            raise ValueError(
                f"No model_response found in compressor session {compressor_session_id}"
            )

        from pipe.core.domains.session_optimization import (
            extract_summary_from_compressor_response,
        )

        summary, _ = extract_summary_from_compressor_response(
            last_model_response.content
        )

        if not summary or summary.startswith("Rejected:"):
            raise ValueError(
                f"Cannot approve: summary was not approved or is empty: {summary}"
            )

        # Extract clean summary text (remove "Approved: " prefix if present)
        clean_summary = summary.replace("Approved: ", "").strip()

        # Escape the summary for use in tool call parameter
        # Replace double quotes with escaped quotes and handle newlines
        escaped_summary = clean_summary.replace('"', '\\"').replace("\n", "\\n")

        # Build detailed approval instruction with exact tool call
        # (using 1-based turn numbers)
        approval_instruction = f"""The user has approved the compression.

**Execute this exact tool call:**
```
compress_session_turns(
    session_id="{target_session_id}",
    start_turn={start_turn},
    end_turn={end_turn},
    summary_text="{escaped_summary}"
)
```

After executing the tool call successfully, report completion and stop.
"""

        self.takt_agent.run_existing_session(
            compressor_session_id, approval_instruction
        )

        # Delete the compressor session after approval
        self.repository.delete(compressor_session_id)

    def deny_compression(self, compressor_session_id: str) -> None:
        """Deny the compression and clean up the compressor session.

        Args:
            compressor_session_id: The compressor session ID
        """
        self.repository.delete(compressor_session_id)

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
        session = self.repository.find(session_id)
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
        self.repository.save(session)

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
        session = self.repository.find(session_id)
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
            session = self.repository.find(therapist_session_id)
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
                self.repository.delete(therapist_session_id)

    # =========================================================================
    # Doctor Operations
    # =========================================================================

    def run_doctor(
        self, session_id: str, modifications: SessionModifications
    ) -> DoctorResultResponse:
        """Create doctor session and run modifications.

        Args:
            session_id: Target session ID to modify
            modifications: Dict containing deletions, edits, compressions

        Returns:
            DoctorResultResponse with session_id and result
        """
        # Get session to validate turn numbers
        session = self.repository.find(session_id)
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
            session = self.repository.find(doctor_session_id)
            if not session or not session.turns:
                raise ValueError("Session or turns not found after creation")

            # Find the last model_response
            last_model_response = None
            for turn in reversed(session.turns):
                if turn.type == "model_response":
                    last_model_response = turn
                    break

            result = DoctorResult(
                status="Failed",
                reason="No response",
                applied_deletions=[],
                applied_edits=[],
                applied_compressions=[],
            )
            if last_model_response:
                result = parse_doctor_result(last_model_response.content)

            return DoctorResultResponse(
                session_id=doctor_session_id,
                result=result,
            )
        finally:
            # Delete the doctor session as it's a shadow session
            if doctor_session_id:
                self.repository.delete(doctor_session_id)
