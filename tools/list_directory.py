import dataclasses
import os
import fnmatch
from typing import Union, List

@dataclasses.dataclass()
class ListDirectoryFileFilteringOptions:
  """Optional: Whether to respect ignore patterns from .gitignore or .geminiignore

  Attributes:
    respect_gemini_ignore: Optional: Whether to respect .geminiignore patterns when listing files. Defaults to true.
    respect_git_ignore: Optional: Whether to respect .gitignore patterns when listing files. Only available in git repositories. Defaults to true.
  """
  respect_gemini_ignore: Union[bool, None] = None
  respect_git_ignore: Union[bool, None] = None


def list_directory(
    path: str,
    file_filtering_options: Union[ListDirectoryFileFilteringOptions, None] = None,
    ignore: Union[List[str], None] = None,
) -> dict:
  """Lists the names of files and subdirectories directly within a specified directory path. Can optionally ignore entries matching provided glob patterns.

  Args:
    path: The absolute path to the directory to list (must be absolute, not relative)
    file_filtering_options: Optional: Whether to respect ignore patterns from .gitignore or .geminiignore
    ignore: List of glob patterns to ignore
  """
  # Convert MapComposite objects to native Python types if necessary
  if hasattr(file_filtering_options, '_pb') and file_filtering_options._pb is not None:
      file_filtering_options = ListDirectoryFileFilteringOptions(**dict(file_filtering_options._pb))
  
  if hasattr(ignore, '_pb') and ignore._pb is not None:
      ignore = list(ignore._pb)



  try:
    entries = os.listdir(path)
    
    if ignore:
      filtered_entries = []
      for entry in entries:
        # Check if the entry matches any ignore pattern
        is_ignored = False
        for pattern in ignore:
          if fnmatch.fnmatch(entry, pattern):
            is_ignored = True
            break
        if not is_ignored:
          filtered_entries.append(entry)
      entries = filtered_entries

    return {"list_directory_response": {"output": entries}}
  except FileNotFoundError:
    return {"list_directory_response": {"error": f"Directory not found: {path}"}}
  except Exception as e:
    return {"list_directory_response": {"error": f"An error occurred: {str(e)}"}}