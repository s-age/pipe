"""
Service orchestrator for payload generation and cache management.

This service manages the complete lifecycle of Gemini API request preparation:
- Tracks TokenCountSummary from API responses
- Orchestrates cache management and payload generation
"""

from google.genai import Client
from pipe.core.domains.gemini_api_dynamic_payload import GeminiApiDynamicPayload
from pipe.core.domains.gemini_cache_manager import GeminiCacheManager, TokenCountSummary
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings


class GeminiPayloadService:
    """
    Service to orchestrate payload generation and cache management.

    This service maintains the state of:
    - Token count summary from the last API response
    - Cache manager instance for cache lifecycle management

    Usage Flow:
    1. Call prepare_request() with session and current_instruction
    2. Use returned contents and cache_name for API call
    3. Call update_token_summary() with usage_metadata from API response
    """

    def __init__(
        self,
        client: Client,
        project_root: str,
        settings: Settings,
    ):
        """
        Initialize the payload service.

        Args:
            client: Gemini API client for cache operations.
            project_root: Path to project root for template loading.
            settings: Application settings containing model config.
        """
        self.client = client
        self.project_root = project_root
        self.settings = settings

        # Internal state
        self.last_token_summary: TokenCountSummary = {
            "cached_tokens": 0,
            "current_prompt_tokens": 0,
            "buffered_tokens": 0,
        }

        # Cache manager instance (created once, reused across requests)
        from google.genai.types import Content  # noqa: F401

        # Note: settings.model is already a ModelConfig object after validation
        if not hasattr(settings.model, "name"):
            raise ValueError("settings.model must be a ModelConfig object")

        self.cache_manager = GeminiCacheManager(
            client=client,
            project_root=project_root,
            model_name=settings.model.name,  # type: ignore[attr-defined]
            cache_update_threshold=settings.model.cache_update_threshold,  # type: ignore[attr-defined]
            prompt_factory=None,  # Will be set in prepare_request
            settings=settings,
        )

    def prepare_request(
        self,
        session: Session,
        prompt_factory: "PromptFactory",  # type: ignore[name-defined] # noqa: F821
        current_instruction: str | None = None,
    ) -> tuple[list["Content"], str | None]:  # type: ignore[name-defined] # noqa: F821
        """
        Prepare the complete API request payload with cache management.

        Args:
            session: Current session object.
            prompt_factory: Factory to create Prompt objects.
            current_instruction: User's current input (optional).

        Returns:
            tuple: (contents, cache_name)
                - contents: List of Content objects for API request
                - cache_name: Name of active cache, or None if no cache is used

        Flow:
            1. Run cache management (assemble buffered history, decide update)
            2. Update session state (cache_name, cached_turn_count)
            3. Build Prompt object with buffered_history
            4. Generate dynamic payload contents
        """
        from google.genai import types

        # === Phase 1: Cache Management ===
        # Set prompt_factory in cache_manager (needed for static payload generation)
        self.cache_manager.prompt_factory = prompt_factory

        full_history = session.turns

        cache_name, confirmed_cached_count, buffered_history = (
            self.cache_manager.update_if_needed(
                session=session,
                full_history=full_history,
                token_count_summary=self.last_token_summary,
                threshold=self.settings.model.cache_update_threshold,  # type: ignore[attr-defined]
            )
        )

        # Update session state (cache_name is managed in .cache_registry.json)
        session.cached_turn_count = confirmed_cached_count

        # === Phase 2: Payload Construction ===
        prompt = prompt_factory.create(
            session=session,
            settings=self.settings,
            artifacts=session.artifacts,
            current_instruction=current_instruction,
        )

        # Override buffered_history with the assembled history from cache manager
        # Note: prompt.buffered_history expects list[Turn], not PromptConversationHistory
        prompt.buffered_history = buffered_history  # type: ignore[assignment]

        dynamic_builder = GeminiApiDynamicPayload(project_root=self.project_root)
        contents: list[types.Content] = dynamic_builder.build(prompt=prompt)

        return (contents, cache_name)

    def update_token_summary(self, usage_metadata: dict) -> None:  # type: ignore[type-arg]
        """
        Update token count summary from API response.

        Args:
            usage_metadata: Usage metadata from API response containing:
                - cached_content_token_count: Number of tokens in cache
                - prompt_token_count: Total number of tokens in prompt
        """
        cached_tokens = usage_metadata.get("cached_content_token_count", 0)
        prompt_tokens = usage_metadata.get("prompt_token_count", 0)

        self.last_token_summary = TokenCountSummary(
            cached_tokens=cached_tokens,
            current_prompt_tokens=prompt_tokens,
            buffered_tokens=prompt_tokens - cached_tokens,
        )
