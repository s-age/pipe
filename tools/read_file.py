from typing import Union

def read_file(
    absolute_path: str,
    limit: Union[float, None] = None,
    offset: Union[float, None] = None,
) -> dict:
  """Reads and returns the content of a specified file. If the file is large, the content will be truncated. The tool's response will clearly indicate if truncation has occurred and will provide details on how to read more of the file using the 'offset' and 'limit' parameters. Handles text, images (PNG, JPG, GIF, WEBP, SVG, BMP), and PDF files. For text files, it can read specific line ranges.

  Args:
    absolute_path: The absolute path to the file to read (e.g., '/home/user/project/file.txt'). Relative paths are not supported. You must provide an absolute path.
    limit: Optional: For text files, maximum number of lines to read. Use with 'offset' to paginate through large files. If omitted, reads the entire file (if feasible, up to a default limit).
    offset: Optional: For text files, the 0-based line number to start reading from. Requires 'limit' to be set. Use for paginating through large files.
  """
  # This function is a stub for actual file system operations.
  # Actual file system operations must be implemented in the environment that calls this function.

  try:
    with open(absolute_path, 'r', encoding='utf-8') as f:
      content = f.read()
    return {"read_file_response": {"output": content}}
  except FileNotFoundError:
    return {"read_file_response": {"output": f"Error: File not found at {absolute_path}"}}
  except Exception as e:
    return {"read_file_response": {"output": f"Error reading file: {e}"}}
