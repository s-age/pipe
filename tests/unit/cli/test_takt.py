import unittest
from unittest.mock import MagicMock, patch

from pipe.cli.takt import main
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings


class TestTaktMain(unittest.TestCase):
    @patch("pipe.cli.takt.check_and_show_warning", return_value=True)
    @patch("pipe.cli.takt.load_dotenv")
    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    @patch("pipe.cli.takt._parse_arguments")
    @patch("pipe.cli.takt.dispatch")
    def test_main_flow_with_api_mode_override(
        self,
        mock_dispatch,
        mock_parse_arguments,
        mock_get_settings,
        mock_load_dotenv,
        mock_check_warning,
    ):
        """
        Tests that the main function correctly parses args, loads settings,
        overrides api_mode, and calls dispatch.
        """
        # Mock the parsed arguments
        mock_args = MagicMock()
        mock_args.api_mode = "gemini-cli"
        mock_args.session = None
        mock_args.instruction = "test"
        mock_args.purpose = "test purpose"
        mock_args.background = "test background"
        mock_parser = MagicMock()
        mock_parse_arguments.return_value = (mock_args, mock_parser)

        # Mock settings
        mock_get_settings.return_value = Settings(
            model="default-model",
            api_mode="gemini-api",  # This should be overridden
            timezone="UTC",
            parameters={
                "temperature": {"value": 0.5, "description": "temp"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        )

        # Run the main function
        main()

        # Assertions
        mock_check_warning.assert_called_once()
        mock_load_dotenv.assert_called_once()
        mock_get_settings.assert_called_once()
        mock_parse_arguments.assert_called_once()
        mock_dispatch.assert_called_once()

        # Check that dispatch was called with the correct arguments
        dispatch_args, dispatch_kwargs = mock_dispatch.call_args
        dispatched_takt_args: TaktArgs = dispatch_args[0]
        dispatched_session_service = dispatch_args[1]

        self.assertEqual(dispatched_takt_args.api_mode, "gemini-cli")
        self.assertEqual(dispatched_session_service.settings.api_mode, "gemini-cli")

    @patch("pipe.cli.takt.check_and_show_warning", return_value=True)
    @patch("pipe.cli.takt.load_dotenv")
    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    @patch("pipe.cli.takt._parse_arguments")
    @patch("pipe.cli.takt.dispatch")
    def test_main_flow_with_artifacts_and_procedure(
        self,
        mock_dispatch,
        mock_parse_arguments,
        mock_get_settings,
        mock_load_dotenv,
        mock_check_warning,
    ):
        """
        Tests that the main function correctly parses artifacts and procedure arguments.
        """
        # Mock the parsed arguments
        mock_args = MagicMock()
        mock_args.api_mode = None
        mock_args.session = None
        mock_args.instruction = "test"
        mock_args.purpose = "test purpose"
        mock_args.background = "test background"
        mock_args.artifacts = "file1.txt,file2.json"
        mock_args.procedure = "guide.md"
        mock_parser = MagicMock()
        mock_parse_arguments.return_value = (mock_args, mock_parser)

        # Mock settings
        mock_get_settings.return_value = Settings(
            model="default-model",
            api_mode="gemini-api",
            timezone="UTC",
            parameters={
                "temperature": {"value": 0.5, "description": "temp"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        )

        # Run the main function
        main()

        # Assertions
        mock_check_warning.assert_called_once()
        mock_load_dotenv.assert_called_once()
        mock_get_settings.assert_called_once()
        mock_parse_arguments.assert_called_once()
        mock_dispatch.assert_called_once()

        # Check that dispatch was called with the correct arguments
        dispatch_args, dispatch_kwargs = mock_dispatch.call_args
        dispatched_takt_args: TaktArgs = dispatch_args[0]

        self.assertEqual(dispatched_takt_args.artifacts, ["file1.txt", "file2.json"])
        self.assertEqual(dispatched_takt_args.procedure, "guide.md")


if __name__ == "__main__":
    unittest.main()
