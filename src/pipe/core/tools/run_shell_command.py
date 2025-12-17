import subprocess

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.results.run_shell_command_result import RunShellCommandResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root


def run_shell_command(
    command: str,
    description: str | None = None,
    directory: str | None = None,
) -> ToolResult[RunShellCommandResult]:
    try:
        # Get project root and create repository
        project_root = get_project_root()
        repo = FileRepositoryFactory.create()

        # Determine the directory to run the command in
        if directory:
            # Validate directory using repository
            if not repo.exists(directory):
                return ToolResult(error=f"Directory does not exist: {directory}")
            if not repo.is_dir(directory):
                return ToolResult(error=f"Path is not a directory: {directory}")

            # Get validated absolute path
            cwd = repo.get_absolute_path(directory)
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

    except ValueError as e:
        # FileSystemRepository validation errors
        return ToolResult(error=f"Invalid directory: {e}")
    except FileNotFoundError:
        return ToolResult(error=f"Command not found: {command.split()[0]}")
    except Exception as e:
        return ToolResult(error=f"Error inside run_shell_command tool: {str(e)}")
