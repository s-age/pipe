"""
Unit tests for start_session validator.
"""

import pytest
from pipe.core.validators.sessions.start_session import validate


class TestStartSessionValidator:
    """Tests for the start_session validate function."""

    def test_validate_success(self) -> None:
        """Test validation with valid purpose and background."""
        # Should not raise any exception
        validate(purpose="Test Purpose", background="Test Background")

    @pytest.mark.parametrize(
        "purpose",
        [None, ""],
    )
    def test_validate_missing_purpose(self, purpose: str | None) -> None:
        """Test validation when purpose is missing or empty."""
        with pytest.raises(ValueError, match="Purpose is required for a new session."):
            validate(purpose=purpose, background="Test Background")

    @pytest.mark.parametrize(
        "background",
        [None, ""],
    )
    def test_validate_missing_background(self, background: str | None) -> None:
        """Test validation when background is missing or empty."""
        with pytest.raises(
            ValueError, match="Background is required for a new session."
        ):
            validate(purpose="Test Purpose", background=background)
