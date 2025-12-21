from typing import TYPE_CHECKING

from pipe.core.models.base import CamelCaseModel

if TYPE_CHECKING:
    pass


class PromptHyperparameters(CamelCaseModel):
    """Simplified hyperparameters for prompt rendering.

    Only contains the numeric values. Type and description are handled
    directly in the template (constraints.j2).
    """

    temperature: float | None
    top_p: float | None
    top_k: float | None


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
