"""Tests for verification result models."""

import pytest
from pipe.core.models.results.verification_result import (
    VerificationError,
    VerificationResult,
)
from pydantic import ValidationError

from tests.factories.models.results.results_factory import ResultFactory


class TestVerificationResult:
    """Tests for VerificationResult model."""

    def test_valid_verification_result_creation(self):
        """Test creating a valid VerificationResult with all fields."""
        result = ResultFactory.create_verification_result(
            verification_status="pending_approval",
            verifier_session_id="session-123",
            message="Test message",
            verifier_response="Verifier response",
            next_action="Next action",
        )
        assert result.verification_status == "pending_approval"
        assert result.verifier_session_id == "session-123"
        assert result.message == "Test message"
        assert result.verifier_response == "Verifier response"
        assert result.next_action == "Next action"

    def test_verification_result_validation_error_invalid_status(self):
        """Test that invalid verification_status raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            VerificationResult(
                verification_status="invalid_status",  # type: ignore
                verifier_session_id="session-123",
                verifier_response="Verifier response",
                next_action="Next action",
            )
        assert "verification_status" in str(exc_info.value)
        assert "Input should be 'pending_approval' or 'rejected'" in str(exc_info.value)

    def test_verification_result_validation_error_missing_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            VerificationResult(
                verification_status="pending_approval",
                # missing verifier_session_id
                verifier_response="Verifier response",
                next_action="Next action",
            )
        assert "verifierSessionId" in str(exc_info.value)

    def test_verification_result_serialization(self):
        """Test serialization and deserialization (snake_case <-> camelCase)."""
        original = ResultFactory.create_verification_result(
            verification_status="rejected",
            verifier_session_id="session-456",
        )

        # model_dump(by_alias=True) should return camelCase
        dumped = original.model_dump(by_alias=True)
        assert dumped["verificationStatus"] == "rejected"
        assert dumped["verifierSessionId"] == "session-456"
        assert dumped["verifierResponse"] == "Looks good"
        assert dumped["nextAction"] == "Proceed with caution"

        # Roundtrip: deserialize back
        restored = VerificationResult.model_validate(dumped)
        assert restored == original

    def test_verification_result_immutability(self):
        """Test that VerificationResult is frozen (immutable)."""
        result = ResultFactory.create_verification_result()
        with pytest.raises(ValidationError):
            # Pydantic V2 raises ValidationError when trying to set attribute
            # of frozen model via __setattr__ if configured.
            # It usually raises ValidationError if using model_validate
            # or AttributeError if direct assignment, but here we expect
            # validation error as per Pydantic configuration.
            result.message = "New message"  # type: ignore


class TestVerificationError:
    """Tests for VerificationError model."""

    def test_valid_verification_error_creation(self):
        """Test creating a valid VerificationError."""
        error = ResultFactory.create_verification_error(error="Something went wrong")
        assert error.error == "Something went wrong"

    def test_verification_error_validation_error_missing_field(self):
        """Test that missing error field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            VerificationError()  # type: ignore
        assert "error" in str(exc_info.value)

    def test_verification_error_serialization(self):
        """Test serialization and deserialization."""
        original = ResultFactory.create_verification_error(error="Critical failure")
        dumped = original.model_dump(by_alias=True)
        assert dumped["error"] == "Critical failure"

        restored = VerificationError.model_validate(dumped)
        assert restored == original

    def test_verification_error_immutability(self):
        """Test that VerificationError is frozen."""
        error = ResultFactory.create_verification_error()
        with pytest.raises(ValidationError):
            error.error = "New error"  # type: ignore
