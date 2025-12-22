import pytest
from pipe.core.models.session_optimization import (
    DiagnosisData,
    DoctorResult,
    SessionModifications,
    TurnCompression,
    TurnEdit,
)
from pydantic import ValidationError


class TestSessionOptimizationModels:
    """Tests for session optimization models."""

    def test_turn_edit_creation_and_aliases(self):
        """Test TurnEdit validation and camelCase alias handling."""
        edit = TurnEdit(turn=1, new_content="updated content")
        assert edit.turn == 1
        assert edit.new_content == "updated content"

        # Test serialization to camelCase
        dumped = edit.model_dump(by_alias=True)
        assert dumped["turn"] == 1
        assert dumped["newContent"] == "updated content"

        # Test deserialization from camelCase
        validated = TurnEdit.model_validate({"turn": 2, "newContent": "more content"})
        assert validated.turn == 2
        assert validated.new_content == "more content"

    def test_turn_compression_defaults(self):
        """Test TurnCompression defaults and validation."""
        comp = TurnCompression(start=1, end=5)
        assert comp.start == 1
        assert comp.end == 5
        assert comp.reason == ""

        # Test with reason
        comp_with_reason = TurnCompression(start=2, end=3, reason="too long")
        assert comp_with_reason.reason == "too long"

    def test_session_modifications_validation(self):
        """Test SessionModifications with nested models."""
        data = {
            "deletions": [1, 2],
            "edits": [{"turn": 3, "newContent": "edit 3"}],
            "compressions": [{"start": 4, "end": 6, "reason": "summary"}],
        }
        mods = SessionModifications.model_validate(data)
        assert mods.deletions == [1, 2]
        assert len(mods.edits) == 1
        assert isinstance(mods.edits[0], TurnEdit)
        assert mods.edits[0].new_content == "edit 3"
        assert len(mods.compressions) == 1
        assert mods.compressions[0].start == 4

    def test_doctor_result_serialization(self):
        """Test DoctorResult full serialization cycle."""
        result = DoctorResult(
            status="success",
            reason="cleaned up",
            applied_deletions=[10],
            applied_edits=[TurnEdit(turn=11, new_content="fixed")],
            applied_compressions=[],
        )

        dumped = result.model_dump(by_alias=True)
        assert dumped["status"] == "success"
        assert dumped["appliedDeletions"] == [10]
        assert dumped["appliedEdits"][0]["newContent"] == "fixed"
        assert dumped["appliedCompressions"] == []

    def test_diagnosis_data_defaults(self):
        """Test DiagnosisData default factories and optional fields."""
        diag = DiagnosisData()
        assert diag.summary == ""
        assert diag.deletions == []
        assert diag.edits == []
        assert diag.compressions == []
        assert diag.raw_diagnosis == ""

        # Verify list factories create new instances
        diag2 = DiagnosisData()
        diag.deletions.append(1)
        assert len(diag2.deletions) == 0

    def test_validation_errors(self):
        """Test that invalid types raise ValidationError."""
        with pytest.raises(ValidationError):
            # turn must be int
            TurnEdit(turn="not-an-int", new_content="test")

        with pytest.raises(ValidationError):
            # edits must be a list of TurnEdit or dicts
            SessionModifications(deletions=[], edits="not-a-list", compressions=[])

    def test_roundtrip_serialization(self):
        """Test roundtrip serialization/deserialization."""
        original = DiagnosisData(
            summary="Test diagnosis",
            deletions=[1, 2, 3],
            edits=[TurnEdit(turn=4, new_content="fixed content")],
            compressions=[TurnCompression(start=5, end=10, reason="too much noise")],
            raw_diagnosis="Found some issues in turns 1-10.",
        )

        # Serialize
        json_data = original.model_dump_json(by_alias=True)

        # Deserialize
        restored = DiagnosisData.model_validate_json(json_data)

        assert restored == original
        assert restored.edits[0].new_content == "fixed content"
        assert restored.compressions[0].reason == "too much noise"
