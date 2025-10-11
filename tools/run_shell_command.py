import subprocess

from typing import Union

def run_shell_command(
    command: str,
    description: Union[str, None] = None,
    directory: Union[str, None] = None,
) -> dict:
  """This tool executes a given shell command as `bash -c <command>`. Command can start background processes using `&`. Command is executed as a subprocess that leads its own process group. Command process group can be terminated as `kill -- -PGID` or signaled as `kill -s SIGNAL -- -PGID`.

      The following information is returned:

      Command: Executed command.
      Directory: Directory where command was executed, or `(root)`.
      Stdout: Output on stdout stream. Can be `(empty)` or partial on error and for any unwaited background processes.
      Stderr: Output on stderr stream. Can be `(empty)` or partial on error and for any unwaited background processes.
      Error: Error or `(none)` if no error was reported for the subprocess.
      Exit Code: Exit code or `(none)` if terminated by signal.
      Signal: Signal number or `(none)` if no signal was received.
      Background PIDs: List of background processes started or `(none)`.
      Process Group PGID: Process group started or `(none)`

  Args:
    command: Exact bash command to execute as `bash -c <command>`
      *** WARNING: Command substitution using $(), `` ` ``, <(), or >() is not allowed for security reasons.
    description: Brief description of the command for the user. Be specific and concise. Ideally a single sentence. Can be up to 3 sentences for clarity. No line breaks.
    directory: (OPTIONAL) The absolute path of the directory to run the command in. If not provided, the project root directory is used. Must be a directory within the workspace and must already exist.
  """
  # This function is a stub for actual shell command execution.
  # Actual shell command execution must be implemented in the environment that calls this function.
  try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=directory)
    return {
        "run_shell_command_response": {
            "output": result.stdout,
            "error": result.stderr,
            "exit_code": result.returncode
        }
    }
  except Exception as e:
    return {"run_shell_command_response": {"output": f"Error executing command: {e}"}}
