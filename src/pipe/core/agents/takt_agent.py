"""
Agent for running takt CLI commands.

This module handles subprocess execution of the takt CLI,
which is used by optimization workflows (compressor, therapist, doctor).
"""

import os
import re
import subprocess
import sys

from pipe.core.models.settings import Settings


class TaktAgent:
    """Agent for executing takt CLI commands."""

    def __init__(self, project_root: str, settings: Settings):
        """Initialize the agent.

        Args:
            project_root: Path to the project root directory
            settings: Settings object for timezone configuration
        """
        self.project_root = project_root
        self.settings = settings

    def run_new_session(
        self,
        purpose: str,
        background: str,
        roles: str,
        instruction: str,
        multi_step_reasoning: bool = False,
    ) -> tuple[str, str, str]:
        """Run takt to create a new session.

        Args:
            purpose: Session purpose
            background: Session background
            roles: Roles file path
            instruction: Initial instruction
            multi_step_reasoning: Enable multi-step reasoning

        Returns:
            Tuple of (session_id, stdout, stderr)

        Raises:
            RuntimeError: If takt command fails or session ID cannot be extracted

        Note:
            This method uses subprocess.run (blocking, non-streaming) for session
            creation. Process management is less critical here since execution is
            short-lived, but we still check for session ID extraction.
        """
        command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--purpose",
            purpose,
            "--background",
            background,
            "--roles",
            roles,
            "--instruction",
            instruction,
            "--output-format",
            "json",
        ]

        if multi_step_reasoning:
            command.append("--multi-step-reasoning")

        env = self._get_env()

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            env=env,
        )

        # Debug output to file
        debug_file = os.path.join(self.project_root, "takt_debug.log")
        with open(debug_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Timestamp: {__import__('datetime').datetime.now()}\n")
            f.write(f"Command: {' '.join(command)}\n")
            f.write(f"Return code: {result.returncode}\n")
            f.write(f"STDOUT:\n{result.stdout}\n")
            f.write(f"STDERR:\n{result.stderr}\n")
            f.write(f"{'='*80}\n")

        if result.returncode != 0:
            raise RuntimeError(
                f"takt command failed with return code {result.returncode}. "
                f"stderr: {result.stderr}"
            )

        # Extract session ID from output
        session_id = self._extract_session_id(result.stdout, result.stderr)

        return session_id, result.stdout, result.stderr

    def run_existing_session(
        self,
        session_id: str,
        instruction: str,
        output_format: str = "json",
        multi_step_reasoning: bool = False,
        references: list[str] | None = None,
        artifacts: list[str] | None = None,
        procedure: str | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> tuple[str, str]:
        """Run takt on an existing session.

        Args:
            session_id: Existing session ID
            instruction: Instruction to execute
            output_format: Output format (json, text, stream-json)
            multi_step_reasoning: Enable multi-step reasoning
            references: List of reference file paths
            artifacts: List of artifact file paths
            procedure: Path to procedure file
            extra_env: Additional environment variables

        Returns:
            Tuple of (stdout, stderr)

        Raises:
            RuntimeError: If takt command fails or session is already running

        Note:
            This method uses subprocess.run (blocking, non-streaming).
            Still checks for concurrent execution to prevent conflicts.
        """
        from pipe.core.services.process_manager_service import ProcessManagerService

        process_manager = ProcessManagerService(self.project_root, self.settings)

        # Check for concurrent execution
        if process_manager.is_running(session_id):
            raise RuntimeError(
                f"Session {session_id} is already running. "
                "Stop the existing process before starting a new one."
            )

        command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--session",
            session_id,
            "--instruction",
            instruction,
            "--output-format",
            output_format,
        ]

        if multi_step_reasoning:
            command.append("--multi-step-reasoning")

        if references:
            command.extend(["--references", ",".join(references)])

        if artifacts:
            command.extend(["--artifacts", ",".join(artifacts)])

        if procedure:
            command.extend(["--procedure", procedure])

        env = self._get_env()
        if extra_env:
            env.update(extra_env)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                env=env,
            )
        except subprocess.CalledProcessError as e:
            # Include stderr in error message for debugging
            error_msg = f"takt command failed with exit code {e.returncode}"
            if e.stderr:
                error_msg += f"\nStderr: {e.stderr}"
            raise RuntimeError(error_msg) from e

        return result.stdout, result.stderr

    def run_existing_session_stream(
        self,
        session_id: str,
        instruction: str,
        multi_step_reasoning: bool = False,
        extra_env: dict[str, str] | None = None,
    ):
        """Run takt on an existing session with streaming output.

        Args:
            session_id: Existing session ID
            instruction: Instruction to execute
            multi_step_reasoning: Enable multi-step reasoning
            extra_env: Additional environment variables

        Yields:
            Output lines from the takt process

        Raises:
            RuntimeError: If takt command fails or session is already running

        Note:
            Integrates with ProcessManagerService for:
            - Concurrent execution prevention
            - Process registration and tracking
            - Cleanup on completion or error
        """
        from pipe.core.services.process_manager_service import ProcessManagerService

        process_manager = ProcessManagerService(self.project_root, self.settings)

        # Check for concurrent execution
        if process_manager.is_running(session_id):
            raise RuntimeError(
                f"Session {session_id} is already running. "
                "Stop the existing process before starting a new one."
            )

        command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--session",
            session_id,
            "--instruction",
            instruction,
            "--output-format",
            "stream-json",
        ]

        if multi_step_reasoning:
            command.append("--multi-step-reasoning")

        env = self._get_env()
        if extra_env:
            env.update(extra_env)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=env,
        )

        # Register process immediately after starting
        try:
            process_manager.register_process(session_id, process.pid, instruction)
        except Exception as e:
            # If registration fails, kill the process
            process.terminate()
            raise RuntimeError(f"Failed to register process: {e}") from e

        try:
            # Stream output
            if process.stdout:
                yield from iter(process.stdout.readline, "")
                process.stdout.close()

            stderr_output = ""
            if process.stderr:
                stderr_output = process.stderr.read()
                process.stderr.close()

            return_code = process.wait()

            if return_code != 0:
                raise RuntimeError(
                    f"takt command failed with return code {return_code}. "
                    f"stderr: {stderr_output}"
                )
        finally:
            # Always cleanup process registration
            process_manager.cleanup_process(session_id)

    def _get_env(self) -> dict[str, str]:
        """Get environment variables for subprocess."""
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.join(self.project_root, "src")
        return env

    def _extract_session_id(self, stdout: str, stderr: str) -> str:
        """Extract session ID from takt output.

        Args:
            stdout: Standard output from takt
            stderr: Standard error from takt

        Returns:
            Extracted session ID

        Raises:
            RuntimeError: If session ID cannot be extracted
        """
        import json

        # Try to parse stdout as JSON, searching line by line for JSON
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if line.startswith("{"):
                try:
                    output = json.loads(line)
                    session_id = output.get("session_id")
                    if session_id:
                        return session_id
                except json.JSONDecodeError:
                    continue

        # Fallback to stderr extraction
        match = re.search(r"New session created: (.+)", stderr)
        if match:
            return match.group(1)

        raise RuntimeError("Failed to extract session ID from takt output")

    def run_instruction_stream_unified(
        self,
        session_id: str,
        instruction: str,
        multi_step_reasoning: bool = False,
    ):
        """Run instruction with streaming output via CLI subprocess.

        This method provides a unified interface for streaming execution,
        delegating all logic to the CLI which handles agent selection,
        Turn saving, and token counting internally.

        Args:
            session_id: Existing session ID
            instruction: Instruction to execute
            multi_step_reasoning: Enable multi-step reasoning

        Yields:
            str: Streaming output lines

        Raises:
            RuntimeError: If execution fails
        """
        # Always use subprocess - let CLI handle agent selection
        yield from self.run_existing_session_stream(
            session_id=session_id,
            instruction=instruction,
            multi_step_reasoning=multi_step_reasoning,
        )


def create_takt_agent(project_root: str, settings: Settings) -> TaktAgent:
    """Factory function to create TaktAgent.

    Args:
        project_root: Path to the project root directory
        settings: Settings object for timezone configuration

    Returns:
        Configured TaktAgent instance
    """
    return TaktAgent(project_root, settings)
