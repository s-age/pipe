import dataclasses
from typing import Union

@dataclasses.dataclass()
class ReadManyFilesFileFilteringOptions:
  respect_gemini_ignore: Union[bool, None] = None
  respect_git_ignore: Union[bool, None] = None

def read_many_files(
    paths: list[str],
    exclude: Union[list[str], None] = [],
    file_filtering_options: Union[ReadManyFilesFileFilteringOptions, None] = None,
    include: Union[list[str], None] = [],
    recursive: Union[bool, None] = True,
    useDefaultExcludes: Union[bool, None] = True,
) -> dict:
  """Reads content from multiple files specified by paths or glob patterns within a configured target directory. For text files, it concatenates their content into a single string. It is primarily designed for text-based files. However, it can also process image (e.g., .png, .jpg) and PDF (.pdf) files if their file names or extensions are explicitly included in the 'paths' argument. For these explicitly requested non-text files, their data is read and included in a format suitable for model consumption (e.g., base64 encoded).

  This tool is useful when you need to understand or analyze a collection of files, such as:
  - Getting an overview of a codebase or parts of it (e.g., all TypeScript files in the 'src' directory).
  - Finding where specific functionality is implemented if the user asks broad questions about code.
  - Reviewing documentation files (e.g., all Markdown files in the 'docs' directory).
  - Gathering context from multiple configuration files.
  - When the user asks to "read all files in X directory" or "show me the content of all Y files".

  Use this tool when the user's query implies needing the content of several files simultaneously for context, analysis, or summarization. For text files, it uses default UTF-8 encoding and a '--- {filePath} ---' separator between file contents. The tool inserts a '--- End of content ---' after the last file. Ensure paths are relative to the target directory. Glob patterns like 'src/**/*.js' are supported. Avoid using for single files if a more specific single-file reading tool is available, unless the user specifically requests to process a list containing just one file via this tool. Other binary files (not explicitly requested as image/PDF) are generally skipped. Default excludes apply to common non-text files (except for explicitly requested images/PDFs) and large dependency directories unless 'useDefaultExcludes' is false.

  Args:
    paths: Required. An array of glob patterns or paths relative to the tool's target directory. Examples: ['src/**/*.ts'], ['README.md', 'docs/']
    exclude: Optional. Glob patterns for files/directories to exclude. Added to default excludes if useDefaultExcludes is true. Example: "**/*.log", "temp/"
    file_filtering_options: Whether to respect ignore patterns from .gitignore or .geminiignore
    include: Optional. Additional glob patterns to include. These are merged with `paths`. Example: "*.test.ts" to specifically add test files if they were broadly excluded.
    recursive: Optional. Whether to search recursively (primarily controlled by `**` in glob patterns). Defaults to true.
    useDefaultExcludes: Optional. Whether to apply a list of default exclusion patterns (e.g., node_modules, .git, binary files). Defaults to true.
  """
  # This function is a stub for actual file system operations.
  # Actual file system operations must be implemented in the environment that calls this function.

  return {"read_many_files_response": {"output": f"Reading multiple files (stub)"}}
