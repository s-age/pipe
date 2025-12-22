import json

from pipe.core.models.results.ts_run_and_test_code_result import TsRunAndTestCodeResult

from tests.helpers.results_factory import ResultFactory


class TestTsRunAndTestCodeResult:
    """Tests for TsRunAndTestCodeResult model."""

    def test_default_values(self):
        """Test model creation with default values."""
        result = TsRunAndTestCodeResult()
        assert result.stdout is None
        assert result.stderr is None
        assert result.exit_code is None
        assert result.message is None
        assert result.error is None

    def test_factory_creation(self):
        """Test model creation using factory."""
        result = ResultFactory.create_ts_run_and_test_code_result(
            stdout="ts output",
            stderr="ts error",
            exit_code=1,
            message="ts failed",
            error="TypeError",
        )
        assert result.stdout == "ts output"
        assert result.stderr == "ts error"
        assert result.exit_code == 1
        assert result.message == "ts failed"
        assert result.error == "TypeError"

    def test_serialization_with_aliases(self):
        """Test serialization to camelCase using aliases."""
        result = ResultFactory.create_ts_run_and_test_code_result(exit_code=0)
        dumped = result.model_dump(by_alias=True)
        assert "exitCode" in dumped
        assert dumped["exitCode"] == 0
        assert "stdout" in dumped
        assert "stderr" in dumped
        assert "message" in dumped
        assert "error" in dumped

    def test_deserialization_from_camel_case(self):
        """Test deserialization from a dictionary with camelCase keys."""
        data = {"stdout": "success", "exitCode": 0, "message": "done"}
        result = TsRunAndTestCodeResult.model_validate(data)
        assert result.stdout == "success"
        assert result.exit_code == 0
        assert result.message == "done"

    def test_roundtrip_serialization(self):
        """Test serialization and deserialization preserves data."""
        original = ResultFactory.create_ts_run_and_test_code_result(
            stdout="test ts out",
            stderr="test ts err",
            exit_code=1,
            message="test failed",
            error="Error",
        )

        json_str = original.model_dump_json(by_alias=True)
        data = json.loads(json_str)

        # Verify camelCase in JSON
        assert data["exitCode"] == 1

        restored = TsRunAndTestCodeResult.model_validate(data)
        assert restored == original
