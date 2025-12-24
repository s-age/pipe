"""Unit tests for TsAutoFormatCodeResult models."""

import json

import pytest
from pipe.core.models.results.ts_auto_format_code_result import (
    FormatterToolResult,
    TsAutoFormatCodeResult,
)
from pydantic import ValidationError

from tests.factories.models.results.results_factory import ResultFactory


class TestTsAutoFormatCodeResult:
    """Tests for TsAutoFormatCodeResult and FormatterToolResult models."""

    def test_formatter_tool_result_creation(self):
        """Test creating a valid FormatterToolResult."""
        result = ResultFactory.create_ts_formatter_tool_result(
            tool="prettier", stdout="success", exit_code=0, message="Formatted"
        )
        assert result.tool == "prettier"
        assert result.stdout == "success"
        assert result.exit_code == 0
        assert result.message == "Formatted"

    def test_ts_auto_format_code_result_creation(self):
        """Test creating a valid TsAutoFormatCodeResult."""
        tool_result = ResultFactory.create_ts_formatter_tool_result(tool="eslint")
        result = ResultFactory.create_ts_auto_format_code_result(
            formatting_results=[tool_result], message="All tools finished"
        )
        assert len(result.formatting_results) == 1
        assert result.formatting_results[0].tool == "eslint"
        assert result.message == "All tools finished"

    def test_validation_error_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        # 'tool' is required in FormatterToolResult
        with pytest.raises(ValidationError):
            FormatterToolResult(stdout="some output")

        # 'formatting_results' is required in TsAutoFormatCodeResult
        with pytest.raises(ValidationError):
            TsAutoFormatCodeResult(message="missing results")

    def test_serialization_with_aliases(self):
        """Test serialization to camelCase using by_alias=True."""
        tool_result = ResultFactory.create_ts_formatter_tool_result(
            tool="prettier", exit_code=0
        )
        result = ResultFactory.create_ts_auto_format_code_result(
            formatting_results=[tool_result]
        )

        dumped = result.model_dump(by_alias=True)
        # Check camelCase conversion
        assert "formattingResults" in dumped
        assert dumped["formattingResults"][0]["exitCode"] == 0

        # Check snake_case without alias
        dumped_no_alias = result.model_dump()
        assert "formatting_results" in dumped_no_alias
        assert dumped_no_alias["formatting_results"][0]["exit_code"] == 0

    def test_deserialization_from_camel_case(self):
        """Test deserialization from a dictionary with camelCase keys."""
        data = {
            "formattingResults": [
                {"tool": "prettier", "exitCode": 0, "stdout": "done"}
            ],
            "message": "success",
        }
        result = TsAutoFormatCodeResult.model_validate(data)
        assert len(result.formatting_results) == 1
        assert result.formatting_results[0].tool == "prettier"
        assert result.formatting_results[0].exit_code == 0
        assert result.message == "success"

    def test_roundtrip_serialization(self):
        """Test that data is preserved through a serialization roundtrip."""
        original = ResultFactory.create_ts_auto_format_code_result(
            formatting_results=[
                ResultFactory.create_ts_formatter_tool_result(tool="prettier"),
                ResultFactory.create_ts_formatter_tool_result(
                    tool="eslint", exit_code=1
                ),
            ],
            message="Partially failed",
        )

        # Serialize to JSON string with camelCase
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = TsAutoFormatCodeResult.model_validate(data)

        # Verify preservation
        assert restored.message == original.message
        assert len(restored.formatting_results) == 2
        assert restored.formatting_results[0].tool == "prettier"
        assert restored.formatting_results[1].tool == "eslint"
        assert restored.formatting_results[1].exit_code == 1
