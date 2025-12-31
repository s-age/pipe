"""
Data Generation Layer 1: Cache creation content list construction.

Builds the static (cacheable) content list for Gemini API cache creation
using the gemini_static_prompt.j2 template.
"""

from __future__ import annotations

import json
import os

from google.genai import types
from jinja2 import Environment, FileSystemLoader
from pipe.core.models.session import Session
from pipe.core.models.turn import Turn


def build(
    session: Session,
    full_history: list[Turn],
    cached_turn_count: int,
    project_root: str,
    prompt_factory: PromptFactory | None = None,  # type: ignore[name-defined] # noqa: F821
    settings: Settings | None = None,  # type: ignore[name-defined] # noqa: F821
) -> list[types.Content]:
    """
    Construct the full list of contents to be cached.

    This function renders the static template with cached history to create
    the content list suitable for client.caches.create(contents=...).

    Args:
        session: Session object (used for template rendering context).
        full_history: Complete list of all Turn objects from session history.
        cached_turn_count: Number of turns to include in the cache (slicing boundary).
        project_root: Path to project root for template loading.

    Returns:
        List of Content objects ready for cache creation.

    Internal Logic:
        1. Extract Cached History: Slice full_history[:cached_turn_count]
        2. Render Static Template (Layer 1): Load gemini_static_prompt.j2
        3. Convert to Content: Create Content(role="user", parts=[Part(text=...)])
    """
    # Step 1: Extract cached history
    cached_history = full_history[:cached_turn_count]

    # Step 1.5: Generate Prompt object using PromptFactory
    # This ensures all prompt attributes (constraints, session_goal, etc.) are properly initialized
    if not prompt_factory or not settings:
        raise ValueError(
            "prompt_factory and settings are required for static payload generation"
        )

    prompt = prompt_factory.create(
        session=session,
        settings=settings,
        artifacts=session.artifacts,
        current_instruction=None,
    )

    # Step 2: Render static template
    template_path = os.path.join(project_root, "templates", "prompt")
    jinja_env = Environment(
        loader=FileSystemLoader(template_path),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Configure tojson filter to disable ASCII escaping (prevent \uXXXX for non-ASCII chars)
    def tojson_filter(value):
        return json.dumps(value, ensure_ascii=False)

    jinja_env.filters["tojson"] = tojson_filter

    # Add custom filter to serialize Pydantic models to dict for JSON serialization
    def pydantic_dump(obj):
        """Convert Pydantic model to dict using model_dump()."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return obj

    jinja_env.filters["pydantic_dump"] = pydantic_dump

    template = jinja_env.get_template("gemini_static_prompt.j2")

    # Pass prompt object (has all required attributes like constraints, session_goal)
    # with cached_history override
    rendered_json = template.render(
        session=prompt,
        cached_history=cached_history,
    )

    # Step 3: Convert to Content
    content = types.Content(
        role="user",
        parts=[types.Part(text=rendered_json)],
    )

    return [content]
