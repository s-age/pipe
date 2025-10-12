import subprocess
import os
from pathlib import Path
from typing import Optional

def run_shell_command(
    command: str,
    description: Optional[str] = None,
    directory: Optional[str] = None,
) -> dict:
    try:
        # Determine the directory to run the command in
        if directory:
            # Ensure the provided directory is within the project root for safety
            project_root = Path(os.getcwd())
            abs_directory = project_root / directory
            if not abs_directory.is_dir() or not abs_directory.is_relative_to(project_root):
                return {"error": f"Invalid or unsafe directory: {directory}"}
            cwd = abs_directory
        else:
            cwd = Path(os.getcwd())

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
