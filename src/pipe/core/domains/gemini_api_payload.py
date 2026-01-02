"""
Orchestrator for payload generation and cache management.

This orchestrator manages the complete lifecycle of Gemini API request preparation:
- Tracks TokenCountSummary from API responses
- Orchestrates cache management and payload generation
"""

from google.genai import Client, types
from pipe.core.domains.gemini_api_dynamic_payload import GeminiApiDynamicPayload
from pipe.core.domains.gemini_cache_manager import GeminiCacheManager, TokenCountSummary
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings


class GeminiApiPayload:
    """
    Orchestrator for payload generation and cache management.

    This orchestrator maintains the state of:
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
        Initialize the payload orchestrator.

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
        self.last_dynamic_tokens: int = (
            0  # Track dynamic layer tokens from last request
        )

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
        tools: list[types.Tool] | None = None,
    ) -> tuple[list["Content"], str | None]:  # type: ignore[name-defined] # noqa: F821
        """
        Prepare the complete API request payload with cache management.

        Args:
            session: Current session object.
            prompt_factory: Factory to create Prompt objects.
            current_instruction: User's current input (optional).
            tools: List of tools to include in cache configuration (optional).

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
                tools=tools,
            )
        )

        # Update session state (cache_name is managed in .cache_registry.json)
        session.cached_turn_count = confirmed_cached_count

        # === Phase 2: Payload Construction ===
        # Build prompt object with buffered_history override
        prompt = prompt_factory.create(
            session=session,
            settings=self.settings,
            artifacts=session.artifacts,
            current_instruction=current_instruction,
        )

        # Override buffered_history with the assembled history from cache manager
        # Note: prompt.buffered_history expects list[Turn], not PromptConversationHistory
        prompt.buffered_history = buffered_history  # type: ignore[assignment]

        # If last turn is tool_response, insert a pseudo user_task to force continuation
        # This prevents the model from returning empty responses by treating the guidance
        # as a direct user command rather than a function response annotation
        if buffered_history and buffered_history[-1].type == "tool_response":
            from pipe.core.models.turn import UserTaskTurn
            from pipe.core.utils.datetime import get_current_timestamp

            pseudo_user_task = UserTaskTurn(
                type="user_task",
                instruction=(
                    "[IMPORTANT] The tool execution result is shown above. You MUST:\n"
                    "1. Review the user's original instruction to determine the next action\n"
                    "2. Continue working until the user's request is fully satisfied\n"
                    "3. DO NOT return an empty response\n"
                    "4. Tool results are for your internal use - provide meaningful output to the user"
                ),
                timestamp=get_current_timestamp(),
            )
            buffered_history.append(pseudo_user_task)
            prompt.buffered_history = buffered_history  # type: ignore[assignment]

        # Build contents following 4-layer architecture:
        # Layer 1 (Static) - only if no cache
        # Layer 2 (Dynamic) - always
        # Layer 3 (Buffered) - handled by dynamic_builder
        # Layer 4 (Trigger) - handled by dynamic_builder
        contents: list[types.Content] = []

        # Layer 1: Static (only if no cache exists)
        if cache_name is None:
            from pipe.core.domains import gemini_api_static_payload

            static_contents = gemini_api_static_payload.build(
                session=session,
                full_history=full_history,
                cached_turn_count=confirmed_cached_count,
                project_root=self.project_root,
                prompt_factory=prompt_factory,
                settings=self.settings,
            )
            contents.extend(static_contents)

        # Layers 2-4: Dynamic + Buffered + Trigger
        dynamic_builder = GeminiApiDynamicPayload(project_root=self.project_root)

        # Render dynamic JSON once and reuse it
        dynamic_json = dynamic_builder.render_dynamic_json(prompt=prompt)

        # Calculate dynamic layer token count
        from pipe.core.domains import gemini_token_count

        tokenizer = gemini_token_count.create_local_tokenizer(
            self.settings.model.name  # type: ignore[attr-defined]
        )
        self.last_dynamic_tokens = gemini_token_count.count_tokens(
            dynamic_json, tools=None, tokenizer=tokenizer
        )

        # Build full dynamic contents using the pre-rendered JSON
        dynamic_contents = dynamic_builder.build(
            prompt=prompt, dynamic_json=dynamic_json
        )
        contents.extend(dynamic_contents)

        return (contents, cache_name)

    def update_token_summary(self, usage_metadata: dict) -> None:  # type: ignore[type-arg]
        """
        Update token count summary from API response.

        Args:
            usage_metadata: Usage metadata from API response containing:
                - cached_content_token_count: Number of tokens in cache
                - prompt_token_count: Total number of tokens in prompt

        Note:
            Automatically subtracts self.last_dynamic_tokens from buffered_tokens
            to exclude Dynamic Layer (file_references, artifacts, etc.) from cache threshold calculation.
        """
        cached_tokens = usage_metadata.get("cached_content_token_count", 0)
        prompt_tokens = usage_metadata.get("prompt_token_count", 0)

        # Calculate buffered tokens and subtract dynamic layer tokens
        # buffered_tokens should only include conversation history, not dynamic context
        raw_buffered_tokens = prompt_tokens - cached_tokens
        adjusted_buffered_tokens = max(
            0, raw_buffered_tokens - self.last_dynamic_tokens
        )

        self.last_token_summary = TokenCountSummary(
            cached_tokens=cached_tokens,
            current_prompt_tokens=prompt_tokens,
            buffered_tokens=adjusted_buffered_tokens,
        )
