"""Factory for creating Turn test fixtures."""

from pipe.core.models.turn import (
    CompressedHistoryTurn,
    FunctionCallingTurn,
    ModelResponseTurn,
    ToolResponseTurn,
    TurnResponse,
    UserTaskTurn,
)


class TurnFactory:
    """Helper class for creating Turn objects in tests."""

    @staticmethod
    def create_user_task(
        instruction: str = "Test instruction",
        timestamp: str = "2025-01-01T00:00:00+09:00",
        **kwargs,
    ) -> UserTaskTurn:
        """Create a UserTaskTurn object."""
        return UserTaskTurn(
            type="user_task",
            instruction=instruction,
            timestamp=timestamp,
            **kwargs,
        )

    @staticmethod
    def create_model_response(
        content: str = "Test response",
        timestamp: str = "2025-01-01T00:01:00+09:00",
        thought: str | None = None,
        raw_response: str | None = None,
        **kwargs,
    ) -> ModelResponseTurn:
        """Create a ModelResponseTurn object."""
        return ModelResponseTurn(
            type="model_response",
            content=content,
            thought=thought,
            timestamp=timestamp,
            raw_response=raw_response,
            **kwargs,
        )

    @staticmethod
    def create_function_calling(
        response: str = "call_result",
        timestamp: str = "2025-01-01T00:02:00+09:00",
        raw_response: str | None = None,
        **kwargs,
    ) -> FunctionCallingTurn:
        """Create a FunctionCallingTurn object."""
        return FunctionCallingTurn(
            type="function_calling",
            response=response,
            timestamp=timestamp,
            raw_response=raw_response,
            **kwargs,
        )

    @staticmethod
    def create_tool_response(
        name: str = "test_tool",
        status: str = "success",
        message: str | None = "Tool executed successfully",
        timestamp: str = "2025-01-01T00:03:00+09:00",
        **kwargs,
    ) -> ToolResponseTurn:
        """Create a ToolResponseTurn object."""
        return ToolResponseTurn(
            type="tool_response",
            name=name,
            response=TurnResponse(status=status, message=message),
            timestamp=timestamp,
            **kwargs,
        )

    @staticmethod
    def create_compressed_history(
        content: str = "Summary of turns",
        original_turns_range: list[int] | None = None,
        timestamp: str = "2025-01-01T00:04:00+09:00",
        **kwargs,
    ) -> CompressedHistoryTurn:
        """Create a CompressedHistoryTurn object."""
        return CompressedHistoryTurn(
            type="compressed_history",
            content=content,
            original_turns_range=original_turns_range or [1, 5],
            timestamp=timestamp,
            **kwargs,
        )

    @staticmethod
    def create_batch(count: int, alternate: bool = True) -> list:
        """Create multiple Turn objects.

        Args:
            count: Number of turns to create
            alternate: If True, alternate between user_task and model_response

        Returns:
            List of Turn objects
        """
        turns = []
        for i in range(count):
            if alternate and i % 2 == 0:
                turns.append(
                    TurnFactory.create_user_task(instruction=f"Instruction {i}")
                )
            else:
                turns.append(TurnFactory.create_model_response(content=f"Response {i}"))
        return turns
