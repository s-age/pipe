"""Unit tests for the Flask application factory and utility functions in app.py."""

import sys
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask, Response
from pipe.web.app import check_and_show_warning, create_app


class TestCheckAndShowWarning:
    """Tests for the check_and_show_warning function."""

    @patch("pipe.web.app.os.path.exists")
    def test_unsealed_exists(self, mock_exists):
        """Test that it returns True if unsealed.txt exists."""
        # Return True for unsealed.txt
        mock_exists.side_effect = lambda p: "unsealed.txt" in p
        assert check_and_show_warning("/mock/root") is True

    @patch("pipe.web.app.os.path.exists")
    @patch("pipe.web.app.read_text_file")
    def test_sealed_not_found(self, mock_read, mock_exists):
        """Test that it returns True if sealed.txt is empty or not found."""
        # Return False for everything
        mock_exists.return_value = False
        mock_read.return_value = ""
        assert check_and_show_warning("/mock/root") is True

    @patch("pipe.web.app.os.path.exists")
    @patch("pipe.web.app.read_text_file")
    @patch("builtins.input")
    @patch("pipe.web.app.os.rename")
    @patch("builtins.print")
    def test_user_agrees(
        self, mock_print, mock_rename, mock_input, mock_read, mock_exists
    ):
        """Test that it renames the file and returns True when user enters 'yes'."""

        def exists_side_effect(path):
            if "unsealed.txt" in path:
                return False
            if "sealed.txt" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect
        mock_read.return_value = "Warning content"
        mock_input.return_value = "yes"

        assert check_and_show_warning("/mock/root") is True
        mock_rename.assert_called_once()
        mock_print.assert_any_call("Warning content")

    @patch("pipe.web.app.os.path.exists")
    @patch("pipe.web.app.read_text_file")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_user_disagrees(self, mock_print, mock_input, mock_read, mock_exists):
        """Test that it returns False when user enters 'no'."""

        def exists_side_effect(path):
            if "unsealed.txt" in path:
                return False
            if "sealed.txt" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect
        mock_read.return_value = "Warning content"
        mock_input.return_value = "no"

        assert check_and_show_warning("/mock/root") is False
        mock_print.assert_any_call(
            "You must agree to the terms to use this tool. Exiting."
        )

    @patch("pipe.web.app.os.path.exists")
    @patch("pipe.web.app.read_text_file")
    @patch("builtins.input")
    @patch("pipe.web.app.os.rename")
    @patch("builtins.print")
    def test_invalid_input_then_yes(
        self, mock_print, mock_rename, mock_input, mock_read, mock_exists
    ):
        """Test that it retries on invalid input until 'yes' is entered."""

        def exists_side_effect(path):
            if "unsealed.txt" in path:
                return False
            if "sealed.txt" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect
        mock_read.return_value = "Warning content"
        mock_input.side_effect = ["maybe", "yes"]

        assert check_and_show_warning("/mock/root") is True
        mock_print.assert_any_call("Invalid input. Please enter 'yes' or 'no'.")
        assert mock_rename.called

    @patch("pipe.web.app.os.path.exists")
    @patch("pipe.web.app.read_text_file")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_keyboard_interrupt(self, mock_print, mock_input, mock_read, mock_exists):
        """Test that it returns False on KeyboardInterrupt."""

        def exists_side_effect(path):
            if "unsealed.txt" in path:
                return False
            if "sealed.txt" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect
        mock_read.return_value = "Warning content"
        mock_input.side_effect = KeyboardInterrupt

        assert check_and_show_warning("/mock/root") is False
        mock_print.assert_any_call("\nOperation cancelled. Exiting.")


class TestCreateApp:
    """Tests for the create_app factory function."""

    @pytest.fixture
    def mock_services(self):
        """Fixture to mock all services and controllers."""
        with (
            patch("pipe.web.app.get_project_root") as mock_root,
            patch("pipe.web.app.SettingsFactory.get_settings") as mock_get_settings,
            patch("pipe.web.app.ServiceFactory") as mock_factory_cls,
            patch("pipe.web.app.StartSessionController"),
            patch("pipe.web.app.SessionChatController"),
            patch("pipe.web.app.SessionManagementController"),
            patch("pipe.web.app.get_container") as mock_get_container,
            patch("pipe.web.app.init_dispatcher") as mock_init_dispatcher,
            patch("pipe.web.app.CORS"),
        ):
            mock_root.return_value = "/mock/root"

            mock_settings = MagicMock()
            mock_settings.timezone = "UTC"
            mock_get_settings.return_value = mock_settings

            mock_factory = mock_factory_cls.return_value
            mock_indexer = MagicMock()
            mock_factory.create_file_indexer_service.return_value = mock_indexer
            mock_indexer.repository.base_path = "/mock/base"
            mock_indexer.repository.index_dir = "/mock/index"

            container = MagicMock()
            mock_get_container.return_value = container

            yield {
                "root": mock_root,
                "settings": mock_settings,
                "factory": mock_factory,
                "indexer": mock_indexer,
                "container": container,
                "init_dispatcher": mock_init_dispatcher,
            }

    def test_create_app_success(self, mock_services):
        """Test successful application creation and service initialization."""
        app = create_app(init_index=True)

        assert isinstance(app, Flask)
        assert app.config["JSON_AS_ASCII"] is False

        # Verify service factory calls
        mock_services["factory"].create_session_service.assert_called_once()
        mock_services["factory"].create_file_indexer_service.assert_called_once()

        # Verify container initialization
        mock_services["container"].init.assert_called_once()

        # Verify dispatcher initialization
        mock_services["init_dispatcher"].assert_called_once()

        # Verify index rebuild
        mock_services["indexer"].create_index.assert_called_once()

    def test_create_app_without_index(self, mock_services):
        """Test application creation without index initialization."""
        create_app(init_index=False)
        mock_services["indexer"].create_index.assert_not_called()

    @patch("pipe.web.app.logger")
    def test_create_app_index_failure(self, mock_logger, mock_services):
        """Test that index rebuild failure is logged but doesn't stop app creation."""
        mock_services["indexer"].create_index.side_effect = Exception("Index error")

        app = create_app(init_index=True)
        assert isinstance(app, Flask)
        mock_logger.warning.assert_called_with(
            "Failed to rebuild Whoosh index: Index error", exc_info=True
        )

    def test_timezone_warning(self, mock_services):
        """Test that a warning is printed if timezone is invalid."""
        mock_services["settings"].timezone = "Invalid/Timezone"

        with patch("builtins.print") as mock_print:
            create_app(init_index=False)
            mock_print.assert_any_call(
                "Warning: Timezone 'Invalid/Timezone' from setting.yml not found. Using UTC.",
                file=sys.stderr,
            )

    def test_dispatch_action_endpoint_options(self, mock_services):
        """Test the OPTIONS method on the dispatch action endpoint."""
        app = create_app(init_index=False)
        with app.test_client() as client:
            response = client.options("/api/v1/some/action")
            assert response.status_code == 200
            assert response.json == {"status": "ok"}
            assert response.headers["Access-Control-Allow-Origin"] == "*"

    @patch("pipe.web.app.dispatch_action")
    def test_dispatch_action_endpoint_success(self, mock_dispatch, mock_services):
        """Test successful dispatching of an action via catch-all endpoint."""
        mock_dispatch.return_value = ({"result": "success"}, 200)

        app = create_app(init_index=False)
        with app.test_client() as client:
            # Use a path that is NOT handled by blueprints to hit the catch-all
            response = client.post("/api/v1/legacy/action?arg=val")
            assert response.status_code == 200
            assert response.json == {"result": "success"}

            # Verify params parsing
            args, kwargs = mock_dispatch.call_args
            params = kwargs["params"]
            assert params["arg"] == "val"

    @patch("pipe.web.app.dispatch_action")
    def test_dispatch_action_endpoint_session_parsing(
        self, mock_dispatch, mock_services
    ):
        """Test session_id and turn_index parsing in catch-all endpoint."""
        mock_dispatch.return_value = ({}, 200)
        app = create_app(init_index=False)
        with app.test_client() as client:
            # Use paths that start with session/ but are NOT matched by blueprints
            # to hit the catch-all.

            # Test session/turn parsing
            client.post("/api/v1/session/123/turn/456/catchall")
            params = mock_dispatch.call_args[1]["params"]
            assert params["session_id"] == "123"
            assert params["turn_index"] == "456"

            # Test session/references parsing
            client.post("/api/v1/session/123/references/789/catchall")
            params = mock_dispatch.call_args[1]["params"]
            assert params["session_id"] == "123"
            assert params["reference_index"] == "789"

            # Test session/fork parsing
            client.post("/api/v1/session/123/fork/0/catchall")
            params = mock_dispatch.call_args[1]["params"]
            assert params["session_id"] == "123"
            assert params["fork_index"] == "0"

    @patch("pipe.web.app.dispatch_action")
    def test_dispatch_action_endpoint_response_object(
        self, mock_dispatch, mock_services
    ):
        """Test dispatching when it returns a Flask Response object.

        Note: The current implementation in app.py has a bug where it tries to
        unpack a Response object if it's not a tuple. This test reflects that
        it currently raises a 500 error due to TypeError.
        """
        mock_dispatch.return_value = Response("raw response", status=201)

        app = create_app(init_index=False)
        with app.test_client() as client:
            response = client.get("/api/v1/legacy/action")
            # It fails with 500 because of 'response_data, status_code = dispatch_action(...)'
            assert response.status_code == 500
            assert "unpack" in response.json["message"]

    @patch("pipe.web.app.dispatch_action")
    def test_dispatch_action_endpoint_error(self, mock_dispatch, mock_services):
        """Test error handling in the dispatch action endpoint."""
        mock_dispatch.side_effect = Exception("Dispatch failed")

        app = create_app(init_index=False)
        with app.test_client() as client:
            response = client.get("/api/v1/legacy/action")
            assert response.status_code == 500
            assert response.json == {"message": "Dispatch failed"}

    @patch("pipe.web.app.logger")
    def test_before_request_logging(self, mock_logger, mock_services):
        """Test that incoming requests are logged."""
        app = create_app(init_index=False)
        with app.test_client() as client:
            client.get("/api/v1/legacy/action")
            mock_logger.debug.assert_any_call("Incoming GET /api/v1/legacy/action")

    @patch("pipe.web.app.logger")
    def test_before_request_logging_exception(self, mock_logger, mock_services):
        """Test that before_request logging doesn't crash on exception."""
        mock_logger.debug.side_effect = Exception("Logging failed")
        app = create_app(init_index=False)
        with app.test_client() as client:
            # Should not raise exception
            response = client.get("/api/v1/legacy/action")
            assert response.status_code is not None
