"""Gemini API Payload Models.

This module defines the payload structures for the Gemini API,
implementing the 4-layer architecture documented in docs/gemini-api-structure.md.

The 4 layers are grouped into 2 dataclasses based on cache lifecycle:
- GeminiApiStaticPayload: Layers 1-2 (History Management)
- GeminiApiDynamicPayload: Layers 3-4 (Execution Management)
"""

from dataclasses import dataclass

from google.genai import types


@dataclass
class GeminiApiStaticPayload:
    """
    Static/Cacheable part of the payload (History Management).

    Contains:
    - Layer 1 (Static): Immutable system instructions (cacheable)
    - Layer 3 (Buffered): Recent history with thought_signature (cache candidate)

    Design Note:
        Layer 1 and Layer 3 are grouped together because they share the same
        cache lifecycle. Buffered history represents "next cache update candidates"
        and logically extends the cached_content.
    """

    cached_content: str  # Layer 1: from gemini_static_prompt.j2
    buffered_history: list[types.Content]  # Layer 3: with thought_signature


@dataclass
class GeminiApiDynamicPayload:
    """
    Dynamic/Volatile part of the payload (Execution Management).

    Contains:
    - Layer 2 (Dynamic): Current project state (files, artifacts, todos, datetime)
    - Layer 4 (Trigger): Execution trigger (user task or tool response)

    Design Note:
        Layer 2 and Layer 4 are grouped together because they represent
        the "current execution context": what the project looks like NOW (Layer 2)
        and what action to take NOW (Layer 4).
    """

    dynamic_content: str  # Layer 2: JSON (files, artifacts, todos, datetime)
    current_instruction: types.Content | None  # Layer 4: User task or tool response
