from typing import Optional, Dict, Any
from pathlib import Path

def read_file(absolute_path: str, limit: Optional[float] = None, offset: Optional[float] = None) -> Dict[str, Any]:
    """
    Reads and returns the content of a specified file. If the file is large, the content will be truncated. The tool's response will clearly indicate if truncation has occurred and will provide details on how to read more of the file using the 'offset' and 'limit' parameters. Handles text, images (PNG, JPG, GIF, WEBP, SVG, BMP), and PDF files. For text files, it can read specific line ranges.
    """
    file_path = Path(absolute_path)

    if not file_path.exists():
        return {"error": f"File not found: {absolute_path}"}
    if not file_path.is_file():
        return {"error": f"Path is not a file: {absolute_path}"}

    try:
        # Attempt to read as text file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines = len(lines)

            start_line = int(offset) if offset is not None else 0
            end_line = int(start_line + limit) if limit is not None else total_lines

            truncated = False
            if start_line >= total_lines:
                content = ""
            else:
                content_lines = lines[start_line:end_line]
                content = "".join(content_lines)
                if end_line < total_lines:
                    truncated = True
            
            return {
                "content": content,
                "truncated": truncated,
                "total_lines": total_lines,
                "read_lines_start": start_line,
                "read_lines_end": min(end_line, total_lines)
            }
    except UnicodeDecodeError:
        # If it's not a text file, or not utf-8 decodable, handle as binary
        # For now, we'll just indicate it's a binary file and not read content
        # In a real scenario, you might want to base64 encode or provide metadata
        return {"content": f"Binary file: {file_path.suffix} (content not displayed)", "truncated": False, "is_binary": True}
    except Exception as e:
        return {"error": f"Error reading file {absolute_path}: {str(e)}"}
