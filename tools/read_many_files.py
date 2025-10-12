import os
import glob as std_glob
from pathlib import Path
from typing import Optional

def read_many_files(
    paths: list[str],
    exclude: Optional[list[str]] = None,
    include: Optional[list[str]] = None,
    recursive: bool = True,
    useDefaultExcludes: bool = True,
) -> dict:
    try:
        all_files_content = []
        project_root = Path(os.getcwd()) # Assuming current working directory is project root

        # Define default exclusion patterns
        default_excludes = [
            "**/.git/**", "**/.gemini/**", "**/.pytest_cache/**", "**/__pycache__/**",
            "**/venv/**", "**/node_modules/**", "*.log", "*.tmp", "*.bak",
            "*.pyc", "*.class", "*.jar", "*.zip", "*.tar.gz", "*.rar", "*.7z",
            "*.exe", "*.dll", "*.so", "*.dylib", "*.o", "*.a",
            "*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.tiff", "*.webp", "*.ico",
            "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx", "*.ppt", "*.pptx",
            "*.mp3", "*.mp4", "*.avi", "*.mov", "*.flv", "*.wmv", "*.mkv",
        ]

        final_excludes = set(exclude if exclude is not None else [])
        if useDefaultExcludes:
            final_excludes.update(default_excludes)
        
        final_includes = set(include if include is not None else [])

        # Process paths and glob patterns
        for pattern_or_path in paths:
            # If it's a directory, glob all files within it
            if (project_root / pattern_or_path).is_dir():
                pattern_or_path = str(project_root / pattern_or_path / "**/*")
            
            # Use std_glob for pattern matching
            for filepath_str in std_glob.glob(str(project_root / pattern_or_path), recursive=recursive):
                filepath = Path(filepath_str)
                
                # Check against final_excludes
                is_excluded = False
                for excl_pattern in final_excludes:
                    if filepath.match(excl_pattern):
                        is_excluded = True
                        break
                if is_excluded:
                    continue

                # Check against final_includes (if any are specified)
                if final_includes:
                    is_included = False
                    for incl_pattern in final_includes:
                        if filepath.match(incl_pattern):
                            is_included = True
                            break
                    if not is_included:
                        continue

                if filepath.is_file():
                    try:
                        content = filepath.read_text(encoding="utf-8")
                        all_files_content.append(f"--- {filepath.relative_to(project_root)} ---{content}")
                    except UnicodeDecodeError:
                        # Handle non-text files by skipping or indicating
                        all_files_content.append(f"--- {filepath.relative_to(project_root)} ---[Binary file or cannot decode]")
                    except Exception as file_e:
                        all_files_content.append(f"--- {filepath.relative_to(project_root)} ---[Error reading file: {file_e}]")

        if not all_files_content:
            return {"content": "No files found matching the criteria."}

        separator = "\n--- End of content ---\n"
        return {"content": separator.join(all_files_content)}
    except Exception as e:
        return {"content": f"Error inside read_many_files tool: {str(e)}"}
