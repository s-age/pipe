# This script utilizes the 'google-genai' library to interact with the Gemini API.
# It is important to note that 'google-genai' is the newer, recommended library,
# and should be used in place of the older 'google-generativeai' library to ensure
# access to the latest features and improvements.
# For reference, see: https://pypi.org/project/google-genai/

import hashlib
import importlib.util
import inspect
import json
import logging
import os
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Union, get_args, get_type_hints

import google.genai as genai
from google.genai import types
from jinja2 import Environment, FileSystemLoader
from pipe.core.agents import register_agent
from pipe.core.agents.base import BaseAgent
from pipe.core.models.args import TaktArgs
from pipe.core.services.token_service import TokenService

if TYPE_CHECKING:
    from pipe.core.services.prompt_service import PromptService
    from pipe.core.services.session_service import SessionService

# Configure logging
log_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "debug.log")
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=log_file_path,
    filemode="w",  # Overwrite the log file on each run
)

# Suppress genai logging
logging.getLogger("google.genai").setLevel(logging.WARNING)


def load_tools(project_root: str) -> list:
    """
    Scans the 'tools' directory to discover available tool scripts and generates
    JSON schema definitions compatible with google-genai for each tool.
    """
    tool_defs = []
    type_mapping = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
    }

    tools_dir = os.path.join(project_root, "src", "pipe", "core", "tools")

    try:
        filenames = os.listdir(tools_dir)
    except Exception:
        return []

    for filename in filenames:
        if not (filename.endswith(".py") and not filename.startswith("__")):
            continue

        tool_name = os.path.splitext(filename)[0]
        tool_file_path = os.path.join(tools_dir, filename)

        try:
            spec = importlib.util.spec_from_file_location(
                f"pipe.core.tools.{tool_name}", tool_file_path
            )
            if not spec or not spec.loader:
                continue
            tool_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tool_module)

            if not hasattr(tool_module, tool_name):
                continue

            tool_function = getattr(tool_module, tool_name)
            sig = inspect.signature(tool_function)
            type_hints = get_type_hints(tool_function)

            description = (
                inspect.getdoc(tool_function) or f"Executes the {tool_name} tool."
            )

            properties = {}
            required = []

            for name, param in sig.parameters.items():
                if name in [
                    "session_service",
                    "session_id",
                    "settings",
                    "project_root",
                ]:
                    continue

                param_type = type_hints.get(name, str)
                is_optional = False
                origin_type = getattr(param_type, "__origin__", None)

                if origin_type is Union:
                    union_args = get_args(param_type)
                    if len(union_args) == 2 and type(None) in union_args:
                        is_optional = True
                        param_type = next(t for t in union_args if t is not type(None))
                        origin_type = getattr(param_type, "__origin__", None)

                if origin_type in (list, list):
                    list_item_type = (
                        get_args(param_type)[0] if get_args(param_type) else str
                    )
                    item_origin_type = getattr(list_item_type, "__origin__", None)
                    if item_origin_type in (dict, dict):
                        properties[name] = {
                            "type": "array",
                            "items": {"type": "object"},
                        }
                    else:
                        mapped_item_type = type_mapping.get(list_item_type, "string")
                        properties[name] = {
                            "type": "array",
                            "items": {"type": mapped_item_type},
                        }
                elif origin_type in (dict, dict):
                    properties[name] = {"type": "object", "properties": {}}
                else:
                    mapped_type = type_mapping.get(param_type, "string")
                    properties[name] = {"type": mapped_type}

                if param.default is inspect.Parameter.empty and not is_optional:
                    required.append(name)

            tool_def = {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            tool_defs.append(tool_def)

        except Exception:
            pass

    return tool_defs


def get_cached_content(
    client: genai.Client,
    static_content: str,
    model_name: str,
    project_root: str,
    tools: list[types.Tool],
):
    """
    Manages cache creation and retrieval.
    Persists cache IDs to a local file to reuse them across CLI executions.
    """
    cache_registry_path = os.path.join(project_root, "sessions", ".cache_registry.json")

    # Calculate hash of the static content + tools
    # Tools are serialized using their string representation
    tools_str = str(tools) if tools else ""
    combined_content = static_content + tools_str
    content_hash = hashlib.md5(combined_content.encode("utf-8")).hexdigest()

    cache_registry = {}
    if os.path.exists(cache_registry_path):
        try:
            with open(cache_registry_path, encoding="utf-8") as f:
                cache_registry = json.load(f)
        except Exception:
            pass

    # Check if we have a valid cache for this content
    cached_info = cache_registry.get(content_hash)
    cache_name = None

    if cached_info:
        cache_name = cached_info.get("name")
        expire_time_str = cached_info.get("expire_time")

        # Check if expired locally (rough check)
        if expire_time_str:
            expire_time = datetime.fromisoformat(expire_time_str)
            if datetime.now() > expire_time:
                cache_name = None  # Expired

        # Verify existence with API
        if cache_name:
            try:
                # API Call to check if cache really exists and is valid
                client.caches.get(name=cache_name)
                logging.info(f"Cache HIT: Using existing cache {cache_name}")
                return cache_name
            except Exception:
                logging.warning(
                    f"Cache registry invalid or expired on server: {cache_name}"
                )
                cache_name = None

    # Create new cache if not found or expired
    if not cache_name:
        logging.info("Cache MISS: Creating new context cache...")
        try:
            # Create cache with 1 hour TTL, including tools
            cached_obj = client.caches.create(
                model=model_name,
                config={
                    "system_instruction": static_content,
                    "tools": tools,  # type: ignore[typeddict-item]
                    "ttl": "3600s",  # 1 hour
                },
            )
            cache_name = cached_obj.name

            # Save to registry
            # Calculate local expiration time (slightly conservative)
            expire_time = datetime.now() + timedelta(minutes=55)
            cache_registry[content_hash] = {
                "name": cache_name,
                "expire_time": expire_time.isoformat(),
            }

            os.makedirs(os.path.dirname(cache_registry_path), exist_ok=True)
            with open(cache_registry_path, "w", encoding="utf-8") as f:
                json.dump(cache_registry, f, indent=2)

            logging.info(f"Cache Created: {cache_name}")
        except Exception as e:
            logging.error(f"Failed to create cache: {e}")
            return None

    return cache_name


def call_gemini_api(session_service: "SessionService", prompt_service: "PromptService"):
    settings = session_service.settings
    session_data = session_service.current_session
    project_root = session_service.project_root

    os.environ["PIPE_SESSION_ID"] = session_data.session_id

    sessions_dir = os.path.join(project_root, "sessions")
    token_service = TokenService(settings=settings)

    # 1. Build the Prompt model
    prompt_model = prompt_service.build_prompt(session_service)
    context = prompt_model.model_dump()

    # 2. Render Prompt: SPLIT into Static (Cache) and Dynamic (Payload)
    template_env = Environment(
        loader=FileSystemLoader(
            os.path.join(prompt_service.project_root, "templates", "prompt")
        ),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    static_content_string = ""
    dynamic_content_string = ""

    # Try to load separate templates for caching architecture
    try:
        # Cache strategy is now handled by GeminiCache domain in PromptFactory
        # The prompt_model already has cached_history and buffered_history populated
        cached_history = context.get("cached_history")
        buffered_history = context.get("buffered_history")

        # Log cache strategy statistics
        cached_turns = len(cached_history["turns"]) if cached_history else 0
        buffered_turns = len(buffered_history["turns"]) if buffered_history else 0
        total_turns = cached_turns + buffered_turns

        logging.info(
            f"Cache strategy: Total turns={total_turns}, "
            f"Cached turns={cached_turns}, "
            f"Buffered turns={buffered_turns}"
        )

        # Static: System instructions + cached conversation history
        static_template = template_env.get_template("gemini_static_prompt.j2")
        static_content_string = static_template.render(session=context)

        # Dynamic: Buffered history + file_references + artifacts + todos + current_task
        dynamic_template = template_env.get_template("gemini_dynamic_prompt.j2")
        dynamic_content_string = dynamic_template.render(session=context)

        logging.info(
            f"Rendered content sizes: Static={len(static_content_string)} chars, "
            f"Dynamic={len(dynamic_content_string)} chars"
        )

    except Exception as e:
        # Fallback for backward compatibility
        logging.warning(
            f"Split templates not found ({e}). "
            "Falling back to monolithic prompt (NO CACHE)."
        )
        template = template_env.get_template("gemini_api_prompt.j2")
        full_string = template.render(session=context)
        dynamic_content_string = full_string
        static_content_string = ""

    # Load tools
    loaded_tools_data = load_tools(project_root)

    # Calculate token count (approximate for limit check)
    full_text_for_check = (static_content_string or "") + dynamic_content_string
    token_count = token_service.count_tokens(
        full_text_for_check, tools=loaded_tools_data
    )

    is_within_limit, message = token_service.check_limit(token_count)
    if not is_within_limit:
        raise ValueError("Prompt exceeds context window limit. Aborting.")

    # Config Setup
    gen_config_params = {
        "temperature": settings.parameters.temperature.value,
        "top_p": settings.parameters.top_p.value,
        "top_k": settings.parameters.top_k.value,
    }

    if session_params := session_data.hyperparameters:
        if temp_val := session_params.temperature:
            gen_config_params["temperature"] = temp_val
        if top_p_val := session_params.top_p:
            gen_config_params["top_p"] = top_p_val
        if top_k_val := session_params.top_k:
            gen_config_params["top_k"] = top_k_val

    # Convert tools to types.Tool objects
    converted_tools = []
    for tool_data in loaded_tools_data:
        parameters_schema = types.Schema(**tool_data.get("parameters", {}))
        converted_tools.append(
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        parameters=parameters_schema,
                    )
                ]
            )
        )

    all_tools: list[types.Tool] = converted_tools
    logging.debug(
        "Final tools passed to Gemini API: "
        f"{[
            func.name for tool in all_tools
            for func in (tool.function_declarations or [])
        ]}"
    )

    # Client initialization
    client = genai.Client()

    # 3. Handle Caching based on token thresholds
    from pipe.core.domains.gemini_cache import GeminiCache
    from pipe.core.repositories.streaming_log_repository import StreamingLogRepository

    gemini_cache = GeminiCache(tool_response_limit=settings.tool_response_expiration)

    # Calculate buffered tokens (not yet cached)
    buffered_tokens = (
        session_data.token_count - session_data.cached_content_token_count
        if session_data.cached_content_token_count > 0
        else session_data.token_count
    )

    # Determine if we should create/update cache
    should_cache = gemini_cache.should_update_cache(buffered_tokens)

    # Get streaming log repository for cache decision logging
    log_file_path = os.path.join(
        sessions_dir, f"{session_data.session_id}.streaming.log"
    )
    streaming_log_repo = StreamingLogRepository(log_file_path)
    try:
        if not streaming_log_repo.file_handle:
            streaming_log_repo.file_handle = open(log_file_path, "a", encoding="utf-8")
    except Exception:
        pass

    cached_content_name = None
    content_to_send = dynamic_content_string  # Default: send only dynamic

    if should_cache and static_content_string:
        # Create or update cache with static content
        cache_msg = (
            f"Cache decision: CREATING/UPDATING cache. "
            f"Current cached_tokens={session_data.cached_content_token_count}, "
            f"Current prompt_tokens={session_data.token_count}, "
            f"Buffered tokens={buffered_tokens}"
        )
        logging.info(cache_msg)
        streaming_log_repo.write_log_line("CACHE_DECISION", cache_msg, datetime.now())

        cached_content_name = get_cached_content(
            client,
            static_content_string,
            token_service.model_name,
            project_root,
            all_tools,
        )
    elif not session_data.cached_content_token_count:
        # No cache exists and below threshold: send static + dynamic
        cache_msg = (
            f"Cache decision: NO CACHE (below threshold). "
            f"Current prompt_tokens={session_data.token_count}, "
            f"Threshold={gemini_cache.CACHE_UPDATE_THRESHOLD}. "
            f"Sending static + dynamic content"
        )
        logging.info(cache_msg)
        streaming_log_repo.write_log_line("CACHE_DECISION", cache_msg, datetime.now())

        content_to_send = static_content_string + "\n" + dynamic_content_string
    else:
        # Cache exists but not updating: use existing cache
        cache_msg = (
            f"Cache decision: USING EXISTING cache (buffered below threshold). "
            f"Current cached_tokens={session_data.cached_content_token_count}, "
            f"Current prompt_tokens={session_data.token_count}, "
            f"Buffered tokens={buffered_tokens}, "
            f"Threshold={gemini_cache.CACHE_UPDATE_THRESHOLD}"
        )
        logging.info(cache_msg)
        streaming_log_repo.write_log_line("CACHE_DECISION", cache_msg, datetime.now())

        # Try to get existing cache
        if static_content_string:
            try:
                cached_content_name = get_cached_content(
                    client,
                    static_content_string,
                    token_service.model_name,
                    project_root,
                    all_tools,
                )
            except Exception as e:
                logging.warning(f"Failed to retrieve cache: {e}")
                content_to_send = static_content_string + "\n" + dynamic_content_string

    # If using cache, don't pass tools again (they're in the cache)
    config = types.GenerateContentConfig(
        tools=None if cached_content_name else all_tools,  # type: ignore[arg-type]
        temperature=gen_config_params.get("temperature"),
        top_p=gen_config_params.get("top_p"),
        top_k=gen_config_params.get("top_k"),
        cached_content=cached_content_name,  # Pass the cache name here
    )

    # Logging setup
    from pipe.core.repositories.streaming_log_repository import StreamingLogRepository

    log_file_path = os.path.join(
        sessions_dir, f"{session_data.session_id}.streaming.log"
    )
    raw_chunk_repo = StreamingLogRepository(log_file_path)
    try:
        if not raw_chunk_repo.file_handle:
            raw_chunk_repo.file_handle = open(log_file_path, "a", encoding="utf-8")
    except Exception:
        pass

    try:
        # 4. Generate Content (Sending dynamic or static+dynamic based on cache status)
        logging.info(
            f"Sending request. Cache: "
            f"{'HIT ('+cached_content_name+')' if cached_content_name else 'MISS'}, "
            f"Content length: {len(content_to_send)} chars"
        )

        stream = client.models.generate_content_stream(
            contents=content_to_send, config=config, model=token_service.model_name
        )

        for chunk in stream:
            try:
                if hasattr(chunk, "to_dict"):
                    chunk_dict = chunk.to_dict()  # type: ignore[attr-defined]
                else:
                    chunk_dict = {"raw": str(chunk)}
                raw_chunk_repo.write_log_line(
                    "RAW_CHUNK",
                    json.dumps(chunk_dict, ensure_ascii=False, default=str),
                    datetime.now(),
                )
            except Exception:
                try:
                    raw_chunk_repo.write_log_line(
                        "RAW_CHUNK",
                        json.dumps({"raw": str(chunk)}, ensure_ascii=False),
                        datetime.now(),
                    )
                except Exception:
                    pass
            yield chunk
    except Exception as e:
        raise RuntimeError(f"Error during Gemini API execution: {e}")


@register_agent("gemini-api")
class GeminiApiAgent(BaseAgent):
    """Agent for Gemini API streaming mode."""

    def run(
        self,
        args: TaktArgs,
        session_service: "SessionService",
        prompt_service: "PromptService",
    ) -> tuple[str, int | None, list]:
        """Execute the Gemini API agent.

        This wraps the streaming call_gemini_api function and returns
        the final result after all streaming is complete.

        Args:
            args: Command line arguments
            session_service: Service for session management
            prompt_service: Service for prompt building

        Returns:
            Tuple of (response_text, token_count, turns_to_save)
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_api_delegate
        from pipe.core.services.session_turn_service import SessionTurnService

        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )
        stream_results = list(
            gemini_api_delegate.run_stream(
                args, session_service, prompt_service, session_turn_service
            )
        )
        # The last yielded item contains the final result
        _, model_response_text, token_count, turns_to_save = stream_results[-1]

        return model_response_text, token_count, turns_to_save

    def run_stream(
        self,
        args: TaktArgs,
        session_service: "SessionService",
        prompt_service: "PromptService",
    ):
        """Execute the Gemini API agent in streaming mode.

        This method yields intermediate results for WebUI streaming support.

        Args:
            args: Command line arguments
            session_service: Service for session management
            prompt_service: Service for prompt building

        Yields:
            Intermediate streaming results and final tuple
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_api_delegate
        from pipe.core.services.session_turn_service import SessionTurnService

        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )
        yield from gemini_api_delegate.run_stream(
            args, session_service, prompt_service, session_turn_service
        )
