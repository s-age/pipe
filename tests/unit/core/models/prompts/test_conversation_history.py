import pytest
from pipe.core.models.prompts.conversation_history import PromptConversationHistory
from pydantic import ValidationError

from tests.factories.models.turn_factory import TurnFactory


class TestPromptConversationHistory:
    """Tests for PromptConversationHistory model."""

    def test_valid_creation(self):
        """Test creating PromptConversationHistory with valid data."""
        turns = TurnFactory.create_batch(2)
        history = PromptConversationHistory(
            description="Test conversation history", turns=turns
        )
        assert history.description == "Test conversation history"
        assert len(history.turns) == 2
        assert history.turns[0].type == "user_task"
        assert history.turns[1].type == "model_response"

    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError):
            PromptConversationHistory(description="Missing turns")  # type: ignore

        with pytest.raises(ValidationError):
            PromptConversationHistory(turns=[])  # type: ignore

    def test_serialization_camel_case(self):
        """Test serialization to camelCase."""
        turns = [
            TurnFactory.create_user_task(instruction="Hello"),
            TurnFactory.create_model_response(content="Hi there"),
        ]
        history = PromptConversationHistory(description="Greeting", turns=turns)

        dumped = history.model_dump(by_alias=True)

        # description and turns are already camelCase (or don't change),
        # but let's check nested fields if any.
        assert dumped["description"] == "Greeting"
        assert len(dumped["turns"]) == 2

        # UserTaskTurn nested serialization check
        # Turn models are also CamelCaseModel
        assert dumped["turns"][0]["instruction"] == "Hello"
        assert dumped["turns"][0]["type"] == "user_task"

    def test_deserialization(self):
        """Test deserialization from dict."""
        data = {
            "description": "Historical context",
            "turns": [
                {
                    "type": "user_task",
                    "instruction": "Tell me a joke",
                    "timestamp": "2025-01-01T12:00:00Z",
                },
                {
                    "type": "model_response",
                    "content": "Why did the chicken cross the road?",
                    "timestamp": "2025-01-01T12:00:05Z",
                },
            ],
        }

        history = PromptConversationHistory.model_validate(data)

        assert history.description == "Historical context"
        assert len(history.turns) == 2
        assert history.turns[0].type == "user_task"
        assert history.turns[0].instruction == "Tell me a joke"

    def test_roundtrip_serialization(self):
        """Test serialization and deserialization roundtrip."""
        turns = TurnFactory.create_batch(3)
        original = PromptConversationHistory(description="Roundtrip test", turns=turns)

        json_str = original.model_dump_json(by_alias=True)
        restored = PromptConversationHistory.model_validate_json(json_str)

        assert restored.description == original.description
        assert len(restored.turns) == len(original.turns)
        for r_turn, o_turn in zip(restored.turns, original.turns):
            assert r_turn.type == o_turn.type
            assert r_turn.timestamp == o_turn.timestamp
