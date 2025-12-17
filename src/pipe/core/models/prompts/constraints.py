from typing import TYPE_CHECKING

from pipe.core.models.base import CamelCaseModel

if TYPE_CHECKING:
    from pipe.core.models.hyperparameters import Hyperparameters
    from pipe.core.models.settings import Settings


class PromptHyperparameters(CamelCaseModel):
    """Simplified hyperparameters for prompt rendering.

    Only contains the numeric values. Type and description are handled
    directly in the template (constraints.j2).
    """

    temperature: float | None
    top_p: float | None
    top_k: float | None

    @classmethod
    def from_hyperparameters(
        cls, hyperparameters: "Hyperparameters"
    ) -> "PromptHyperparameters":
        """Creates a PromptHyperparameters instance from Hyperparameters model."""
        return cls(
            temperature=hyperparameters.temperature,
            top_p=hyperparameters.top_p,
            top_k=hyperparameters.top_k,
        )


class PromptProcessingConfig(CamelCaseModel):
    """Processing configuration for prompt rendering.

    Description is handled directly in the template (constraints.j2).
    """

    multi_step_reasoning_active: bool


class PromptConstraints(CamelCaseModel):
    """Constraints for prompt rendering.

    Description is handled directly in the template (constraints.j2).
    """

    language: str
    processing_config: PromptProcessingConfig
    hyperparameters: PromptHyperparameters | None = None

    @classmethod
    def build(
        cls,
        settings: "Settings",
        hyperparameters: "Hyperparameters | None",
        multi_step_reasoning_enabled: bool,
    ) -> "PromptConstraints":
        """Builds the PromptConstraints component."""
        prompt_hyperparameters = None
        if hyperparameters:
            prompt_hyperparameters = PromptHyperparameters.from_hyperparameters(
                hyperparameters
            )

        return cls(
            language=settings.language,
            processing_config=PromptProcessingConfig(
                multi_step_reasoning_active=multi_step_reasoning_enabled,
            ),
            hyperparameters=prompt_hyperparameters,
        )
