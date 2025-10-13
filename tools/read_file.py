from typing import Optional, Dict, Any
import os

# session_manager and session_id are dynamically passed by the tool executor
def read_file(absolute_path: str, limit: Optional[float] = None, offset: Optional[float] = None, session_manager=None, session_id=None) -> Dict[str, Any]:
    """
    Adds a file to the session's reference list for inclusion in the prompt. It does not read the file content directly.
    """
    if not session_manager or not session_id:
        return {"error": "This tool requires an active session."}

    abs_path = os.path.abspath(absolute_path)
    
    if not os.path.exists(abs_path):
        return {"error": f"File not found: {abs_path}"}
    if not os.path.isfile(abs_path):
        return {"error": f"Path is not a file: {abs_path}"}

    try:
        session_manager.add_references(session_id, [abs_path])
        
        # Check if the file is empty and tailor the message
        if os.path.getsize(abs_path) == 0:
            message = f"File '{abs_path}' has been added to the session references, but it is empty."
        else:
            message = f"File '{abs_path}' has been added to the session references."
            
        return {"message": message}
    except Exception as e:
        return {"error": f"Failed to add reference to session: {e}"}