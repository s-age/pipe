import pytest
from pipe.core.models.prompt import Prompt
from pydantic import ValidationError


class TestPromptModel:
    """Tests for Prompt model validation and serialization."""

    @pytest.fixture
    def valid_prompt_data(self):
        """Returns valid data for Prompt model."""
        return {
            "description": "Main prompt description",
            "main_instruction": "Main instruction text",
            "current_task": {
                "type": "user_task",
                "instruction": "Current task instruction",
                "timestamp": "2025-01-01T00:00:00Z",
            },
            "current_datetime": "2025-01-01T00:00:00Z",
            "session_goal": {
                "description": "Goal description",
                "purpose": "Session purpose",
                "background": "Session background",
            },
            "roles": {
                "description": "Roles description",
                "definitions": ["Role definition 1"],
            },
            "constraints": {
                "language": "en",
                "processing_config": {"multi_step_reasoning_active": True},
                "hyperparameters": {"temperature": 0.7, "top_p": 0.9, "top_k": 40},
            },
            "conversation_history": {
                "description": "History description",
                "turns": [
                    {
                        "type": "user_task",
                        "instruction": "Previous instruction",
                        "timestamp": "2025-01-01T00:00:00Z",
                    }
                ],
            },
        }

    def test_valid_prompt_creation(self, valid_prompt_data):
        """Test creating a valid Prompt with all required fields."""
        prompt = Prompt.model_validate(valid_prompt_data)
        assert prompt.description == "Main prompt description"
        assert prompt.main_instruction == "Main instruction text"
        assert prompt.current_task.type == "user_task"
        assert prompt.constraints.language == "en"
        assert len(prompt.conversation_history.turns) == 1

    def test_prompt_validation_missing_required_field(self, valid_prompt_data):
        """Test that missing required fields raise ValidationError."""
        del valid_prompt_data["description"]
        with pytest.raises(ValidationError) as exc_info:
            Prompt.model_validate(valid_prompt_data)
        assert "description" in str(exc_info.value)

    def test_prompt_optional_fields(self, valid_prompt_data):
        """Test Prompt with optional fields like reasoning_process and todos."""
        valid_prompt_data["reasoning_process"] = {
            "description": "Reasoning description",
            "flowchart": "Reasoning flowchart",
        }
        valid_prompt_data["todos"] = [
            {"title": "Todo 1", "description": "Todo description", "checked": False}
        ]
        valid_prompt_data["procedure"] = "procedure/path"
        valid_prompt_data["procedure_content"] = "procedure content"

        prompt = Prompt.model_validate(valid_prompt_data)
        assert prompt.reasoning_process["description"] == "Reasoning description"
        assert prompt.todos[0].title == "Todo 1"
        assert prompt.procedure == "procedure/path"

    def test_prompt_serialization_camel_case(self, valid_prompt_data):
        """Test serialization with by_alias=True for camelCase conversion."""
        prompt = Prompt.model_validate(valid_prompt_data)
        dumped = prompt.model_dump(by_alias=True)

        assert dumped["mainInstruction"] == "Main instruction text"
        assert dumped["currentDatetime"] == "2025-01-01T00:00:00Z"
        assert dumped["sessionGoal"]["purpose"] == "Session purpose"
        assert (
            dumped["constraints"]["processingConfig"]["multiStepReasoningActive"]
            is True
        )

    def test_prompt_roundtrip_serialization(self, valid_prompt_data):
        """Test that serialization and deserialization preserve data."""
        original = Prompt.model_validate(valid_prompt_data)
        json_str = original.model_dump_json(by_alias=True)

        restored = Prompt.model_validate_json(json_str)
        assert restored.description == original.description
        assert restored.main_instruction == original.main_instruction
        assert restored.current_task.instruction == original.current_task.instruction
        assert restored.constraints.language == original.constraints.language
        assert len(restored.conversation_history.turns) == len(
            original.conversation_history.turns
        )
        assert restored == original
