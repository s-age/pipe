import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.delegates import gemini_api_delegate
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings
from pipe.core.models.turn import UserTaskTurn
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService

# We avoid importing specific response types to make the test more robust
# against library changes. MagicMock will create the structure we need.


class TestGeminiApiDelegate(unittest.TestCase):
    def setUp(self):
        # Use the real project root to find templates, but a temporary dir for sessions
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        self.temp_sessions_dir = tempfile.mkdtemp()

        settings_data = {
            "model": "test-model",
            "search_model": "test-model",
            "context_limit": 10000,
            "api_mode": "gemini-api",
            "language": "en",
            "yolo": False,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)

        # Instantiate services with the real project root
        self.session_service = SessionService(
            project_root=self.project_root, settings=self.settings
        )
        self.prompt_service = PromptService(project_root=self.project_root)

        # Override session paths to use the temporary directory
        self.session_service.sessions_dir = self.temp_sessions_dir
        self.session_service.index_path = os.path.join(
            self.temp_sessions_dir, "index.json"
        )

        # Patch the token counter to avoid real API calls during setup/run
        self.token_service_patcher = patch("pipe.core.agents.gemini_api.TokenService")
        self.mock_token_service_class = self.token_service_patcher.start()
        self.mock_token_service_instance = self.mock_token_service_class.return_value
        self.mock_token_service_instance.count_tokens.return_value = 0
        self.mock_token_service_instance.check_limit.return_value = (True, "OK")
        self.mock_token_service_instance.model_name = (
            "test-model"  # Set a concrete string value
        )

    def tearDown(self):
        self.token_service_patcher.stop()
        shutil.rmtree(self.temp_sessions_dir)

    def test_run_with_simple_text_response(self):
        """Tests the delegate's behavior with a simple text response from the API."""
        with (
            patch(
                "pipe.core.delegates.gemini_api_delegate.call_gemini_api"
            ) as mock_call_api,
            patch(
                "pipe.core.delegates.gemini_api_delegate.execute_tool_call"
            ) as mock_execute_tool,
        ):
            # 1. Setup: Mock the API to return a simple text stream
            mock_part = MagicMock()
            mock_part.text = "Hello, world!"
            # Configure the mock to explicitly not have a function_call attribute
            del mock_part.function_call

            mock_response = MagicMock()
            mock_response.candidates = [MagicMock()]
            mock_response.candidates[0].content.parts = [mock_part]
            mock_response.usage_metadata.prompt_token_count = 10
            mock_response.usage_metadata.candidates_token_count = 5
            mock_call_api.return_value = iter([mock_response])  # Return an iterator

            # 2. Prepare session
            args = TaktArgs(instruction="Say hello", purpose="Test", background="Test")
            self.session_service.prepare_session_for_takt(args)

            # 3. Run the delegate
            _, token_count, turns_to_save = gemini_api_delegate.run(
                args, self.session_service, self.prompt_service
            )

            # 4. Assertions
            mock_call_api.assert_called_once()
            self.assertEqual(token_count, 15)
            self.assertEqual(len(turns_to_save), 1)
            self.assertEqual(turns_to_save[0].type, "model_response")
            self.assertEqual(turns_to_save[0].content, "Hello, world!")
            mock_execute_tool.assert_not_called()

    def test_run_with_function_call_flow(self):
        """Tests the full flow of a function call and subsequent text response."""
        with (
            patch(
                "pipe.core.delegates.gemini_api_delegate.call_gemini_api"
            ) as mock_call_api,
            patch(
                "pipe.core.delegates.gemini_api_delegate.execute_tool_call"
            ) as mock_execute_tool,
        ):
            # 1. Setup: Mock the API to return a function call, then a text response
            func_call = MagicMock()
            func_call.name = "test_tool"
            func_call.args = {"arg1": "value1"}

            mock_part_1 = MagicMock()
            mock_part_1.function_call = func_call
            mock_part_1.text = None
            mock_response_1 = MagicMock()
            mock_response_1.candidates = [MagicMock()]
            mock_response_1.candidates[0].content.parts = [mock_part_1]
            mock_response_1.usage_metadata.prompt_token_count = 20
            mock_response_1.usage_metadata.candidates_token_count = 10

            mock_part_2 = MagicMock()
            mock_part_2.text = "Tool executed successfully."
            mock_part_2.function_call = None
            mock_response_2 = MagicMock()
            mock_response_2.candidates = [MagicMock()]
            mock_response_2.candidates[0].content.parts = [mock_part_2]
            mock_response_2.usage_metadata.prompt_token_count = 40
            mock_response_2.usage_metadata.candidates_token_count = 8

            mock_call_api.side_effect = [
                iter([mock_response_1]),
                iter([mock_response_2]),
            ]

            mock_execute_tool.return_value = {
                "status": "succeeded",
                "message": "Tool output",
            }

            # 2. Prepare session
            args = TaktArgs(
                instruction="Use the test tool", purpose="Test", background="Test"
            )
            self.session_service.prepare_session_for_takt(args)

            # 3. Run the delegate
            _, token_count, turns_to_save = gemini_api_delegate.run(
                args, self.session_service, self.prompt_service
            )

            # 4. Assertions
            self.assertEqual(mock_call_api.call_count, 2)
            mock_execute_tool.assert_called_once()
            self.assertEqual(token_count, 48)

            self.assertEqual(len(turns_to_save), 3)
            self.assertEqual(turns_to_save[0].type, "function_calling")
            self.assertEqual(turns_to_save[1].type, "tool_response")
            self.assertEqual(turns_to_save[2].type, "model_response")
            self.assertEqual(turns_to_save[2].content, "Tool executed successfully.")

    def test_run_merges_pool_into_turns(self):
        """Tests that the delegate merges the turn pool before calling the API."""
        with (
            patch(
                "pipe.core.delegates.gemini_api_delegate.call_gemini_api"
            ) as mock_call_api,
            patch.object(
                self.session_service, "merge_pool_into_turns"
            ) as mock_merge_pool,
        ):
            # 1. Setup: Mock the API to return a simple text stream to exit the loop
            mock_part = MagicMock()
            mock_part.text = "Final response."
            delattr(mock_part, "function_call")  # Ensure no function call

            mock_response = MagicMock()
            mock_response.candidates = [MagicMock()]
            mock_response.candidates[0].content.parts = [mock_part]
            mock_response.usage_metadata.prompt_token_count = 10
            mock_response.usage_metadata.candidates_token_count = 5
            mock_call_api.return_value = iter([mock_response])

            # 2. Prepare session with items in the pool
            args = TaktArgs(
                instruction="Test pool merge", purpose="Test", background="Test"
            )
            self.session_service.prepare_session_for_takt(args)

            # Add a dummy turn to the pool
            dummy_turn_in_pool = UserTaskTurn(
                type="user_task",
                instruction="This was in the pool",
                timestamp="dummy_timestamp",
            )
            self.session_service.current_session.pools.append(dummy_turn_in_pool)

            # 3. Run the delegate
            gemini_api_delegate.run(args, self.session_service, self.prompt_service)

            # 4. Assertions
            # Verify that merge_pool_into_turns was called before the API call
            mock_merge_pool.assert_called_once_with(
                self.session_service.current_session_id
            )

            # Verify the API was called after the merge attempt
            mock_call_api.assert_called_once()


if __name__ == "__main__":
    unittest.main()
