from pipe.core.prompt_builder import PromptBuilder

import unittest
import os
import json
from unittest.mock import patch, mock_open
from pipe.core.prompt_builder import PromptBuilder

class TestPromptBuilder(unittest.TestCase):

    def setUp(self):
        self.project_root = os.getcwd() # Use current working directory for testing
        self.settings = {
            "parameters": {
                "temperature": {"value": 0.5},
                "top_p": {"value": 0.9},
                "top_k": {"value": 40}
            },
            "constraints": {
                "description": "Test Constraints",
                "processing_config": {"description": "Test Processing Config"}
            },
            "language": "English"
        }
        self.session_data = {
            "purpose": "Test Purpose",
            "background": "Test Background",
            "roles": ["roles/engineer.md"],
            "references": [
                {"path": "articles/test_article.md", "disabled": False}
            ],
            "turns": [
                {"type": "user_task", "instruction": "Initial instruction."},
                {"type": "model_response", "content": "Model response."}
            ],
            "todos": ["Task 1", "Task 2"]
        }
        self.api_mode = "gemini-api"
        self.multi_step_reasoning_enabled = True

    @patch('builtins.open', new_callable=mock_open, read_data="Role content.")
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.exists', return_value=True)
    @patch('os.path.relpath', side_effect=lambda path, start: path.replace(start + os.sep, ''))
    def test_build_prompt_gemini_api(self, mock_relpath, mock_exists, mock_isfile, mock_file_open):
        """Test the prompt construction for gemini-api mode."""
        builder = PromptBuilder(
            settings=self.settings,
            session_data=self.session_data,
            project_root=self.project_root,
            api_mode=self.api_mode,
            multi_step_reasoning_enabled=self.multi_step_reasoning_enabled
        )
        
        # Mock the template loading and rendering
        with patch.object(builder.template_env, 'get_template') as mock_get_template:
            mock_template = mock_get_template.return_value
            mock_template.render.return_value = json.dumps({
                "session": {
                    "session_goal": {"purpose": "Test Purpose", "background": "Test Background"},
                    "roles": {"definitions": ["Role content."]},
                    "file_references": [{"path": "articles/test_article.md", "content": "Article content."}]
                }
            })

            prompt = builder.build()
            parsed_prompt = json.loads(prompt)

            self.assertIn("Test Purpose", parsed_prompt['session']['session_goal']['purpose'])
            self.assertIn("Test Background", parsed_prompt['session']['session_goal']['background'])
            self.assertIn("Role content.", parsed_prompt['session']['roles']['definitions'][0])
            self.assertIn("articles/test_article.md", parsed_prompt['session']['file_references'][0]['path'])

    @patch('builtins.open', new_callable=mock_open, read_data="Role content.")
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.exists', return_value=True)
    @patch('os.path.relpath', side_effect=lambda path, start: path.replace(start + os.sep, ''))
    def test_build_prompt_gemini_cli(self, mock_relpath, mock_exists, mock_isfile, mock_file_open):
        """Test the prompt construction for gemini-cli mode."""
        self.api_mode = "gemini-cli"
        builder = PromptBuilder(
            settings=self.settings,
            session_data=self.session_data,
            project_root=self.project_root,
            api_mode=self.api_mode,
            multi_step_reasoning_enabled=self.multi_step_reasoning_enabled
        )

        with patch.object(builder.template_env, 'get_template') as mock_get_template:
            mock_template = mock_get_template.return_value
            mock_template.render.return_value = json.dumps({
                "session": {
                    "session_goal": {"purpose": "Test Purpose", "background": "Test Background"},
                    "roles": {"definitions": ["Role content."]},
                    "file_references": [{"path": "articles/test_article.md", "content": "Article content."}]
                }
            })

            prompt = builder.build()
            parsed_prompt = json.loads(prompt)

            self.assertIn("Test Purpose", parsed_prompt['session']['session_goal']['purpose'])
            self.assertIn("Test Background", parsed_prompt['session']['session_goal']['background'])
            self.assertIn("Role content.", parsed_prompt['session']['roles']['definitions'][0])
            self.assertIn("articles/test_article.md", parsed_prompt['session']['file_references'][0]['path'])

    def test_unknown_api_mode(self):
        """Test that an unknown api_mode raises a ValueError."""
        with self.assertRaises(ValueError):
            PromptBuilder(
                settings=self.settings,
                session_data=self.session_data,
                project_root=self.project_root,
                api_mode="unknown-mode",
                multi_step_reasoning_enabled=self.multi_step_reasoning_enabled
            ).build()
