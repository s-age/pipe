import subprocess
import os

from typing import Optional

def run_shell_command(
    command: str,
    description: Optional[str] = None,
    directory: Optional[str] = None,
) -> dict:
    try:
        # Determine the directory to run the command in
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if directory:
            target_directory = os.path.abspath(directory)
            if not os.path.isdir(target_directory):
                return {"error": f"Directory does not exist: {directory}"}
            if not target_directory.startswith(project_root):
                return {"error": f"Running commands outside project root is not allowed: {directory}"}
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
            check=False # Do not raise an exception for non-zero exit codes
        )

        # Prepare the result dictionary
        result = {
            "command": command,
            "directory": str(cwd),
            "stdout": process.stdout.strip() if process.stdout else "(empty)",
            "stderr": process.stderr.strip() if process.stderr else "(empty)",
            "exit_code": process.returncode,
            "error": "(none)",
            "signal": "(none)", # subprocess.run doesn't directly expose signal for shell=True
            "background_pids": "(none)", # Not easily captured with shell=True
            "process_group_pgid": "(none)" # Not easily captured with shell=True
        }

        if process.returncode != 0:
            result["error"] = f"Command failed with exit code {process.returncode}"

        return result

    except FileNotFoundError:
        return {"error": f"Command not found: {command.split()[0]}"}
    except Exception as e:
        return {"error": f"Error inside run_shell_command tool: {str(e)}"}
