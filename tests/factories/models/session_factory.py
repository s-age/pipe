"""Factory for creating Session test fixtures."""

from typing import Any

from pipe.core.collections.turns import TurnCollection
from pipe.core.models.session import Session


class SessionFactory:
    """Helper class for creating Session objects in tests."""

    @staticmethod
    def create(
        session_id: str = "test-session-123",
        created_at: str = "2025-01-01T00:00:00+09:00",
        purpose: str | None = "Test session purpose",
        background: str | None = "Test background",
        roles: list[str] | None = None,
        multi_step_reasoning_enabled: bool = False,
        **kwargs: Any,
    ) -> Session:
        """Create a Session object with default test values.

        Args:
            session_id: Session ID (default: "test-session-123")
            created_at: Creation timestamp (default: "2025-01-01T00:00:00+09:00")
            purpose: Session purpose
            background: Session background
            roles: List of roles
            multi_step_reasoning_enabled: Enable multi-step reasoning
            **kwargs: Additional fields to override

        Returns:
            Session object
        """
        data = {
            "session_id": session_id,
            "created_at": created_at,
            "purpose": purpose,
            "background": background,
            "roles": roles or [],
            "multi_step_reasoning_enabled": multi_step_reasoning_enabled,
        }
        data.update(kwargs)
        return Session(**data)

    @staticmethod
    def create_batch(count: int, **kwargs: Any) -> list[Session]:
        """Create multiple Session objects.

        Args:
            count: Number of sessions to create
            **kwargs: Arguments passed to create()

        Returns:
            List of Session objects
        """
        return [
            SessionFactory.create(session_id=f"test-session-{i}", **kwargs)
            for i in range(count)
        ]

    @staticmethod
    def create_with_turns(turn_count: int = 3, **kwargs: Any) -> Session:
        """Create a Session with predefined turns.

        Args:
            turn_count: Number of turns to create
            **kwargs: Arguments passed to create()

        Returns:
            Session object with turns
        """
        from tests.factories.models.turn_factory import TurnFactory

        turns = TurnFactory.create_batch(turn_count)
        return SessionFactory.create(turns=TurnCollection(turns), **kwargs)
