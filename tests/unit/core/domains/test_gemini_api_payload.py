import json
from unittest.mock import MagicMock, patch

import pytest
from google.genai import types
from pipe.core.domains.gemini_api_payload import GeminiApiPayloadBuilder
from pipe.core.models.gemini_api_payload import (
    GeminiApiDynamicPayload,
    GeminiApiStaticPayload,
)


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.parameters.temperature.value = 0.7
    settings.parameters.top_p.value = 0.9
    settings.parameters.top_k.value = 40
    settings.timezone = "UTC"
    return settings


@pytest.fixture
def builder(mock_settings):
    with (
        patch("pipe.core.domains.gemini_api_payload.ResourceRepository"),
        patch("pipe.core.domains.gemini_api_payload.PromptFactory"),
        patch("pipe.core.domains.gemini_api_payload.FileSystemLoader"),
        patch("pipe.core.domains.gemini_api_payload.Environment") as mock_env_class,
    ):
        # Setup mock environment to have a real filters dict
        mock_env_class.return_value.filters = {}
        return GeminiApiPayloadBuilder("/project/root", mock_settings)


class TestGeminiApiPayloadBuilder:
    def test_init(self, builder, mock_settings):
        assert builder.project_root == "/project/root"
        assert builder.settings == mock_settings
        assert builder.last_cached_turn_count is None

    def test_create_jinja_environment(self, builder):
        with (
            patch(
                "pipe.core.domains.gemini_api_payload.FileSystemLoader"
            ) as mock_loader,
            patch("pipe.core.domains.gemini_api_payload.Environment") as mock_env_class,
        ):
            mock_env = mock_env_class.return_value
            mock_env.filters = {}

            builder._create_jinja_environment()

            mock_loader.assert_called_once()
            mock_env_class.assert_called_once()
            assert "tojson" in mock_env.filters
            assert "pydantic_dump" in mock_env.filters

    def test_build_prompt_no_session(self, builder):
        session_service = MagicMock()
        session_service.current_session = None
        with pytest.raises(
            ValueError, match="Cannot build prompt without a current session"
        ):
            builder.build_prompt(session_service)

    def test_build_prompt_with_artifacts(self, builder):
        session_service = MagicMock()
        session = MagicMock()
        session.artifacts = ["file1.txt", "file2.txt"]
        session_service.current_session = session
        session_service.settings = builder.settings
        session_service.current_instruction = "test instruction"

        builder.resource_repository.exists.side_effect = [True, False]
        builder.resource_repository.read_text.return_value = "content1"

        with patch(
            "pipe.core.domains.gemini_api_payload.build_artifacts_from_data"
        ) as mock_build_artifacts:
            builder.build_prompt(session_service)

            mock_build_artifacts.assert_called_once_with(
                [("file1.txt", "content1"), ("file2.txt", None)]
            )
            builder.prompt_factory.create.assert_called_once()

    def test_render(self, builder):
        prompt_model = MagicMock()
        with (
            patch.object(builder, "_render_static_payload") as mock_static,
            patch.object(builder, "_render_dynamic_payload") as mock_dynamic,
        ):
            mock_static.return_value = "static_payload"
            mock_dynamic.return_value = "dynamic_payload"

            static, dynamic = builder.render(prompt_model)

            assert static == "static_payload"
            assert dynamic == "dynamic_payload"
            mock_static.assert_called_once_with(prompt_model)
            mock_dynamic.assert_called_once_with(prompt_model)

    def test_render_static_payload(self, builder):
        prompt_model = MagicMock()
        prompt_model.buffered_history = MagicMock()

        with (
            patch.object(builder, "_render_static_template") as mock_render_template,
            patch.object(builder, "_convert_buffered_history") as mock_convert_history,
        ):
            mock_render_template.return_value = "rendered_static"
            mock_convert_history.return_value = ["content1"]

            payload = builder._render_static_payload(prompt_model)

            assert isinstance(payload, GeminiApiStaticPayload)
            assert payload.cached_content == "rendered_static"
            assert payload.buffered_history == ["content1"]

    def test_render_dynamic_payload(self, builder):
        prompt_model = MagicMock()
        prompt_model.current_task = MagicMock()

        with (
            patch.object(builder, "_render_dynamic_template") as mock_render_template,
            patch.object(
                builder, "_convert_current_instruction"
            ) as mock_convert_instruction,
        ):
            mock_render_template.return_value = "rendered_dynamic"
            mock_convert_instruction.return_value = "converted_instruction"

            payload = builder._render_dynamic_payload(prompt_model)

            assert isinstance(payload, GeminiApiDynamicPayload)
            assert payload.dynamic_content == "rendered_dynamic"
            assert payload.current_instruction == "converted_instruction"

    def test_render_static_template_success(self, builder):
        prompt_model = MagicMock()
        prompt_model.model_dump.return_value = {"key": "value"}
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered"
        builder.jinja_env.get_template.return_value = mock_template

        result = builder._render_static_template(prompt_model)

        assert result == "rendered"
        builder.jinja_env.get_template.assert_called_with("gemini_static_prompt.j2")

    def test_render_static_template_fallback(self, builder):
        prompt_model = MagicMock()
        mock_template = MagicMock()
        mock_template.render.return_value = "fallback"
        builder.jinja_env.get_template.side_effect = [Exception("Error"), mock_template]

        result = builder._render_static_template(prompt_model)

        # The implementation returns "" on fallback for static template
        assert result == ""
        builder.jinja_env.get_template.assert_any_call("gemini_api_prompt.j2")

    def test_render_dynamic_template_success(self, builder):
        prompt_model = MagicMock()
        prompt_model.model_dump.return_value = {"key": "value"}
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered"
        builder.jinja_env.get_template.return_value = mock_template

        result = builder._render_dynamic_template(prompt_model)

        assert result == "rendered"
        builder.jinja_env.get_template.assert_called_with("gemini_dynamic_prompt.j2")

    def test_render_dynamic_template_fallback(self, builder):
        prompt_model = MagicMock()
        mock_template = MagicMock()
        mock_template.render.return_value = "fallback_rendered"
        builder.jinja_env.get_template.side_effect = [Exception("Error"), mock_template]

        result = builder._render_dynamic_template(prompt_model)

        assert result == "fallback_rendered"
        builder.jinja_env.get_template.assert_any_call("gemini_api_prompt.j2")

    def test_convert_buffered_history_empty(self, builder):
        assert builder._convert_buffered_history(None) == []
        assert builder._convert_buffered_history(MagicMock(turns=[])) == []

    def test_convert_buffered_history_with_turns(self, builder):
        history = MagicMock()
        turn1 = MagicMock()
        turn2 = MagicMock()
        history.turns = [turn1, turn2]

        with patch.object(builder, "convert_turn_to_content") as mock_convert:
            mock_convert.side_effect = ["content1", "content2"]
            result = builder._convert_buffered_history(history)
            assert result == ["content1", "content2"]

    def test_convert_current_instruction_empty(self, builder):
        assert builder._convert_current_instruction(None) is None
        assert builder._convert_current_instruction(MagicMock(instruction="  ")) is None

    def test_convert_current_instruction_valid(self, builder):
        task = MagicMock(instruction="do something")
        result = builder._convert_current_instruction(task)
        assert isinstance(result, types.Content)
        assert result.role == "user"
        assert result.parts is not None
        assert result.parts[0].text == "do something"

    def test_build_payloads_with_tools(self, builder):
        session_service = MagicMock()
        loaded_tools = [{"name": "tool1"}]
        prompt_model = MagicMock()
        prompt_model.cached_history.turns = [1, 2, 3]

        with (
            patch.object(builder, "build_prompt") as mock_build_prompt,
            patch.object(builder, "render") as mock_render,
            patch.object(builder, "convert_tools") as mock_convert_tools,
        ):
            mock_build_prompt.return_value = prompt_model
            mock_render.return_value = ("static", "dynamic")
            mock_convert_tools.return_value = ["tool_obj"]

            static, dynamic, tools = builder.build_payloads_with_tools(
                session_service, loaded_tools
            )

            assert static == "static"
            assert dynamic == "dynamic"
            assert tools == ["tool_obj"]
            assert builder.last_cached_turn_count == 3

    def test_build_payloads_with_tools_no_cached_history(self, builder):
        session_service = MagicMock()
        prompt_model = MagicMock()
        prompt_model.cached_history = None

        with (
            patch.object(builder, "build_prompt") as mock_build_prompt,
            patch.object(builder, "render") as mock_render,
        ):
            mock_build_prompt.return_value = prompt_model
            mock_render.return_value = ("static", "dynamic")

            builder.build_payloads_with_tools(session_service, [])
            assert builder.last_cached_turn_count == 0

    def test_convert_tools(self, builder):
        tools_data = [
            {
                "name": "get_weather",
                "description": "Get weather",
                "parameters": {"type": types.Type.OBJECT},
            }
        ]
        result = builder.convert_tools(tools_data)

        assert len(result) == 1
        assert isinstance(result[0], types.Tool)
        assert result[0].function_declarations is not None
        assert result[0].function_declarations[0].name == "get_weather"
        assert result[0].function_declarations[0].description == "Get weather"

    def test_build_generation_config_default(self, builder):
        session_data = MagicMock()
        session_data.hyperparameters = None
        # Use a real Tool object to avoid Pydantic validation error
        tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="t", parameters=types.Schema(type=types.Type.OBJECT)
                    )
                ]
            )
        ]

        config = builder.build_generation_config(session_data, None, tools)

        assert config.temperature == 0.7
        assert config.top_p == 0.9
        assert config.top_k == 40
        assert config.tools == tools
        assert config.cached_content is None

    def test_build_generation_config_session_override(self, builder):
        session_data = MagicMock()
        session_data.hyperparameters.temperature = 0.5
        session_data.hyperparameters.top_p = 0.8
        session_data.hyperparameters.top_k = 20
        tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="t", parameters=types.Schema(type=types.Type.OBJECT)
                    )
                ]
            )
        ]

        config = builder.build_generation_config(session_data, "cache_name", tools)

        assert config.temperature == 0.5
        assert config.top_p == 0.8
        assert config.top_k == 20
        assert (
            config.tools is None
        )  # tools should be None if cached_content is provided
        assert config.cached_content == "cache_name"

    def test_convert_turn_to_content_user_task(self, builder):
        turn = MagicMock()
        turn.type = "user_task"
        turn.instruction = "hello"

        result = builder.convert_turn_to_content(turn)

        assert result.role == "user"
        assert result.parts is not None
        assert result.parts[0].text == "hello"

    def test_convert_turn_to_content_model_response_no_signature(self, builder):
        turn = MagicMock()
        turn.type = "model_response"
        turn.content = "response content"
        turn.raw_response = None

        result = builder.convert_turn_to_content(turn)

        assert result.role == "model"
        assert result.parts is not None
        assert result.parts[0].text == "response content"

    def test_convert_turn_to_content_model_response_with_signature(self, builder):
        turn = MagicMock()
        turn.type = "model_response"
        turn.content = "response content"
        turn.raw_response = '{"dummy": "json"}'

        with patch.object(builder, "_restore_thought_signature") as mock_restore:
            mock_restore.return_value = types.Content(
                role="model", parts=[types.Part(text="restored")]
            )
            result = builder.convert_turn_to_content(turn)
            assert result.parts is not None
            assert result.parts[0].text == "restored"

    def test_convert_turn_to_content_function_calling(self, builder):
        turn = MagicMock()
        turn.type = "function_calling"
        turn.response = "call_info"
        turn.raw_response = None

        result = builder.convert_turn_to_content(turn)

        assert result.role == "model"
        assert result.parts is not None
        assert result.parts[0].text == "Function Call: call_info"

    def test_convert_turn_to_content_tool_response(self, builder):
        turn = MagicMock()
        turn.type = "tool_response"
        turn.name = "my_tool"
        turn.response = "tool_output"

        result = builder.convert_turn_to_content(turn)

        assert result.role == "user"
        assert result.parts is not None
        assert result.parts[0].text == "Tool Response (my_tool): tool_output"

    def test_restore_thought_signature_list_format(self, builder):
        raw_json = json.dumps(
            [
                {"candidates": [{"content": {"parts": [{"text": "chunk1"}]}}]},
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {"text": "chunk2", "thought_signature": "sig"}
                                ]
                            }
                        }
                    ]
                },
            ]
        )

        # We need to mock types.GenerateContentResponse.model_validate
        with patch(
            "google.genai.types.GenerateContentResponse.model_validate"
        ) as mock_validate:
            resp1 = MagicMock()
            resp1.candidates = [
                MagicMock(content=MagicMock(parts=[MagicMock(thought_signature=None)]))
            ]

            resp2 = MagicMock()
            part2 = MagicMock()
            part2.thought_signature = "sig"
            resp2.candidates = [MagicMock(content=MagicMock(parts=[part2]))]

            mock_validate.side_effect = [resp2, resp1]  # reversed order in code

            result = builder._restore_thought_signature(raw_json)
            assert result == resp2.candidates[0].content

    def test_restore_thought_signature_dict_format(self, builder):
        raw_json = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "content"}]}}]}
        )

        with patch(
            "google.genai.types.GenerateContentResponse.model_validate"
        ) as mock_validate:
            resp = MagicMock()
            resp.candidates = [MagicMock(content="content_obj")]
            mock_validate.return_value = resp

            result = builder._restore_thought_signature(raw_json)
            assert result == "content_obj"

    def test_restore_thought_signature_invalid_json(self, builder):
        assert builder._restore_thought_signature("invalid json") is None

    def test_restore_thought_signature_exception(self, builder):
        with patch("json.loads", side_effect=Exception("Error")):
            assert builder._restore_thought_signature("{}") is None
