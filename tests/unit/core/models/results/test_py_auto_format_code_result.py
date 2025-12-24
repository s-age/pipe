import json

import pytest
from pipe.core.models.results.py_auto_format_code_result import (
    FormatterToolResult,
    PyAutoFormatCodeResult,
)
from pydantic import ValidationError

from tests.factories.models.results.results_factory import ResultFactory


class TestPyAutoFormatCodeResult:
    """Tests for PyAutoFormatCodeResult model."""

    def test_valid_py_auto_format_code_result_creation(self):
        """Test creating a valid PyAutoFormatCodeResult with all fields."""
        formatter_result = ResultFactory.create_formatter_tool_result(
            tool="black",
            stdout="reformatted",
            stderr="",
            exit_code=0,
            message="Success",
        )
        result = PyAutoFormatCodeResult(
            formatting_results=[formatter_result], message="All tools finished"
        )
        assert len(result.formatting_results) == 1
        assert result.formatting_results[0].tool == "black"
        assert result.message == "All tools finished"

    def test_formatter_tool_result_defaults(self):
        """Test default values for FormatterToolResult."""
        result = FormatterToolResult(tool="ruff")
        assert result.tool == "ruff"
        assert result.stdout is None
        assert result.stderr is None
        assert result.exit_code is None
        assert result.error is None
        assert result.message is None

    def test_py_auto_format_code_result_serialization_by_alias(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        formatter_result = ResultFactory.create_formatter_tool_result(
            tool="black", exit_code=0
        )
        result = PyAutoFormatCodeResult(
            formatting_results=[formatter_result], message="Success"
        )

        dumped = result.model_dump(by_alias=True)

        # Check camelCase fields
        assert "formattingResults" in dumped
        assert dumped["formattingResults"][0]["tool"] == "black"
        assert dumped["formattingResults"][0]["exitCode"] == 0
        assert dumped["message"] == "Success"

    def test_py_auto_format_code_result_deserialization(self):
        """Test deserialization from camelCase dictionary."""
        data = {
            "formattingResults": [
                {"tool": "isort", "stdout": "Sorted imports", "exitCode": 0}
            ],
            "message": "Done",
        }

        result = PyAutoFormatCodeResult.model_validate(data)

        assert len(result.formatting_results) == 1
        assert result.formatting_results[0].tool == "isort"
        assert result.formatting_results[0].stdout == "Sorted imports"
        assert result.formatting_results[0].exit_code == 0
        assert result.message == "Done"

    def test_py_auto_format_code_result_roundtrip(self):
        """Test serialization and deserialization roundtrip."""
        original = ResultFactory.create_py_auto_format_code_result(
            formatting_results=[
                ResultFactory.create_formatter_tool_result(tool="black", exit_code=0),
                ResultFactory.create_formatter_tool_result(
                    tool="ruff", exit_code=1, error="Failed"
                ),
            ],
            message="Finished with errors",
        )

        # Serialize to JSON
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = PyAutoFormatCodeResult.model_validate(data)

        assert restored == original
        assert len(restored.formatting_results) == 2
        assert restored.formatting_results[1].tool == "ruff"
        assert restored.formatting_results[1].exit_code == 1
        assert restored.formatting_results[1].error == "Failed"

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        # formatting_results is required
        with pytest.raises(ValidationError) as exc_info:
            PyAutoFormatCodeResult(message="No results")
        assert "formattingResults" in str(exc_info.value)

        # tool is required in FormatterToolResult
        with pytest.raises(ValidationError) as exc_info:
            FormatterToolResult(stdout="some output")
        assert "tool" in str(exc_info.value)
