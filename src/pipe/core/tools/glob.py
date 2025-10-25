import glob as std_glob
import os
import subprocess
from typing import Optional, Dict

def glob(pattern: str, path: Optional[str] = None, recursive: Optional[bool] = True) -> Dict[str, str]:
    """
    Efficiently finds files matching specific glob patterns, respecting .gitignore.
    """
    try:
        search_path = path if path else '.'
        
        # Get all files matching the pattern
        glob_pattern = os.path.join(search_path, pattern)
        all_files = set(std_glob.glob(glob_pattern, recursive=recursive))

        # Get all ignored files from git
        try:
            git_process = subprocess.run(
                ['git', 'ls-files', '--ignored', '--exclude-standard', '--others'],
                capture_output=True,
                text=True,
                cwd=search_path, # Run git command in the target directory
                check=True
            )
            ignored_files = set(git_process.stdout.strip().split('\n'))
            # Make ignored paths relative to the search_path if needed
            ignored_files_abs = {os.path.join(search_path, f) for f in ignored_files}
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git command might fail or git might not be installed.
            # In this case, we proceed without filtering.
            ignored_files_abs = set()

        # Filter out the ignored files
        matched_files = [f for f in all_files if f not in ignored_files_abs]
        matched_files.sort(reverse=True) # Sort by name descending as a default

        content_string = "\n".join(matched_files)
        return {"content": content_string}
    except Exception as e:
        return {"content": f"Error inside glob tool: {str(e)}"}

