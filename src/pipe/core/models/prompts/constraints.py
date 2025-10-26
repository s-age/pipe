from pydantic import BaseModel

class PromptHyperparameter(BaseModel):
    type: str
    value: float
    description: str

class PromptHyperparameters(BaseModel):
    description: str
    temperature: PromptHyperparameter
    top_p: PromptHyperparameter
    top_k: PromptHyperparameter

class PromptProcessingConfig(BaseModel):
    description: str
    multi_step_reasoning_active: bool

class PromptConstraints(BaseModel):
    description: str
    language: str
    processing_config: PromptProcessingConfig
    hyperparameters: PromptHyperparameters
