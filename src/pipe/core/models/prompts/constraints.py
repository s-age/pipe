from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from pipe.core.models.settings import Settings


class PromptHyperparameter(BaseModel):
    type: str
    value: float
    description: str


class PromptHyperparameters(BaseModel):
    description: str
    temperature: PromptHyperparameter
    top_p: PromptHyperparameter
    top_k: PromptHyperparameter

    @classmethod
    def from_merged_params(cls, merged_params: dict) -> "PromptHyperparameters":
        """
        Creates a PromptHyperparameters instance from a merged parameters dictionary.
        """
        return cls(
            description="Hyperparameter settings for the model.",
            temperature=PromptHyperparameter(
                type="number", **merged_params["temperature"]
            ),
            top_p=PromptHyperparameter(type="number", **merged_params["top_p"]),
            top_k=PromptHyperparameter(type="number", **merged_params["top_k"]),
        )


class PromptProcessingConfig(BaseModel):
    description: str
    multi_step_reasoning_active: bool


class PromptConstraints(BaseModel):
    description: str
    language: str
    processing_config: PromptProcessingConfig
    hyperparameters: PromptHyperparameters

    @classmethod
    def build(
        cls,
        settings: "Settings",
        hyperparameters: PromptHyperparameters,
        multi_step_reasoning_enabled: bool,
    ) -> "PromptConstraints":
        """Builds the PromptConstraints component."""
        return cls(
            description="Constraints for the model.",
            language=settings.language,
            processing_config=PromptProcessingConfig(
                description="Configuration for processing.",
                multi_step_reasoning_active=multi_step_reasoning_enabled,
            ),
            hyperparameters=hyperparameters,
        )
