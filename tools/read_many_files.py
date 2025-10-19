import os
import glob as std_glob
import fnmatch

from typing import Optional, List, Dict, Any

# session_manager and session_id are dynamically passed by the tool executor
def read_many_files(
    paths: List[str],
    exclude: Optional[List[str]] = None,
    include: Optional[List[str]] = None,
    recursive: bool = True,
    useDefaultExcludes: bool = True,
    session_manager=None,
    session_id=None
) -> Dict[str, Any]:
    """
    Resolves file paths based on glob patterns and adds them to the session's reference list.
    """
    if not session_manager or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        resolved_files = []
        project_root = os.getcwd()

        default_excludes = [
            "**/.git/**", "**/.gemini/**", "**/.pytest_cache/**", "**/__pycache__/**",
            "**/venv/**", "**/node_modules/**", "*.log", "*.tmp", "*.bak",
        ]

        final_excludes = set(exclude if exclude is not None else [])
        if useDefaultExcludes:
            final_excludes.update(default_excludes)
        
        final_includes = set(include if include is not None else [])

        for pattern_or_path in paths:
            # Handle directory paths
            if os.path.isdir(os.path.join(project_root, pattern_or_path)):
                pattern_to_glob = os.path.join(project_root, pattern_or_path, "**/*")
            else:
                pattern_to_glob = os.path.join(project_root, pattern_or_path)

            for filepath_str in std_glob.glob(pattern_to_glob, recursive=recursive):
                filepath = filepath_str
                
                if not os.path.isfile(filepath):
                    continue

                is_excluded = any(std_glob.fnmatch.fnmatch(filepath, p) for p in final_excludes)
                if is_excluded:
                    continue

                if final_includes:
                    is_included = any(std_glob.fnmatch.fnmatch(filepath, p) for p in final_includes)
                    if not is_included:
                        continue
                
                resolved_files.append(os.path.abspath(filepath))

        if not resolved_files:
            return {"message": "No files found matching the criteria."}

        # Remove duplicates
        unique_files = sorted(list(set(resolved_files)))
        
        session_manager.add_references(session_id, unique_files)
        
        return {"message": f"Added {len(unique_files)} files to the session references."}

    except Exception as e:
        return {"error": f"Error in read_many_files tool: {str(e)}"}