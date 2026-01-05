"""
Unit tests for the instruction validator.
"""

import pytest
from pipe.core.validators.sessions.instruction import validate


class TestInstructionValidator:
    """Tests for the validate function."""

    def test_validate_with_valid_instruction(self):
        """Test validation with a valid instruction string."""
        # Should not raise any exception
        validate("Do something")

    def test_validate_with_none(self):
        """Test validation with None."""
        with pytest.raises(ValueError, match="Instruction is required."):
            validate(None)

    def test_validate_with_empty_string(self):
        """Test validation with an empty string."""
        with pytest.raises(ValueError, match="Instruction is required."):
            validate("")
