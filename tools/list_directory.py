from typing import List, Optional, Dict, Any

def list_directory(path: str, file_filtering_options: Optional[Dict[str, Any]] = None, ignore: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Lists the names of files and subdirectories directly within a specified directory.
    """
    # Stub implementation
    print(f"Stub: list_directory called with path={path}, file_filtering_options={file_filtering_options}, ignore={ignore}")
    return {"files": [], "directories": []}
