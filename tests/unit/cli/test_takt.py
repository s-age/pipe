"""Unit tests for the takt CLI entry point."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from pipe.cli.takt import _parse_arguments, check_and_show_warning, main


class TestTaktCLI:
    """Tests for takt.py functions."""

    @patch("pipe.cli.takt.os.path.exists")
    def test_check_and_show_warning_unsealed_exists(self, mock_exists):
        """Test that it returns True if unsealed.txt exists."""
        mock_exists.side_effect = lambda p: os.path.basename(p) == "unsealed.txt"
        assert check_and_show_warning("/mock/root") is True

    @patch("pipe.cli.takt.os.path.exists")
    @patch("pipe.cli.takt.read_text_file")
    def test_check_and_show_warning_no_content(self, mock_read, mock_exists):
        """Test that it returns True if sealed.txt has no content."""
        mock_exists.side_effect = lambda p: os.path.basename(p) == "sealed.txt"
        mock_read.return_value = ""
        assert check_and_show_warning("/mock/root") is True

    @patch("pipe.cli.takt.os.path.exists")
    @patch("pipe.cli.takt.read_text_file")
    @patch("pipe.cli.takt.input")
    @patch("pipe.cli.takt.os.rename")
    def test_check_and_show_warning_user_agrees(
        self, mock_rename, mock_input, mock_read, mock_exists
    ):
        """Test that it renames and returns True if user agrees."""
        mock_exists.side_effect = lambda p: os.path.basename(p) == "sealed.txt"
        mock_read.return_value = "Warning content"
        mock_input.return_value = "yes"

        assert check_and_show_warning("/mock/root") is True
        mock_rename.assert_called_once()

    @patch("pipe.cli.takt.os.path.exists")
    @patch("pipe.cli.takt.read_text_file")
    @patch("pipe.cli.takt.input")
    def test_check_and_show_warning_user_declines(
        self, mock_input, mock_read, mock_exists
    ):
        """Test that it returns False if user declines."""
        mock_exists.side_effect = lambda p: os.path.basename(p) == "sealed.txt"
        mock_read.return_value = "Warning content"
        mock_input.return_value = "no"

        assert check_and_show_warning("/mock/root") is False

    @patch("pipe.cli.takt.os.path.exists")
    @patch("pipe.cli.takt.read_text_file")
    @patch("pipe.cli.takt.input")
    @patch("pipe.cli.takt.os.rename")
    def test_check_and_show_warning_invalid_then_yes(
        self, mock_rename, mock_input, mock_read, mock_exists
    ):
        """Test that it retries on invalid input."""
        mock_exists.side_effect = lambda p: os.path.basename(p) == "sealed.txt"
        mock_read.return_value = "Warning content"
        mock_input.side_effect = ["maybe", "yes"]

        assert check_and_show_warning("/mock/root") is True
        assert mock_input.call_count == 2
        mock_rename.assert_called_once()

    @patch("pipe.cli.takt.os.path.exists")
    @patch("pipe.cli.takt.read_text_file")
    @patch("pipe.cli.takt.input")
    def test_check_and_show_warning_interrupt(self, mock_input, mock_read, mock_exists):
        """Test that it returns False on KeyboardInterrupt."""
        mock_exists.side_effect = lambda p: os.path.basename(p) == "sealed.txt"
        mock_read.return_value = "Warning content"
        mock_input.side_effect = KeyboardInterrupt

        assert check_and_show_warning("/mock/root") is False

    def test_parse_arguments_basic(self):
        """Test basic argument parsing."""
        test_args = ["takt", "--instruction", "test instruction"]
        with patch.object(sys, "argv", test_args):
            args, parser = _parse_arguments()
            assert args.instruction == "test instruction"
            assert args.dry_run is False

    def test_parse_arguments_complex(self):
        """Test complex argument parsing with multiple flags."""
        test_args = [
            "takt",
            "--purpose",
            "test purpose",
            "--roles",
            "role1.yml",
            "--roles",
            "role2.yml",
            "--references",
            "ref1.md,ref2.md",
            "--multi-step-reasoning",
        ]
        with patch.object(sys, "argv", test_args):
            args, parser = _parse_arguments()
            assert args.purpose == "test purpose"
            assert args.roles == ["role1.yml", "role2.yml"]
            assert args.references == ["ref1.md,ref2.md"]
            assert args.multi_step_reasoning is True

    @patch("pipe.cli.takt.get_project_root")
    @patch("pipe.cli.takt.check_and_show_warning")
    @patch("pipe.cli.takt.load_dotenv")
    @patch("pipe.cli.takt.SettingsFactory.get_settings")
    @patch("pipe.cli.takt._parse_arguments")
    @patch("pipe.cli.takt.ServiceFactory")
    @patch("pipe.cli.takt.dispatch")
    def test_main_success(
        self,
        mock_dispatch,
        mock_service_factory,
        mock_parse,
        mock_get_settings,
        mock_load_dotenv,
        mock_check_warning,
        mock_get_root,
    ):
        """Test successful main execution."""
        mock_get_root.return_value = "/mock/root"
        mock_check_warning.return_value = True
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        # Mock parsed_args
        mock_parsed_args = MagicMock()
        mock_parsed_args.instruction = "test"
        mock_parsed_args.session = None
        mock_parsed_args.purpose = "purpose"
        mock_parsed_args.background = "background"
        mock_parsed_args.roles = []
        mock_parsed_args.references = []
        mock_parsed_args.references_persist = []
        mock_parsed_args.artifacts = []
        mock_parsed_args.dry_run = False
        mock_parsed_args.parent = None
        mock_parsed_args.procedure = None
        mock_parsed_args.multi_step_reasoning = False
        mock_parsed_args.fork = None
        mock_parsed_args.at_turn = None
        mock_parsed_args.api_mode = "gemini-api"
        mock_parsed_args.therapist = None
        mock_parsed_args.output_format = "json"

        mock_parse.return_value = (mock_parsed_args, MagicMock())

        mock_session_service = MagicMock()
        mock_service_factory.return_value.create_session_service.return_value = (
            mock_session_service
        )

        with patch("pipe.cli.takt.start_session_validator.validate") as mock_validate:
            main()

            mock_check_warning.assert_called_once_with("/mock/root")
            mock_load_dotenv.assert_called_once()
            mock_get_settings.assert_called_once()
            mock_validate.assert_called_once_with("purpose", "background")
            mock_dispatch.assert_called_once()

    @patch("pipe.cli.takt.get_project_root")
    @patch("pipe.cli.takt.check_and_show_warning")
    def test_main_warning_declined(self, mock_check_warning, mock_get_root):
        """Test main exits if warning is declined."""
        mock_get_root.return_value = "/mock/root"
        mock_check_warning.return_value = False

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    @patch("pipe.cli.takt.get_project_root")
    @patch("pipe.cli.takt.check_and_show_warning")
    @patch("pipe.cli.takt.load_dotenv")
    @patch("pipe.cli.takt.SettingsFactory.get_settings")
    @patch("pipe.cli.takt._parse_arguments")
    @patch("pipe.cli.takt.ServiceFactory")
    @patch("pipe.cli.takt.dispatch")
    def test_main_dispatch_error(
        self,
        mock_dispatch,
        mock_service_factory,
        mock_parse,
        mock_get_settings,
        mock_load_dotenv,
        mock_check_warning,
        mock_get_root,
    ):
        """Test main handles dispatch errors."""
        mock_get_root.return_value = "/mock/root"
        mock_check_warning.return_value = True
        mock_get_settings.return_value = MagicMock()

        mock_parsed_args = MagicMock()
        mock_parsed_args.api_mode = None
        mock_parsed_args.instruction = "test"
        mock_parsed_args.session = "session-id"
        mock_parse.return_value = (mock_parsed_args, MagicMock())

        mock_dispatch.side_effect = ValueError("Dispatch error")

        with patch("sys.stderr", new_callable=MagicMock) as mock_stderr:
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 1
            # Verify error message was printed to stderr
            mock_stderr.write.assert_any_call("Dispatch error")

    @patch("pipe.cli.takt.get_project_root")
    @patch("pipe.cli.takt.check_and_show_warning")
    @patch("pipe.cli.takt.load_dotenv")
    @patch("pipe.cli.takt.SettingsFactory.get_settings")
    @patch("pipe.cli.takt._parse_arguments")
    @patch("pipe.cli.takt.ServiceFactory")
    @patch("pipe.cli.takt.dispatch")
    def test_main_with_api_mode_override(
        self,
        mock_dispatch,
        mock_service_factory,
        mock_parse,
        mock_get_settings,
        mock_load_dotenv,
        mock_check_warning,
        mock_get_root,
    ):
        """Test main with api_mode override from arguments."""
        mock_get_root.return_value = "/mock/root"
        mock_check_warning.return_value = True
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        mock_parsed_args = MagicMock()
        mock_parsed_args.api_mode = "custom-api"
        mock_parsed_args.instruction = "test"
        mock_parsed_args.session = "sess"
        mock_parse.return_value = (mock_parsed_args, MagicMock())

        main()

        assert mock_settings.api_mode == "custom-api"

    @patch("pipe.cli.takt.get_project_root")
    @patch("pipe.cli.takt.check_and_show_warning")
    @patch("pipe.cli.takt.load_dotenv")
    @patch("pipe.cli.takt.SettingsFactory.get_settings")
    @patch("pipe.cli.takt._parse_arguments")
    @patch("pipe.cli.takt.ServiceFactory")
    @patch("pipe.cli.takt.dispatch")
    def test_main_file_not_found_error(
        self,
        mock_dispatch,
        mock_service_factory,
        mock_parse,
        mock_get_settings,
        mock_load_dotenv,
        mock_check_warning,
        mock_get_root,
    ):
        """Test main handles FileNotFoundError."""
        mock_get_root.return_value = "/mock/root"
        mock_check_warning.return_value = True
        mock_get_settings.return_value = MagicMock()

        mock_parsed_args = MagicMock()
        mock_parsed_args.api_mode = None
        mock_parsed_args.instruction = "test"
        mock_parsed_args.session = "sess"
        mock_parse.return_value = (mock_parsed_args, MagicMock())

        mock_dispatch.side_effect = FileNotFoundError("File not found")

        with patch("sys.stderr", new_callable=MagicMock):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 1
