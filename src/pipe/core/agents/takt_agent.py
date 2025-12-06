"""
Agent for running takt CLI commands.

This module handles subprocess execution of the takt CLI,
which is used by optimization workflows (compressor, therapist, doctor).
"""

import os
import re
import subprocess
import sys
from typing import Any


class TaktAgent:
    """Agent for executing takt CLI commands."""

    def __init__(self, project_root: str):
        """Initialize the agent.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root

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
        extra_env: dict[str, str] | None = None,
    ) -> tuple[str, str]:
        """Run takt on an existing session.

        Args:
            session_id: Existing session ID
            instruction: Instruction to execute
            extra_env: Additional environment variables

        Returns:
            Tuple of (stdout, stderr)

        Raises:
            RuntimeError: If takt command fails
        """
        command = [
            sys.executable,
            "-m",
            "pipe.cli.takt",
            "--session",
            session_id,
            "--instruction",
            instruction,
        ]

        env = self._get_env()
        if extra_env:
            env.update(extra_env)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            env=env,
        )

        return result.stdout, result.stderr

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

        # Try to parse stdout as JSON first
        try:
            output = json.loads(stdout.strip())
            session_id = output.get("session_id")
            if session_id:
                return session_id
        except json.JSONDecodeError:
            pass

        # Fallback to stderr extraction
        match = re.search(r"New session created: (.+)", stderr)
        if match:
            return match.group(1)

        raise RuntimeError("Failed to extract session ID from takt output")


def create_takt_agent(project_root: str) -> TaktAgent:
    """Factory function to create TaktAgent.

    Args:
        project_root: Path to the project root directory

    Returns:
        Configured TaktAgent instance
    """
    return TaktAgent(project_root)
