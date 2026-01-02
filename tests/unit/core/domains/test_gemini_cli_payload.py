import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from jinja2 import Environment, FileSystemLoader
from pipe.core.domains.gemini_cli_payload import GeminiCliPayloadBuilder
from pipe.core.models.prompt import Prompt
from pipe.core.services.session_service import SessionService


class TestGeminiCliPayloadBuilder:
    """Tests for GeminiCliPayloadBuilder."""

    @pytest.fixture
    def mock_project_root(self, tmp_path):
        """Create a temporary project root with templates."""
        template_dir = tmp_path / "templates" / "prompt"
        template_dir.mkdir(parents=True)
        # Create real template files for testing
        (template_dir / "gemini_cli_prompt.j2").write_text(
            '{"instruction": "{{ prompt.main_instruction | pydantic_dump }}"}'
        )
        (template_dir / "gemini_api_prompt.j2").write_text(
            '{"instruction": "{{ prompt.main_instruction | pydantic_dump }}"}'
        )
        return str(tmp_path)

    @pytest.fixture
    def builder(self, mock_project_root):
        """Create a GeminiCliPayloadBuilder instance."""
        return GeminiCliPayloadBuilder(project_root=mock_project_root)

    @pytest.fixture
    def mock_prompt_model(self):
        """Create a mock Prompt model."""
        mock_prompt = MagicMock(spec=Prompt)
        mock_prompt.main_instruction = "Test instruction"
        mock_prompt.model_dump.return_value = {"main_instruction": "Test instruction"}
        return mock_prompt

    @pytest.fixture
    def mock_session_service(self):
        """Create a mock SessionService instance."""
        return MagicMock(spec=SessionService)

    @patch(
        "pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder._create_jinja_environment"
    )
    def test_init(self, mock_create_jinja_environment, mock_project_root):
        """Test initialization of GeminiCliPayloadBuilder."""
        builder = GeminiCliPayloadBuilder(
            project_root=mock_project_root, api_mode="gemini-api"
        )

        mock_create_jinja_environment.assert_called_once()
        assert builder.project_root == mock_project_root
        assert builder.api_mode == "gemini-api"
        assert builder.jinja_env == mock_create_jinja_environment.return_value

    def test_create_jinja_environment(self, mock_project_root):
        """Test the creation and configuration of the Jinja2 environment."""
        builder = GeminiCliPayloadBuilder(project_root=mock_project_root)
        env = builder._create_jinja_environment()

        assert isinstance(env, Environment)
        assert isinstance(env.loader, FileSystemLoader)
        assert env.loader.searchpath == [
            str(Path(mock_project_root) / "templates" / "prompt")
        ]
        assert "tojson" in env.filters
        assert "pydantic_dump" in env.filters

        # Test tojson filter
        assert env.filters["tojson"]({"key": "value"}) == '{"key": "value"}'
        assert env.filters["tojson"]({"key": "値"}) == '{"key": "値"}'

        # Test pydantic_dump filter
        mock_obj = MagicMock()
        mock_obj.model_dump.return_value = {"test": "data"}
        assert env.filters["pydantic_dump"](mock_obj) == {"test": "data"}
        assert env.filters["pydantic_dump"]("simple_string") == "simple_string"

    @patch("pipe.core.domains.gemini_cli_payload.json.dumps")
    @patch("pipe.core.domains.gemini_cli_payload.json.loads")
    def test_render_gemini_cli_mode(
        self, mock_json_loads, mock_json_dumps, builder, mock_prompt_model
    ):
        """Test render method in gemini-cli mode."""
        builder.api_mode = "gemini-cli"
        mock_json_loads.return_value = {"instruction": "Test instruction"}
        mock_json_dumps.return_value = '{\n  "instruction": "Test instruction"\n}'

        result = builder.render(mock_prompt_model)

        mock_json_loads.assert_called_once()
        mock_json_dumps.assert_called_once()
        assert result == '{\n  "instruction": "Test instruction"\n}'.replace("@", "\\@")

    @patch("pipe.core.domains.gemini_cli_payload.json.dumps")
    @patch("pipe.core.domains.gemini_cli_payload.json.loads")
    def test_render_gemini_api_mode(
        self, mock_json_loads, mock_json_dumps, builder, mock_prompt_model
    ):
        """Test render method in gemini-api mode."""
        builder.api_mode = "gemini-api"
        mock_json_loads.return_value = {"instruction": "Test instruction"}
        mock_json_dumps.return_value = '{\n  "instruction": "Test instruction"\n}'

        result = builder.render(mock_prompt_model)

        mock_json_loads.assert_called_once()
        mock_json_dumps.assert_called_once()
        assert result == '{\n  "instruction": "Test instruction"\n}'.replace("@", "\\@")

    @patch(
        "pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder.build_prompt_model"
    )
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder.render")
    def test_build(
        self,
        mock_render,
        mock_build_prompt_model,
        builder,
        mock_session_service,
        mock_prompt_model,
    ):
        """Test the build method."""
        mock_build_prompt_model.return_value = mock_prompt_model
        mock_render.return_value = '{"instruction": "Test instruction"}'

        result = builder.build(mock_session_service)

        mock_build_prompt_model.assert_called_once_with(mock_session_service)
        mock_render.assert_called_once_with(mock_prompt_model)
        assert result == '{"instruction": "Test instruction"}'

    def test_render_with_at_symbol_escaping(self, mock_project_root, mock_prompt_model):
        """Test that the @ symbol is correctly escaped in the rendered output."""
        builder = GeminiCliPayloadBuilder(project_root=mock_project_root)
        builder.api_mode = "gemini-cli"
        mock_prompt_model.main_instruction = "Instruction with @symbol"

        # Manually render to verify the escaping logic
        template_path = Path(mock_project_root) / "templates" / "prompt"
        loader = FileSystemLoader(template_path)
        env = Environment(loader=loader, autoescape=False)

        def tojson_filter(value):
            return json.dumps(value, ensure_ascii=False)

        env.filters["tojson"] = tojson_filter

        def pydantic_dump(obj):
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json", exclude_none=True)
            return obj

        env.filters["pydantic_dump"] = pydantic_dump

        template = env.get_template("gemini_cli_prompt.j2")
        rendered_prompt = template.render(prompt=mock_prompt_model)
        json_output = json.dumps(
            json.loads(rendered_prompt), indent=2, ensure_ascii=False
        )
        expected_output = json_output.replace("@", "\\@")

        result = builder.render(mock_prompt_model)
        assert result == expected_output
