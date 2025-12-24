import json

from pipe.core.models.results.py_run_and_test_code_result import PyRunAndTestCodeResult

from tests.factories.models.results.results_factory import ResultFactory


class TestPyRunAndTestCodeResult:
    """Tests for PyRunAndTestCodeResult model."""

    def test_default_values(self):
        """Test model creation with default values."""
        result = PyRunAndTestCodeResult()
        assert result.stdout is None
        assert result.stderr is None
        assert result.exit_code is None
        assert result.message is None
        assert result.error is None

    def test_factory_creation(self):
        """Test model creation using factory."""
        result = ResultFactory.create_py_run_and_test_code_result(
            stdout="output",
            stderr="error",
            exit_code=1,
            message="failed",
            error="RuntimeError",
        )
        assert result.stdout == "output"
        assert result.stderr == "error"
        assert result.exit_code == 1
        assert result.message == "failed"
        assert result.error == "RuntimeError"

    def test_serialization_with_aliases(self):
        """Test serialization to camelCase using aliases."""
        result = ResultFactory.create_py_run_and_test_code_result(exit_code=0)
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
        result = PyRunAndTestCodeResult.model_validate(data)
        assert result.stdout == "success"
        assert result.exit_code == 0
        assert result.message == "done"

    def test_roundtrip_serialization(self):
        """Test serialization and deserialization preserves data."""
        original = ResultFactory.create_py_run_and_test_code_result(
            stdout="test out",
            stderr="test err",
            exit_code=127,
            message="command not found",
            error="OSError",
        )

        json_str = original.model_dump_json(by_alias=True)
        data = json.loads(json_str)

        # Verify camelCase in JSON
        assert data["exitCode"] == 127

        restored = PyRunAndTestCodeResult.model_validate(data)
        assert restored == original
