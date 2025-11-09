import os
import subprocess


def ts_checker(
    project_root: str | None = None,
    lint_command: str = "npm run lint",
    build_command: str = "npm run build"
) -> dict:
    """Runs TypeScript lint and build checks and reports any errors or warnings.

    Args:
        project_root: The absolute path to the project root directory.
            Defaults to the current working directory.
        lint_command: The command to run for linting. Defaults to "npm run lint".
        build_command: The command to run for building. Defaults to "npm run build".
    """
    if project_root is None:
        project_root = os.getcwd()

    results = {}

    def _run_command(command_str, command_name):
        try:
            process = subprocess.run(
                command_str,
                shell=True,
                capture_output=True,
                text=True,
                cwd=project_root
            )
            output = process.stdout + process.stderr
            errors = []
            warnings = []
            for line in output.splitlines():
                if "error" in line.lower():
                    errors.append(line.strip())
                elif "warning" in line.lower():
                    warnings.append(line.strip())
            results[command_name] = {
                "output": output,
                "errors": errors,
                "warnings": warnings,
                "exit_code": process.returncode
            }
        except Exception as e:
            results[command_name] = {
                "output": f"Error running command '{command_str}': {e}",
                "errors": [f"Tool execution error: {e}"],
                "warnings": [],
                "exit_code": 1
            }

    _run_command(lint_command, "Lint")
    _run_command(build_command, "Build")

    return results
