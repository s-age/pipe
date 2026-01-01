"""
Domain logic for session optimization (compression, therapist, doctor).

This module contains pure functions for building instructions and
processing optimization results.
"""

from pipe.core.models.session_optimization import (
    DiagnosisData,
    DoctorResult,
    SessionModifications,
    TurnCompression,
    TurnEdit,
)


def build_compressor_instruction(
    session_id: str,
    policy: str,
    target_length: int,
    start_turn: int,
    end_turn: int,
) -> str:
    """Build the instruction for compressor session.

    Args:
        session_id: Target session ID to compress
        policy: Compression policy
        target_length: Target length after compression
        start_turn: Start turn index (1-based, converted to 0-based internally)
        end_turn: End turn index (1-based, converted to 0-based internally)

    Returns:
        Instruction string for the compressor agent
    """
    return f"""Compress session {session_id} from turn {start_turn} to {end_turn} \
with policy '{policy}' and target length {target_length} tokens.

**Execute the following steps in order:**

**Step 1: Retrieve the target session**
Call the get_session tool with this exact parameter:
```
get_session(session_id="{session_id}")
```

**Step 2: Generate summary**
Based on the session data (turns {start_turn} to {end_turn}), create a summary \
following the policy '{policy}' with target length {target_length} tokens.

**Step 3: Verify the summary**
Call the verify_summary tool with these exact parameters:
```
verify_summary(
    session_id="{session_id}",
    start_turn={start_turn},
    end_turn={end_turn},
    summary_text="<YOUR GENERATED SUMMARY HERE>"
)
```

**Step 4: Report the result and STOP**
Use the output format specified in your role definition.
Output the verification result and wait for user approval.

**CRITICAL: DO NOT call compress_session_turns in this session.**
That tool will only be called after the user explicitly approves the summary \
in a separate instruction.
"""


def build_therapist_instruction(session_id: str, turns_count: int) -> str:
    """Build the instruction for therapist session.

    Args:
        session_id: Target session ID to diagnose
        turns_count: Number of turns in the session

    Returns:
        Instruction string for the therapist agent
    """
    return (
        f"Diagnose the TARGET SESSION with ID: {session_id} "
        f"which has exactly {turns_count} turns. "
        f"IMPORTANT: Always use session_id='{session_id}' in all tool calls. "
        f"This is the target session to diagnose, NOT your own session.\n\n"
        f"First, call get_session(session_id='{session_id}') "
        f"to retrieve the session data.\n\n"
        f"Then, provide advice on edits, deletions, and compressions. "
        f"All suggested turn numbers must be between 1 and {turns_count} "
        f"inclusive. "
        f"Do not suggest any operations on turns outside this range."
    )


def build_doctor_instruction(
    session_id: str, modifications: SessionModifications
) -> str:
    """Build the instruction for doctor session.

    Args:
        session_id: Target session ID to modify
        modifications: Pydantic model containing deletions, edits, compressions

    Returns:
        Instruction string for the doctor agent
    """
    deletions = modifications.deletions
    edits = modifications.edits
    compressions = modifications.compressions

    # Adjust edits and compressions for deletions
    deletions_set = sorted(set(deletions))
    adjusted_edits = []
    for edit in edits:
        turn = edit.turn
        adjusted_turn = turn - sum(1 for d in deletions_set if d < turn)
        adjusted_edits.append(
            TurnEdit(turn=adjusted_turn, new_content=edit.new_content)
        )

    adjusted_compressions = []
    for comp in compressions:
        start_turn = comp.start
        end_turn = comp.end
        adjusted_start = start_turn - sum(1 for d in deletions_set if d < start_turn)
        adjusted_end = end_turn - sum(1 for d in deletions_set if d < end_turn)
        adjusted_compressions.append(
            TurnCompression(start=adjusted_start, end=adjusted_end, reason=comp.reason)
        )

    instruction = (
        f"Apply the following approved modifications to the TARGET SESSION "
        f"with ID: {session_id}\n\n"
    )
    instruction += (
        f"IMPORTANT: Always use session_id='{session_id}' in all tool calls. "
        f"This is the target session to modify, NOT your own session.\n\n"
    )

    if deletions:
        instruction += (
            f"delete_session_turns(session_id='{session_id}', " f"turns={deletions})\n"
        )
    for edit in adjusted_edits:
        instruction += (
            f"edit_session_turn(session_id='{session_id}', turn={edit.turn}, "
            f"new_content='{edit.new_content}')\n"
        )
    for comp in adjusted_compressions:
        instruction += (
            f"compress_session_turns(session_id='{session_id}', "
            f"start_turn={comp.start}, end_turn={comp.end}, "
            f"summary='{comp.reason}')\n"
        )

    if not deletions and not adjusted_edits and not adjusted_compressions:
        instruction += "No modifications to apply. Output Succeeded.\n"
    else:
        instruction += "\nExecute these tool calls in the order listed above."

    instruction += (
        f"\nCRITICAL: Do NOT use your own session ID. "
        f"Always use session_id='{session_id}' for the target session."
    )

    return instruction


def filter_valid_modifications(
    modifications: SessionModifications, turns_count: int
) -> SessionModifications:
    """Filter modifications to only include valid turn indices.

    Args:
        modifications: Pydantic model containing deletions, edits, compressions
        turns_count: Total number of turns in the session

    Returns:
        Filtered modifications model
    """
    deletions = modifications.deletions
    edits = modifications.edits
    compressions = modifications.compressions

    valid_deletions = [d for d in deletions if 1 <= d <= turns_count]
    valid_edits = [e for e in edits if 1 <= e.turn <= turns_count]
    valid_compressions = [
        c for c in compressions if 1 <= c.start <= c.end <= turns_count
    ]

    return SessionModifications(
        deletions=valid_deletions,
        edits=valid_edits,
        compressions=valid_compressions,
    )


def extract_summary_from_compressor_response(content: str) -> tuple[str, str | None]:
    """Extract summary and verifier session ID from compressor response.

    The compressor agent MUST output in a format starting with "Approved:" or
    "Rejected:". This is enforced by roles/compressor.md and Python will reject
    any other format.

    Expected format (Approved):
        Approved: [message]

        ## SUMMARY CONTENTS
        {summary_text}

        Verifier Session ID: `{session_id}`

    Expected format (Rejected):
        Rejected: [rejection reason and details]

    Args:
        content: Model response content

    Returns:
        Tuple of (summary_or_message, verifier_session_id)
        - For Approved: (summary_text, verifier_session_id)
        - For Rejected: (full_rejected_message, None)
        - For invalid format: ("", None)
    """
    content = content.strip()

    # Handle Rejected responses
    if content.startswith("Rejected:"):
        # Return the full rejection message as the "summary"
        return content, None

    # Must start with "Approved:" to be valid for extraction
    if not content.startswith("Approved:"):
        return "", None

    summary = ""
    verifier_session_id = None

    # Extract summary after ## SUMMARY CONTENTS
    summary_marker = "## SUMMARY CONTENTS"
    summary_start = content.find(summary_marker)
    if summary_start == -1:
        return "", None

    summary_text = content[summary_start + len(summary_marker) :].strip()

    # Extract Verifier Session ID
    verifier_marker = "Verifier Session ID:"
    verifier_id_start = summary_text.find(verifier_marker)
    if verifier_id_start != -1:
        verifier_line = summary_text[verifier_id_start + len(verifier_marker) :].strip()
        # Extract ID from backticks if present
        if verifier_line.startswith("`"):
            end = verifier_line.find("`", 1)
            if end != -1:
                verifier_session_id = verifier_line[1:end]
        else:
            # Take first word as ID
            verifier_session_id = verifier_line.split()[0] if verifier_line else None

        # Remove the Verifier Session ID line and everything after from summary
        summary_text = summary_text[:verifier_id_start].strip()

    # Prepend "Approved: " to match client expectation
    summary = f"Approved: {summary_text}"

    return summary, verifier_session_id


def parse_therapist_diagnosis(content: str) -> DiagnosisData:
    """Parse therapist diagnosis from response content.

    Args:
        content: Model response content (possibly JSON)

    Returns:
        Parsed diagnosis Pydantic model
    """
    import json

    diagnosis = content.strip()

    # Remove markdown code block formatting if present
    if diagnosis.startswith("```json"):
        diagnosis = diagnosis[7:]  # Remove ```json
    if diagnosis.endswith("```"):
        diagnosis = diagnosis[:-3]  # Remove ```
    diagnosis = diagnosis.strip()

    try:
        diagnosis_data = json.loads(diagnosis)
        # Ensure summary is present
        if "summary" not in diagnosis_data:
            diagnosis_data["summary"] = "Analysis completed"
        return DiagnosisData(**diagnosis_data)
    except json.JSONDecodeError:
        # If not JSON, wrap in a basic structure
        return DiagnosisData(
            summary=diagnosis or "No analysis provided",
            deletions=[],
            edits=[],
            compressions=[],
            raw_diagnosis=diagnosis,
        )


def parse_doctor_result(content: str) -> DoctorResult:
    """Parse doctor result from response content.

    Args:
        content: Model response content

    Returns:
        Parsed result dict with status, reason, and applied modifications
    """
    import json
    import re

    content = content.strip()

    # Remove markdown code blocks if present
    code_block_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", content, re.DOTALL)
    if code_block_match:
        content = code_block_match.group(1).strip()

    try:
        doctor_result = json.loads(content)
        status = doctor_result.get("status", "Unknown")
        reason = ""
        if status == "Failed":
            reason = doctor_result.get("reason", content)

        # Convert applied_edits to TurnEdit objects
        # Support both camelCase (from LLM) and snake_case
        applied_edits_data = doctor_result.get(
            "appliedEdits", doctor_result.get("applied_edits", [])
        )
        applied_edits = [
            (
                TurnEdit(**edit)
                if isinstance(edit, dict)
                else TurnEdit(turn=0, new_content="")
            )
            for edit in applied_edits_data
        ]

        # Convert applied_compressions to TurnCompression objects
        applied_compressions_data = doctor_result.get(
            "appliedCompressions", doctor_result.get("applied_compressions", [])
        )
        applied_compressions = [
            (
                TurnCompression(**comp)
                if isinstance(comp, dict)
                else TurnCompression(start=0, end=0)
            )
            for comp in applied_compressions_data
        ]

        return DoctorResult(
            status=status,
            reason=reason,
            applied_deletions=doctor_result.get(
                "appliedDeletions", doctor_result.get("applied_deletions", [])
            ),
            applied_edits=applied_edits,
            applied_compressions=applied_compressions,
        )
    except json.JSONDecodeError:
        # Fallback to string matching
        if "Succeeded" in content:
            status = "Succeeded"
            reason = ""
        elif "Failed" in content:
            status = "Failed"
            reason = content
        else:
            status = "Unknown"
            reason = content

        return DoctorResult(
            status=status,
            reason=reason,
            applied_deletions=[],
            applied_edits=[],
            applied_compressions=[],
        )
