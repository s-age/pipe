"""Unit tests for PromptTurnCollection."""

from pipe.core.collections.prompts.turn_collection import PromptTurnCollection

from tests.factories.models import TurnFactory


class TestPromptTurnCollection:
    """Tests for PromptTurnCollection class."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        turns = TurnFactory.create_batch(3)
        collection = PromptTurnCollection(turns=turns)

        assert collection._turns == turns
        assert collection.token_limit == 120000

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        turns = TurnFactory.create_batch(2)
        token_limit = 50000
        collection = PromptTurnCollection(turns=turns, token_limit=token_limit)

        assert collection._turns == turns
        assert collection.token_limit == token_limit

    def test_get_turns_returns_all_turns(self):
        """Test that get_turns currently returns all turns (placeholder behavior)."""
        turns = TurnFactory.create_batch(5)
        collection = PromptTurnCollection(turns=turns)

        result = collection.get_turns()

        assert result == turns
        assert len(result) == 5

    def test_get_turns_with_empty_list(self):
        """Test get_turns with an empty list of turns."""
        collection = PromptTurnCollection(turns=[])

        result = collection.get_turns()

        assert result == []
        assert len(result) == 0
