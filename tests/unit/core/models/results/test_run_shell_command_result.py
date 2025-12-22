from pipe.core.models.results.run_shell_command_result import RunShellCommandResult

from tests.helpers.results_factory import ResultFactory


class TestRunShellCommandResult:
    """Tests for RunShellCommandResult model."""

    def test_run_shell_command_result_default_values(self):
        """Test creating RunShellCommandResult with default values."""
        result = RunShellCommandResult()
        assert result.command is None
        assert result.directory is None
        assert result.stdout is None
        assert result.stderr is None
        assert result.exit_code is None
        assert result.error is None
        assert result.signal == "(none)"
        assert result.background_pids == "(none)"
        assert result.process_group_pgid == "(none)"

    def test_run_shell_command_result_factory_creation(self):
        """Test creating RunShellCommandResult using factory."""
        result = ResultFactory.create_run_shell_command_result(
            command="echo hello", stdout="hello\n", exit_code=0
        )
        assert result.command == "echo hello"
        assert result.stdout == "hello\n"
        assert result.exit_code == 0
        assert result.signal == "(none)"

    def test_run_shell_command_result_serialization_alias(self):
        """Test serialization with by_alias=True for camelCase output."""
        result = ResultFactory.create_run_shell_command_result(
            exit_code=1, background_pids="12345", process_group_pgid="54321"
        )
        dumped = result.model_dump(by_alias=True)
        assert dumped["exitCode"] == 1
        assert dumped["backgroundPids"] == "12345"
        assert dumped["processGroupPgid"] == "54321"

    def test_run_shell_command_result_deserialization(self):
        """Test deserialization from a dictionary."""
        data = {"command": "ls", "exitCode": 0, "backgroundPids": "(none)"}
        result = RunShellCommandResult.model_validate(data)
        assert result.command == "ls"
        assert result.exit_code == 0
        assert result.background_pids == "(none)"

    def test_run_shell_command_result_roundtrip(self):
        """Test roundtrip serialization and deserialization."""
        original = ResultFactory.create_run_shell_command_result(
            command="git status",
            stdout="On branch main",
            exit_code=0,
            process_group_pgid="1000",
        )

        # Serialize
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize
        restored = RunShellCommandResult.model_validate_json(json_str)

        # Verify
        assert restored == original
        assert restored.command == "git status"
        assert restored.exit_code == 0
        assert restored.process_group_pgid == "1000"
