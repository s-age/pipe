import os
import subprocess

from pipe.core.models.results.run_shell_command_result import RunShellCommandResult
from pipe.core.models.tool_result import ToolResult


def run_shell_command(
    command: str,
    description: str | None = None,
    directory: str | None = None,
) -> ToolResult[RunShellCommandResult]:
    try:
        # Determine the directory to run the command in
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if directory:
            target_directory = os.path.abspath(directory)
            if not os.path.isdir(target_directory):
                return ToolResult(error=f"Directory does not exist: {directory}")
            if not target_directory.startswith(project_root):
                return ToolResult(
                    error=(
                        "Running commands outside project root is not allowed: "
                        f"{directory}"
                    )
                )
            cwd = target_directory
        else:
            cwd = project_root

        # Execute the command
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=False,  # Do not raise an exception for non-zero exit codes
        )

        error_msg = "(none)"
        if process.returncode != 0:
            error_msg = f"Command failed with exit code {process.returncode}"

        result = RunShellCommandResult(
            command=command,
            directory=str(cwd),
            stdout=process.stdout.strip() if process.stdout else "(empty)",
            stderr=process.stderr.strip() if process.stderr else "(empty)",
            exit_code=process.returncode,
            error=error_msg,
            signal="(none)",
            background_pids="(none)",
            process_group_pgid="(none)",
        )
        return ToolResult(data=result)

    except FileNotFoundError:
        return ToolResult(error=f"Command not found: {command.split()[0]}")
    except Exception as e:
        return ToolResult(error=f"Error inside run_shell_command tool: {str(e)}")
