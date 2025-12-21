# Tools Layer

## Purpose

Tools provide **AI agent capabilities** - functions that AI models can call to interact with the system. Each tool is a discrete operation (read file, search web, execute command).

## Responsibilities

1. **Operation Execution** - Perform specific operations
2. **Parameter Validation** - Validate tool parameters
3. **Error Handling** - Return errors as tool results
4. **Result Formatting** - Format results for AI consumption
5. **Safety** - Enforce sandboxing and constraints

## Rules

### ✅ DO

- Single-purpose operations
- Validate parameters
- Return structured ToolResult
- Handle errors gracefully
- Document parameters clearly (for AI)
- Keep stateless

### ❌ DON'T

- **NO orchestration** - One tool, one operation
- **NO calling other tools** - Let agent orchestrate
- **NO persistence** - Use services for that
- **NO side effects outside operation scope**

## File Structure

```
tools/
├── base_tool.py          # Abstract base
├── file_tools.py         # File operations
├── search_tools.py       # Search operations
└── ...
```

## Dependencies

**Allowed:**
- ✅ Services (for business operations)
- ✅ Utils (for helpers)
- ✅ Standard library

**Forbidden:**
- ❌ Other tools
- ❌ Direct repository access
- ❌ Direct domain access

## Example

```python
"""File reading tool."""

from pipe.core.tools.base_tool import BaseTool, ToolResult

class ReadFileTool(BaseTool):
    """
    Read file contents.
    
    Parameters:
        file_path (str): Path to file to read
        start_line (int): Starting line (optional)
        end_line (int): Ending line (optional)
    
    Returns:
        File contents as string
    """
    
    name = "read_file"
    description = "Read contents of a file"
    
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to file"
            },
            "start_line": {
                "type": "integer",
                "description": "Starting line number (1-indexed)"
            },
            "end_line": {
                "type": "integer",
                "description": "Ending line number (1-indexed)"
            }
        },
        "required": ["file_path"]
    }
    
    def execute(self, file_path: str, start_line: int = None, end_line: int = None) -> ToolResult:
        """
        Execute file read.
        
        Args:
            file_path: Path to file
            start_line: Optional start line
            end_line: Optional end line
            
        Returns:
            ToolResult with file contents or error
        """
        try:
            # Validate path is within workspace
            if not self._is_safe_path(file_path):
                return ToolResult(
                    success=False,
                    error="Path outside workspace"
                )
            
            # Read file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Apply line range if specified
            if start_line or end_line:
                start = (start_line or 1) - 1
                end = end_line
                lines = lines[start:end]
            
            content = ''.join(lines)
            
            return ToolResult(
                success=True,
                result=content,
                metadata={
                    "file_path": file_path,
                    "lines_read": len(lines)
                }
            )
            
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error=f"File not found: {file_path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error reading file: {str(e)}"
            )
    
    def _is_safe_path(self, path: str) -> bool:
        """Validate path is within workspace."""
        abs_path = os.path.abspath(path)
        workspace = os.path.abspath(self.workspace_root)
        return abs_path.startswith(workspace)
```

## Common Patterns

### Pattern 1: Parameter Validation

```python
def execute(self, param: str) -> ToolResult:
    """Execute with validation."""
    if not param:
        return ToolResult(
            success=False,
            error="Parameter required"
        )
    # Execute operation
```

### Pattern 2: Service Delegation

```python
def execute(self, entity_id: str) -> ToolResult:
    """Execute via service."""
    try:
        result = self.service.operation(entity_id)
        return ToolResult(success=True, result=result)
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

## Testing

```python
# tests/core/tools/test_file_tools.py

def test_read_file_returns_contents(tmp_path):
    """Test read_file returns file contents."""
    file = tmp_path / "test.txt"
    file.write_text("Hello World")
    
    tool = ReadFileTool(workspace_root=str(tmp_path))
    result = tool.execute(str(file))
    
    assert result.success
    assert result.result == "Hello World"

def test_read_file_rejects_outside_workspace(tmp_path):
    """Test read_file rejects paths outside workspace."""
    tool = ReadFileTool(workspace_root=str(tmp_path))
    
    result = tool.execute("/etc/passwd")
    
    assert not result.success
    assert "outside workspace" in result.error
```

## Summary

**Tools:**
- ✅ Single-purpose AI operations
- ✅ Validate parameters
- ✅ Return ToolResult
- ✅ Handle errors gracefully
- ❌ No orchestration or side effects

**Tools are discrete operations AI can invoke**
