"""Unit tests for session_optimization domain logic."""

import json

from pipe.core.domains.session_optimization import (
    build_compressor_instruction,
    build_doctor_instruction,
    build_therapist_instruction,
    extract_summary_from_compressor_response,
    filter_valid_modifications,
    parse_doctor_result,
    parse_therapist_diagnosis,
)
from pipe.core.models.session_optimization import (
    DiagnosisData,
    DoctorResult,
    SessionModifications,
    TurnCompression,
    TurnEdit,
)


class TestBuildCompressorInstruction:
    """Tests for build_compressor_instruction function."""

    def test_build_compressor_instruction_format(self):
        """Test that the instruction contains all required parameters."""
        session_id = "test-session"
        policy = "summarize"
        target_length = 100
        start_turn = 1
        end_turn = 5

        instruction = build_compressor_instruction(
            session_id=session_id,
            policy=policy,
            target_length=target_length,
            start_turn=start_turn,
            end_turn=end_turn,
        )

        assert session_id in instruction
        assert policy in instruction
        assert str(target_length) in instruction
        assert f"turn {start_turn} to {end_turn}" in instruction
        assert 'get_session(session_id="test-session")' in instruction
        assert "verify_summary" in instruction


class TestBuildTherapistInstruction:
    """Tests for build_therapist_instruction function."""

    def test_build_therapist_instruction_format(self):
        """Test that the instruction contains session ID and turn count."""
        session_id = "diag-session"
        turns_count = 10

        instruction = build_therapist_instruction(session_id, turns_count)

        assert session_id in instruction
        assert str(turns_count) in instruction
        assert f"get_session(session_id='{session_id}')" in instruction


class TestBuildDoctorInstruction:
    """Tests for build_doctor_instruction function."""

    def test_build_doctor_instruction_with_adjustments(self):
        """Test that turn numbers are correctly adjusted based on deletions."""
        session_id = "mod-session"
        modifications = SessionModifications(
            deletions=[2, 4],
            edits=[
                TurnEdit(turn=3, new_content="Edited 3"),
                TurnEdit(turn=5, new_content="Edited 5"),
            ],
            compressions=[
                TurnCompression(start=3, end=5, reason="Comp 3-5"),
            ],
        )

        instruction = build_doctor_instruction(session_id, modifications)

        # Deletions: 2, 4
        # Edit turn 3: 3 - (1 deletion before 3) = 2
        # Edit turn 5: 5 - (2 deletions before 5) = 3
        # Compression 3-5: start 3-1=2, end 5-2=3

        assert (
            f"delete_session_turns(session_id='{session_id}', turns=[2, 4])"
            in instruction
        )
        assert (
            "edit_session_turn(session_id='mod-session', turn=2, new_content='Edited 3')"
            in instruction
        )
        assert (
            "edit_session_turn(session_id='mod-session', turn=3, new_content='Edited 5')"
            in instruction
        )
        assert (
            "compress_session_turns(session_id='mod-session', start_turn=2, end_turn=3, summary='Comp 3-5')"
            in instruction
        )

    def test_build_doctor_instruction_no_modifications(self):
        """Test instruction when no modifications are provided."""
        modifications = SessionModifications(deletions=[], edits=[], compressions=[])
        instruction = build_doctor_instruction("empty-session", modifications)
        assert "No modifications to apply. Output Succeeded." in instruction


class TestFilterValidModifications:
    """Tests for filter_valid_modifications function."""

    def test_filter_valid_modifications(self):
        """Test filtering of out-of-range turn indices."""
        modifications = SessionModifications(
            deletions=[1, 5, 10],
            edits=[
                TurnEdit(turn=2, new_content="Valid"),
                TurnEdit(turn=11, new_content="Invalid"),
            ],
            compressions=[
                TurnCompression(start=1, end=3, reason="Valid"),
                TurnCompression(start=8, end=12, reason="Invalid"),
            ],
        )
        turns_count = 5

        filtered = filter_valid_modifications(modifications, turns_count)

        assert filtered.deletions == [1, 5]
        assert len(filtered.edits) == 1
        assert filtered.edits[0].turn == 2
        assert len(filtered.compressions) == 1
        assert filtered.compressions[0].start == 1
        assert filtered.compressions[0].end == 3


class TestExtractSummaryFromCompressorResponse:
    """Tests for extract_summary_from_compressor_response function."""

    def test_extract_approved_with_backticks(self):
        """Test extraction from an approved response with backticked ID."""
        content = """
Approved: Summary looks good.

## SUMMARY CONTENTS
This is the summary text.

Verifier Session ID: `verifier-123`
"""
        summary, verifier_id = extract_summary_from_compressor_response(content)
        assert summary == "Approved: This is the summary text."
        assert verifier_id == "verifier-123"

    def test_extract_approved_without_backticks(self):
        """Test extraction from an approved response without backticks."""
        content = """
Approved: OK
## SUMMARY CONTENTS
Summary here
Verifier Session ID: verifier-456
"""
        summary, verifier_id = extract_summary_from_compressor_response(content)
        assert summary == "Approved: Summary here"
        assert verifier_id == "verifier-456"

    def test_extract_rejected(self):
        """Test handling of rejected responses."""
        content = "Rejected: Too long."
        summary, verifier_id = extract_summary_from_compressor_response(content)
        assert summary == "Rejected: Too long."
        assert verifier_id is None

    def test_extract_invalid_format(self):
        """Test handling of invalid response formats."""
        content = "Something else entirely."
        summary, verifier_id = extract_summary_from_compressor_response(content)
        assert summary == ""
        assert verifier_id is None

    def test_extract_missing_summary_marker(self):
        """Test handling of approved response missing summary marker."""
        content = "Approved: But no marker."
        summary, verifier_id = extract_summary_from_compressor_response(content)
        assert summary == ""
        assert verifier_id is None


class TestParseTherapistDiagnosis:
    """Tests for parse_therapist_diagnosis function."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON diagnosis."""
        data = {
            "summary": "Test summary",
            "deletions": [1],
            "edits": [{"turn": 2, "newContent": "New"}],
            "compressions": [{"start": 3, "end": 4, "reason": "Reason"}],
        }
        content = f"```json\n{json.dumps(data)}\n```"
        result = parse_therapist_diagnosis(content)

        assert isinstance(result, DiagnosisData)
        assert result.summary == "Test summary"
        assert result.deletions == [1]
        assert result.edits[0].turn == 2
        assert result.compressions[0].reason == "Reason"

    def test_parse_json_missing_summary(self):
        """Test parsing JSON missing the summary field."""
        data = {"deletions": [1]}
        result = parse_therapist_diagnosis(json.dumps(data))
        assert result.summary == "Analysis completed"
        assert result.deletions == [1]

    def test_parse_non_json(self):
        """Test fallback for non-JSON content."""
        content = "This is just text advice."
        result = parse_therapist_diagnosis(content)
        assert result.summary == "This is just text advice."
        assert result.raw_diagnosis == content


class TestParseDoctorResult:
    """Tests for parse_doctor_result function."""

    def test_parse_valid_json_succeeded(self):
        """Test parsing valid JSON result for success."""
        data = {
            "status": "Succeeded",
            "appliedDeletions": [1],
            "appliedEdits": [{"turn": 2, "newContent": "Fixed"}],
            "appliedCompressions": [{"start": 3, "end": 4, "reason": "Done"}],
        }
        content = f"```json\n{json.dumps(data)}\n```"
        result = parse_doctor_result(content)

        assert isinstance(result, DoctorResult)
        assert result.status == "Succeeded"
        assert result.applied_deletions == [1]
        assert result.applied_edits[0].turn == 2
        assert result.applied_compressions[0].start == 3

    def test_parse_valid_json_failed(self):
        """Test parsing valid JSON result for failure."""
        data = {"status": "Failed", "reason": "Tool error"}
        result = parse_doctor_result(json.dumps(data))
        assert result.status == "Failed"
        assert result.reason == "Tool error"

    def test_parse_non_json_succeeded(self):
        """Test fallback for non-JSON success message."""
        result = parse_doctor_result("The operation Succeeded.")
        assert result.status == "Succeeded"

    def test_parse_non_json_failed(self):
        """Test fallback for non-JSON failure message."""
        result = parse_doctor_result("It Failed because of something.")
        assert result.status == "Failed"
        assert "It Failed" in result.reason

    def test_parse_unknown(self):
        """Test fallback for unknown response."""
        result = parse_doctor_result("Maybe it worked?")
        assert result.status == "Unknown"
        assert result.reason == "Maybe it worked?"

    def test_parse_malformed_items(self):
        """Test parsing when items in lists are not dicts."""
        data = {
            "status": "Succeeded",
            "appliedEdits": ["not a dict"],
            "appliedCompressions": [None],
        }
        result = parse_doctor_result(json.dumps(data))
        assert result.applied_edits[0].turn == 0
        assert result.applied_compressions[0].start == 0
