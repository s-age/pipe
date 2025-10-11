from typing import Optional, Dict, Any

def run_shell_command(command: str, description: Optional[str] = None, directory: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes a specified shell command.
    """
    # Stub implementation
    print(f"Stub: run_shell_command called with command={command}, description={description}, directory={directory}")
    return {"stdout": "Stub stdout", "stderr": "", "exit_code": 0}
