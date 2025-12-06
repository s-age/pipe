"""Base class for all agents in the pipe system."""

from abc import ABC, abstractmethod

from pipe.core.models.args import TaktArgs
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService


class BaseAgent(ABC):
    """Abstract base class for all agents.
    
    All agents must implement the run method which returns a tuple of:
    - model_response_text: The text response from the model
    - token_count: Number of tokens used (or None)
    - turns_to_save: List of Turn objects to save to the session
    """

    @abstractmethod
    def run(
        self,
        args: TaktArgs,
        session_service: SessionService,
        prompt_service: PromptService,
    ) -> tuple[str, int | None, list]:
        """Execute the agent and return results.
        
        Args:
            args: Command line arguments
            session_service: Service for session management
            prompt_service: Service for prompt building
            
        Returns:
            Tuple of (response_text, token_count, turns_to_save)
        """
        pass
