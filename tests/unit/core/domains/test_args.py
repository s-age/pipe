"""Unit tests for args domain logic."""

import pytest
from pipe.core.domains.args import convert_args_to_turn
from pipe.core.models.args import TaktArgs
from pipe.core.models.turn import UserTaskTurn
from pydantic import ValidationError


class TestConvertArgsToTurn:
    """Tests for convert_args_to_turn function."""

    def test_convert_args_to_turn_valid(self):
        """Test converting valid TaktArgs to UserTaskTurn."""
        args = TaktArgs(instruction="Test instruction")
        timestamp = "2026-01-01T00:00:00+09:00"

        turn = convert_args_to_turn(args, timestamp)

        assert isinstance(turn, UserTaskTurn)
        assert turn.type == "user_task"
        assert turn.instruction == "Test instruction"
        assert turn.timestamp == timestamp

    def test_convert_args_to_turn_empty_instruction(self):
        """Test converting TaktArgs with empty instruction."""
        args = TaktArgs(instruction="")
        timestamp = "2026-01-01T00:00:00+09:00"

        turn = convert_args_to_turn(args, timestamp)

        assert turn.instruction == ""
        assert turn.timestamp == timestamp

    def test_convert_args_to_turn_none_instruction(self):
        """Test that None instruction raises ValidationError."""
        args = TaktArgs(instruction=None)  # type: ignore
        timestamp = "2026-01-01T00:00:00+09:00"

        with pytest.raises(ValidationError):
            convert_args_to_turn(args, timestamp)
