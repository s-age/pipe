import pytest
from pipe.core.models.prompts.constraints import (
    PromptConstraints,
    PromptHyperparameters,
    PromptProcessingConfig,
)
from pydantic import ValidationError


class TestPromptConstraintsModels:
    """Tests for prompt constraint models."""

    def test_prompt_hyperparameters_creation(self):
        """Test creating PromptHyperparameters with valid data."""
        params = PromptHyperparameters(temperature=0.7, top_p=0.9, top_k=40)
        assert params.temperature == 0.7
        assert params.top_p == 0.9
        assert params.top_k == 40

    def test_prompt_hyperparameters_none_values(self):
        """Test creating PromptHyperparameters with None values."""
        params = PromptHyperparameters(temperature=None, top_p=None, top_k=None)
        assert params.temperature is None
        assert params.top_p is None
        assert params.top_k is None

    def test_prompt_processing_config_creation(self):
        """Test creating PromptProcessingConfig."""
        config = PromptProcessingConfig(multi_step_reasoning_active=True)
        assert config.multi_step_reasoning_active is True

    def test_prompt_constraints_creation(self):
        """Test creating PromptConstraints with nested models."""
        hyperparams = PromptHyperparameters(temperature=0.5, top_p=None, top_k=None)
        config = PromptProcessingConfig(multi_step_reasoning_active=False)

        constraints = PromptConstraints(
            language="Japanese", processing_config=config, hyperparameters=hyperparams
        )

        assert constraints.language == "Japanese"
        assert constraints.processing_config.multi_step_reasoning_active is False
        assert constraints.hyperparameters.temperature == 0.5

    def test_prompt_constraints_missing_required(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError):
            # language and processing_config are required
            PromptConstraints(language="English")  # type: ignore

    def test_camel_case_alias_serialization(self):
        """Test that fields are serialized to camelCase using aliases."""
        config = PromptProcessingConfig(multi_step_reasoning_active=True)
        dumped = config.model_dump(by_alias=True)

        # multi_step_reasoning_active -> multiStepReasoningActive
        assert "multiStepReasoningActive" in dumped
        assert dumped["multiStepReasoningActive"] is True

    def test_camel_case_alias_deserialization(self):
        """Test that models can be created from camelCase data."""
        data = {
            "language": "English",
            "processingConfig": {"multiStepReasoningActive": True},
            "hyperparameters": {"temperature": 0.8, "topP": None, "topK": None},
        }
        constraints = PromptConstraints.model_validate(data)

        assert constraints.language == "English"
        assert constraints.processing_config.multi_step_reasoning_active is True
        assert constraints.hyperparameters is not None
        assert constraints.hyperparameters.temperature == 0.8

    def test_roundtrip_serialization(self):
        """Test serialization and deserialization roundtrip."""
        original = PromptConstraints(
            language="French",
            processing_config=PromptProcessingConfig(multi_step_reasoning_active=True),
            hyperparameters=PromptHyperparameters(
                temperature=0.2, top_p=0.5, top_k=None
            ),
        )

        # Serialize to dict with aliases
        dumped = original.model_dump(by_alias=True)

        # Validate back to model
        restored = PromptConstraints.model_validate(dumped)

        assert restored == original
