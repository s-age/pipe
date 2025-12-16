from pipe.core.models.results.save_memory_result import SaveMemoryResult
from pipe.core.models.tool_result import ToolResult


def save_memory(fact: str) -> ToolResult[SaveMemoryResult]:
    """
    Saves specific information to long-term memory.
    """
    # Stub implementation

    result = SaveMemoryResult(status="success", message="Fact saved (stub).")
    return ToolResult(data=result)
