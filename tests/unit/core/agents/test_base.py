"""Unit tests for the BaseAgent abstract class."""

from typing import TYPE_CHECKING

import pytest
from pipe.core.agents.base import BaseAgent
from pipe.core.models.args import TaktArgs

if TYPE_CHECKING:
    from pipe.core.services.session_service import SessionService


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""

    def test_base_agent_cannot_be_instantiated(self):
        """Verify that BaseAgent cannot be instantiated directly due to abstract methods."""
        with pytest.raises(TypeError) as excinfo:
            BaseAgent()  # type: ignore[abstract]
        assert "Can't instantiate abstract class BaseAgent" in str(excinfo.value)

    def test_concrete_agent_implementation(self):
        """Verify that a concrete implementation of BaseAgent works as expected."""

        class ConcreteAgent(BaseAgent):
            def run(
                self,
                args: TaktArgs,
                session_service: "SessionService",
            ) -> tuple[str, int | None, list, str | None]:
                super().run(args, session_service)
                return ("response", 100, [], "thought")

        # Mock session_service
        from unittest.mock import MagicMock

        mock_session_service = MagicMock()
        args = TaktArgs(instruction="test")

        agent = ConcreteAgent()
        response, token_count, turns, thought = agent.run(args, mock_session_service)

        assert response == "response"
        assert token_count == 100
        assert turns == []
        assert thought == "thought"
