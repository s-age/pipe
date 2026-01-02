from pipe.core.collections.prompts.turn_collection import PromptTurnCollection

from tests.factories.models.turn_factory import TurnFactory


class TestPromptTurnCollection:
    """Tests for PromptTurnCollection."""

    def test_init(self):
        """Test initialization of PromptTurnCollection."""
        turns = TurnFactory.create_batch(2)
        token_limit = 1000
        collection = PromptTurnCollection(turns=turns, token_limit=token_limit)

        assert collection._turns == turns
        assert collection.token_limit == token_limit

    def test_get_turns_returns_all_turns(self):
        """
        Test that get_turns returns all turns.
        Note: Current implementation is a placeholder that returns all turns.
        """
        turns = TurnFactory.create_batch(3)
        collection = PromptTurnCollection(turns=turns)

        result = collection.get_turns()

        assert result == turns
        assert len(result) == 3

    def test_get_turns_empty(self):
        """Test get_turns with an empty collection."""
        collection = PromptTurnCollection(turns=[])

        result = collection.get_turns()

        assert result == []
        assert len(result) == 0

    def test_token_limit_default(self):
        """Test default token limit."""
        collection = PromptTurnCollection(turns=[])
        assert collection.token_limit == 120000
