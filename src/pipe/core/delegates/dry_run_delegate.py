from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService

def run(session_service: SessionService, prompt_service: PromptService):
    """
    Builds the prompt using PromptService and prints the resulting JSON.
    """
    prompt_model = prompt_service.build_prompt(session_service)
    
    # Use Pydantic's built-in JSON serialization
    print(prompt_model.model_dump_json(indent=2))

