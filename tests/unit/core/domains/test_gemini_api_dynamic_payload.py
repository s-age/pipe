"""Unit tests for gemini_api_dynamic_payload module."""

import json
from unittest.mock import MagicMock, patch

import pytest
from google.genai import types
from pipe.core.domains.gemini_api_dynamic_payload import GeminiApiDynamicPayload
from pipe.core.models.artifact import Artifact
from pipe.core.models.prompt import Prompt
from pipe.core.models.prompts.current_task import PromptCurrentTask
from pipe.core.models.prompts.file_reference import PromptFileReference
from pipe.core.models.prompts.todo import PromptTodo
from pipe.core.models.turn import (
    FunctionCallingTurn,
    ModelResponseTurn,
    UserTaskTurn,
)


@pytest.fixture
def builder():
    """Create a builder instance."""
    return GeminiApiDynamicPayload(project_root="/test/project")


@pytest.fixture
def mock_prompt():
    """Create a mock prompt with minimal fields."""
    return MagicMock(spec=Prompt)


class TestGeminiApiDynamicPayload:
    """Test cases for GeminiApiDynamicPayload class."""

    def test_init(self):
        """Test builder initialization."""
        builder = GeminiApiDynamicPayload(project_root="/test/project")
        assert builder.project_root == "/test/project"

    def test_build_with_empty_prompt(self, builder, mock_prompt):
        """Test build with minimal empty prompt."""
        mock_prompt.file_references = None
        mock_prompt.artifacts = None
        mock_prompt.todos = None
        mock_prompt.current_datetime = "2025-01-01T00:00:00Z"
        mock_prompt.buffered_history = None
        mock_prompt.current_task = None

        with patch.object(
            builder, "_build_dynamic_context", return_value=None
        ) as mock_context:
            result = builder.build(mock_prompt)

            mock_context.assert_called_once_with(mock_prompt)
            assert isinstance(result, list)
            assert len(result) == 0

    def test_build_with_current_task_only(self, builder, mock_prompt):
        """Test build with only current task."""
        mock_prompt.file_references = None
        mock_prompt.artifacts = None
        mock_prompt.todos = None
        mock_prompt.current_datetime = "2025-01-01T00:00:00Z"
        mock_prompt.buffered_history = None
        mock_prompt.current_task = PromptCurrentTask(
            type="user_task",
            instruction="Test instruction",
            timestamp="2025-01-01T00:00:00Z",
        )

        with patch.object(builder, "_build_dynamic_context", return_value=None):
            result = builder.build(mock_prompt)

            assert len(result) == 1
            assert isinstance(result[0], types.Content)
            assert result[0].role == "user"
            assert result[0].parts is not None
            assert len(result[0].parts) == 1
            assert result[0].parts[0].text == "Test instruction"

    def test_build_with_all_layers(self, builder, mock_prompt):
        """Test build with all layers (dynamic context, buffered history, current task)."""
        mock_prompt.current_task = PromptCurrentTask(
            type="user_task",
            instruction="Do something",
            timestamp="2025-01-01T00:00:00Z",
        )
        mock_prompt.buffered_history = [
            UserTaskTurn(
                type="user_task",
                instruction="Previous task",
                timestamp="2025-01-01T00:00:01Z",
            )
        ]

        mock_dynamic_content = types.Content(
            role="user",
            parts=[types.Part(text='{"dynamic": "context"}')],
        )

        with patch.object(
            builder, "_build_dynamic_context", return_value=mock_dynamic_content
        ):
            result = builder.build(mock_prompt)

            # Should have: dynamic context + buffered history + current task
            assert len(result) == 3
            assert result[0] == mock_dynamic_content
            assert result[1].role == "user"
            assert result[1].parts is not None
            assert result[1].parts[0].text == "Previous task"
            assert result[2].role == "user"
            assert result[2].parts is not None
            assert result[2].parts[0].text == "Do something"


class TestBuildDynamicContext:
    """Test cases for _build_dynamic_context method."""

    def test_build_dynamic_context_with_all_fields(self, builder, mock_prompt):
        """Test dynamic context rendering with all fields."""
        mock_prompt.file_references = [
            PromptFileReference(
                path="/test/file.py",
                content="test content",
            )
        ]
        mock_prompt.artifacts = [
            Artifact(
                path="/test/artifact.py",
                content="artifact content",
            )
        ]
        mock_prompt.todos = [
            PromptTodo(
                title="Test todo",
                description="Testing todo",
                checked=False,
            )
        ]
        mock_prompt.current_datetime = "2025-01-01T00:00:00Z"

        with patch(
            "pipe.core.domains.gemini_api_dynamic_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = '{"test": "rendered"}'
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            result = builder._build_dynamic_context(mock_prompt)

            assert isinstance(result, types.Content)
            assert result.role == "user"
            assert result.parts is not None
            assert len(result.parts) == 1
            assert result.parts[0].text == '{"test": "rendered"}'

            # Verify template was called with correct context
            render_call_args = mock_template.render.call_args
            context = render_call_args.kwargs["session"]
            assert context["file_references"] == mock_prompt.file_references
            assert context["artifacts"] == mock_prompt.artifacts
            assert context["todos"] == mock_prompt.todos
            assert context["current_datetime"] == "2025-01-01T00:00:00Z"

    def test_build_dynamic_context_returns_none_for_empty_template(
        self, builder, mock_prompt
    ):
        """Test that empty rendered template returns None."""
        mock_prompt.file_references = None
        mock_prompt.artifacts = None
        mock_prompt.todos = None
        mock_prompt.current_datetime = "2025-01-01T00:00:00Z"

        with patch(
            "pipe.core.domains.gemini_api_dynamic_payload.Environment"
        ) as mock_env_class:
            mock_env = MagicMock()
            mock_template = MagicMock()
            mock_template.render.return_value = "   \n  "  # Whitespace only
            mock_env.get_template.return_value = mock_template
            mock_env_class.return_value = mock_env

            result = builder._build_dynamic_context(mock_prompt)

            assert result is None


class TestBuildBufferedHistory:
    """Test cases for _build_buffered_history method."""

    def test_build_buffered_history_with_user_turns(self, builder):
        """Test buffered history with user turns only."""
        history = [
            UserTaskTurn(
                type="user_task",
                instruction="First task",
                timestamp="2025-01-01T00:00:01Z",
            ),
            UserTaskTurn(
                type="user_task",
                instruction="Second task",
                timestamp="2025-01-01T00:00:02Z",
            ),
        ]

        result = builder._build_buffered_history(history)

        assert len(result) == 2
        assert all(isinstance(c, types.Content) for c in result)
        assert all(c.role == "user" for c in result)
        assert result[0].parts is not None
        assert result[0].parts[0].text == "First task"
        assert result[1].parts is not None
        assert result[1].parts[0].text == "Second task"

    def test_build_buffered_history_with_model_response_fallback(self, builder):
        """Test model response without raw_response uses fallback."""
        history = [
            ModelResponseTurn(
                type="model_response",
                content="Model response text",
                timestamp="2025-01-01T00:00:01Z",
                raw_response=None,
            )
        ]

        result = builder._build_buffered_history(history)

        assert len(result) == 1
        assert result[0].role == "model"
        assert result[0].parts is not None
        assert len(result[0].parts) == 1
        assert result[0].parts[0].text == "Model response text"

    def test_build_buffered_history_with_thought_signature_restoration(self, builder):
        """Test model response with thought signature restoration."""
        raw_response = json.dumps(
            [
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {"text": "Regular text"},
                                    {"thought": True, "text": "Thinking process"},
                                ],
                                "role": "model",
                            }
                        }
                    ]
                }
            ]
        )

        history = [
            ModelResponseTurn(
                type="model_response",
                content="Fallback content",
                timestamp="2025-01-01T00:00:01Z",
                raw_response=raw_response,
            )
        ]

        result = builder._build_buffered_history(history)

        assert len(result) == 1
        assert result[0].role == "model"
        assert result[0].parts is not None
        assert len(result[0].parts) == 2
        assert result[0].parts[0].text == "Regular text"
        assert result[0].parts[1].thought is True
        assert result[0].parts[1].text == "Thinking process"

    def test_build_buffered_history_mixed_turns(self, builder):
        """Test buffered history with mixed turn types."""
        history = [
            UserTaskTurn(
                type="user_task",
                instruction="User task",
                timestamp="2025-01-01T00:00:01Z",
            ),
            ModelResponseTurn(
                type="model_response",
                content="Model response",
                timestamp="2025-01-01T00:00:02Z",
                raw_response=None,
            ),
        ]

        result = builder._build_buffered_history(history)

        assert len(result) == 2
        assert result[0].role == "user"
        assert result[0].parts is not None
        assert result[0].parts[0].text == "User task"
        assert result[1].role == "model"
        assert result[1].parts is not None
        assert result[1].parts[0].text == "Model response"

    def test_build_buffered_history_with_function_calling_turn(self, builder):
        """Test buffered history with function calling turn."""
        raw_response = json.dumps(
            [
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "function_call": {
                                            "name": "test_function",
                                            "args": {"param": "value"},
                                        }
                                    }
                                ],
                                "role": "model",
                            }
                        }
                    ]
                }
            ]
        )

        history = [
            FunctionCallingTurn(
                type="function_calling",
                response="Function response",
                timestamp="2025-01-01T00:00:01Z",
                raw_response=raw_response,
            )
        ]

        result = builder._build_buffered_history(history)

        assert len(result) == 1
        assert result[0].role == "model"
        assert result[0].parts is not None
        assert len(result[0].parts) == 1
        assert hasattr(result[0].parts[0], "function_call")
        assert result[0].parts[0].function_call.name == "test_function"
        assert result[0].parts[0].function_call.args == {"param": "value"}


class TestRestoreThoughtSignature:
    """Test cases for _restore_thought_signature method."""

    def test_restore_returns_none_for_no_raw_response(self, builder):
        """Test that restoration returns None when raw_response is absent."""
        turn = ModelResponseTurn(
            type="model_response",
            content="Content",
            timestamp="2025-01-01T00:00:01Z",
            raw_response=None,
        )

        result = builder._restore_thought_signature(turn)

        assert result is None

    def test_restore_returns_none_for_invalid_json(self, builder):
        """Test that restoration returns None for invalid JSON."""
        turn = ModelResponseTurn(
            type="model_response",
            content="Content",
            timestamp="2025-01-01T00:00:01Z",
            raw_response="invalid json {",
        )

        result = builder._restore_thought_signature(turn)

        assert result is None

    def test_restore_simple_text_parts(self, builder):
        """Test restoration of simple text parts."""
        raw_response = json.dumps(
            [
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [{"text": "Simple text"}],
                                "role": "model",
                            }
                        }
                    ]
                }
            ]
        )

        turn = ModelResponseTurn(
            type="model_response",
            content="Fallback",
            timestamp="2025-01-01T00:00:01Z",
            raw_response=raw_response,
        )

        result = builder._restore_thought_signature(turn)

        assert result is not None
        assert result.role == "model"
        assert result.parts is not None
        assert len(result.parts) == 1
        assert result.parts[0].text == "Simple text"

    def test_restore_thought_parts(self, builder):
        """Test restoration of thought=True parts."""
        raw_response = json.dumps(
            [
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {"thought": True, "text": "Thinking..."},
                                ],
                                "role": "model",
                            }
                        }
                    ]
                }
            ]
        )

        turn = ModelResponseTurn(
            type="model_response",
            content="Fallback",
            timestamp="2025-01-01T00:00:01Z",
            raw_response=raw_response,
        )

        result = builder._restore_thought_signature(turn)

        assert result is not None
        assert result.parts is not None
        assert len(result.parts) == 1
        assert result.parts[0].thought is True
        assert result.parts[0].text == "Thinking..."

    def test_restore_with_thought_signature_chunks(self, builder):
        """Test restoration with thought_signature chunks."""
        raw_response = json.dumps(
            [
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "thought_signature": {
                                            "chunks": [
                                                {"thought": "Thinking step 1"},
                                                {"text": "Output step 1"},
                                                {"thought": "Thinking step 2"},
                                                {"text": "Output step 2"},
                                            ]
                                        }
                                    }
                                ],
                                "role": "model",
                            }
                        }
                    ]
                }
            ]
        )

        turn = ModelResponseTurn(
            type="model_response",
            content="Fallback",
            timestamp="2025-01-01T00:00:01Z",
            raw_response=raw_response,
        )

        result = builder._restore_thought_signature(turn)

        assert result is not None
        assert result.parts is not None
        assert len(result.parts) == 4
        assert result.parts[0].thought is True
        assert result.parts[0].text == "Thinking step 1"
        assert result.parts[1].text == "Output step 1"
        assert result.parts[2].thought is True
        assert result.parts[2].text == "Thinking step 2"
        assert result.parts[3].text == "Output step 2"


class TestReconstructParts:
    """Test cases for _reconstruct_parts method."""

    def test_reconstruct_empty_parts(self, builder):
        """Test reconstruction with empty parts list."""
        result = builder._reconstruct_parts([])

        assert isinstance(result, list)
        assert len(result) == 0

    def test_reconstruct_text_part(self, builder):
        """Test reconstruction of simple text part."""
        parts_data = [{"text": "Hello world"}]

        result = builder._reconstruct_parts(parts_data)

        assert len(result) == 1
        assert result[0].text == "Hello world"

    def test_reconstruct_thought_part(self, builder):
        """Test reconstruction of thought part."""
        parts_data = [{"thought": True, "text": "Thinking..."}]

        result = builder._reconstruct_parts(parts_data)

        assert len(result) == 1
        assert result[0].thought is True
        assert result[0].text == "Thinking..."

    def test_reconstruct_function_call_part(self, builder):
        """Test reconstruction of function call part."""
        parts_data = [
            {
                "function_call": {
                    "name": "my_function",
                    "args": {"arg1": "value1", "arg2": 42},
                }
            }
        ]

        result = builder._reconstruct_parts(parts_data)

        assert len(result) == 1
        assert hasattr(result[0], "function_call")
        assert result[0].function_call.name == "my_function"
        assert result[0].function_call.args == {"arg1": "value1", "arg2": 42}

    def test_reconstruct_thought_signature_chunks(self, builder):
        """Test reconstruction of thought_signature with chunks."""
        parts_data = [
            {
                "thought_signature": {
                    "chunks": [
                        {"thought": "First thought"},
                        {"text": "First output"},
                        {"thought": "Second thought"},
                        {"text": "Second output"},
                    ]
                }
            }
        ]

        result = builder._reconstruct_parts(parts_data)

        assert len(result) == 4
        assert result[0].thought is True
        assert result[0].text == "First thought"
        assert result[1].text == "First output"
        assert result[2].thought is True
        assert result[2].text == "Second thought"
        assert result[3].text == "Second output"

    def test_reconstruct_mixed_parts(self, builder):
        """Test reconstruction of mixed part types."""
        parts_data = [
            {"text": "Regular text"},
            {"thought": True, "text": "Thought process"},
            {
                "function_call": {
                    "name": "tool",
                    "args": {"x": 1},
                }
            },
        ]

        result = builder._reconstruct_parts(parts_data)

        assert len(result) == 3
        assert result[0].text == "Regular text"
        assert result[1].thought is True
        assert result[1].text == "Thought process"
        assert result[2].function_call.name == "tool"


class TestRestoreFunctionCall:
    """Test cases for _restore_function_call method."""

    def test_restore_function_call_returns_none_for_no_raw_response(self, builder):
        """Test that restoration returns None when raw_response is absent."""
        turn = FunctionCallingTurn(
            type="function_calling",
            response="Response",
            timestamp="2025-01-01T00:00:01Z",
            raw_response=None,
        )

        result = builder._restore_function_call(turn)

        assert result is None

    def test_restore_function_call_returns_none_for_invalid_json(self, builder):
        """Test that restoration returns None for invalid JSON."""
        turn = FunctionCallingTurn(
            type="function_calling",
            response="Response",
            timestamp="2025-01-01T00:00:01Z",
            raw_response="invalid json",
        )

        result = builder._restore_function_call(turn)

        assert result is None

    def test_restore_function_call_with_valid_data(self, builder):
        """Test restoration of function call with valid data."""
        raw_response = json.dumps(
            [
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "function_call": {
                                            "name": "search",
                                            "args": {"query": "test"},
                                        }
                                    }
                                ],
                                "role": "model",
                            }
                        }
                    ]
                }
            ]
        )

        turn = FunctionCallingTurn(
            type="function_calling",
            response="Response",
            timestamp="2025-01-01T00:00:01Z",
            raw_response=raw_response,
        )

        result = builder._restore_function_call(turn)

        assert result is not None
        assert result.role == "model"
        assert result.parts is not None
        assert len(result.parts) == 1
        assert result.parts[0].function_call.name == "search"
        assert result.parts[0].function_call.args == {"query": "test"}

    def test_restore_function_call_with_multiple_chunks(self, builder):
        """Test restoration uses the last chunk with valid content."""
        raw_response = json.dumps(
            [
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "function_call": {
                                            "name": "first",
                                            "args": {},
                                        }
                                    }
                                ],
                                "role": "model",
                            }
                        }
                    ]
                },
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "function_call": {
                                            "name": "second",
                                            "args": {"final": True},
                                        }
                                    }
                                ],
                                "role": "model",
                            }
                        }
                    ]
                },
            ]
        )

        turn = FunctionCallingTurn(
            type="function_calling",
            response="Response",
            timestamp="2025-01-01T00:00:01Z",
            raw_response=raw_response,
        )

        result = builder._restore_function_call(turn)

        assert result is not None
        assert result.parts is not None
        # Should use the last chunk
        assert result.parts[0].function_call.name == "second"
        assert result.parts[0].function_call.args == {"final": True}
