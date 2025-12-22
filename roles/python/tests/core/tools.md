# Tools Layer Testing Strategy

**Layer:** `src/pipe/core/tools/`

## Responsibilities
- Integration with external tools and APIs
- Command execution, file operations, etc.

## Testing Strategy
- **Mock All External Dependencies**: Subprocesses, file system, API calls.
- **Focus**: Input validation, output formatting, error handling.

## Test Patterns

```python
# tests/unit/tools/test_run_shell_command.py
import pytest
from unittest.mock import Mock, patch
from pipe.core.tools.run_shell_command import run_shell_command


class TestRunShellCommand:
    """Test run_shell_command tool."""

    @patch('subprocess.run')
    def test_successful_command_execution(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="output",
            stderr="",
        )

        result = run_shell_command(command="echo hello", cwd="/tmp")

        assert result.status == "success"
        assert result.output == "output"
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_command_execution_failure(self, mock_run):
        """Test command execution with non-zero exit code."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error message",
        )

        result = run_shell_command(command="invalid-command", cwd="/tmp")

        assert result.status == "error"
        assert "error message" in result.message

    @patch('subprocess.run')
    def test_timeout_handling(self, mock_run):
        """Test that timeout is properly handled."""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired(cmd="sleep 10", timeout=5)

        result = run_shell_command(command="sleep 10", cwd="/tmp", timeout=5)

        assert result.status == "error"
        assert "timeout" in result.message.lower()


class TestRunShellCommandSecurity:
    """Security tests for shell command execution."""

    def test_command_injection_prevention(self):
        """Test that dangerous command injection patterns are rejected."""
        dangerous_commands = [
            "echo hello; rm -rf /",
            "ls && cat /etc/passwd",
            "echo `whoami`",
            "echo $(cat ~/.ssh/id_rsa)",
        ]

        for cmd in dangerous_commands:
            # Depending on implementation, should either:
            # 1. Raise ValueError for dangerous patterns
            # 2. Use shell=False to prevent injection
            # This test documents the security requirement
            with pytest.raises((ValueError, SecurityError)):
                run_shell_command(command=cmd, cwd="/tmp")

    def test_command_whitelist_enforcement(self):
        """Test that only whitelisted commands are allowed (if applicable)."""
        # If the tool uses a whitelist approach
        allowed_commands = ["git", "npm", "python"]
        disallowed_command = "rm"

        # This should be rejected
        with pytest.raises(ValueError, match="Command not allowed"):
            run_shell_command(command=f"{disallowed_command} -rf /tmp/test", cwd="/tmp")

    @patch('subprocess.run')
    def test_path_traversal_prevention(self, mock_run):
        """Test that path traversal in cwd is prevented."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Attempt to use path traversal
        dangerous_paths = [
            "../../../etc",
            "/etc/passwd",
            "~/.ssh",
        ]

        for path in dangerous_paths:
            # Should either normalize path or raise error
            result = run_shell_command(command="ls", cwd=path)
            # Verify that the actual path used was sanitized
            call_args = mock_run.call_args
            actual_cwd = call_args.kwargs.get('cwd')
            assert '..' not in actual_cwd or actual_cwd.startswith('/tmp/')
```

## Mandatory Test Items
- ✅ Verification of successful execution
- ✅ Error cases (timeout, command failure, etc.)
- ✅ Mocking of external dependencies
- ✅ Input validation
- ✅ Consistency of output format
- ✅ **Security Verification**: Command injection, path traversal, whitelist checks
