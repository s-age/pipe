"""
Unit tests for the read_file tool.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.read_file_result import ReadFileResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.read_file import read_file


class TestReadFile:
    """Unit tests for the read_file tool."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture for a mocked file repository."""
        repo = MagicMock()
        repo.get_absolute_path.return_value = "/project/root/test.txt"
        return repo

    @pytest.fixture
    def mock_settings(self):
        """Fixture for mocked settings."""
        return MagicMock()

    @pytest.fixture
    def mock_reference_service(self):
        """Fixture for a mocked session reference service."""
        return MagicMock()

    @pytest.fixture
    def mock_service_factory(self, mock_reference_service):
        """Fixture for a mocked service factory."""
        factory = MagicMock()
        factory.create_session_reference_service.return_value = mock_reference_service
        return factory

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    def test_read_file_success(self, mock_get_root, mock_repo_create, mock_repo):
        """Test successful file read without session."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "file content"

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("test.txt")

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, ReadFileResult)
        assert result.data.content == "file content"
        assert result.data.message is None
        mock_repo.read_text.assert_called_once_with("test.txt", limit=None, offset=0)

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    @patch("pipe.core.tools.read_file.SettingsFactory.get_settings")
    @patch("pipe.core.tools.read_file.ServiceFactory")
    @patch("os.path.getsize")
    def test_read_file_with_session_success(
        self,
        mock_getsize,
        MockServiceFactory,
        mock_get_settings,
        mock_get_root,
        mock_repo_create,
        mock_repo,
        mock_settings,
        mock_service_factory,
        mock_reference_service,
    ):
        """Test successful file read with session reference."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_get_settings.return_value = mock_settings
        MockServiceFactory.return_value = mock_service_factory

        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "file content"
        mock_getsize.return_value = 100

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("test.txt", session_id="session-123")

        assert result.is_success
        assert result.data.content == "file content"
        assert "added or updated" in result.data.message
        assert "empty" not in result.data.message
        mock_reference_service.add_reference_to_session.assert_called_once_with(
            "session-123", "/project/root/test.txt"
        )
        mock_reference_service.update_reference_ttl_in_session.assert_called_once_with(
            "session-123", "/project/root/test.txt", 3
        )

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    @patch("pipe.core.tools.read_file.SettingsFactory.get_settings")
    @patch("pipe.core.tools.read_file.ServiceFactory")
    @patch("os.path.getsize")
    def test_read_file_with_session_empty_file(
        self,
        mock_getsize,
        MockServiceFactory,
        mock_get_settings,
        mock_get_root,
        mock_repo_create,
        mock_repo,
        mock_settings,
        mock_service_factory,
        mock_reference_service,
    ):
        """Test successful file read with session, but file is empty."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_get_settings.return_value = mock_settings
        MockServiceFactory.return_value = mock_service_factory

        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = ""
        mock_getsize.return_value = 0

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("empty.txt", session_id="session-123")

        assert result.is_success
        assert result.data.content == ""
        assert "added or updated" in result.data.message
        assert "is empty" in result.data.message

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    @patch("pipe.core.tools.read_file.SettingsFactory.get_settings")
    @patch("pipe.core.tools.read_file.ServiceFactory")
    def test_read_file_with_session_failure(
        self,
        MockServiceFactory,
        mock_get_settings,
        mock_get_root,
        mock_repo_create,
        mock_repo,
        mock_settings,
        mock_service_factory,
    ):
        """Test session reference failure doesn't fail the whole operation."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_get_settings.return_value = mock_settings
        MockServiceFactory.return_value = mock_service_factory

        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "file content"

        # Simulate exception in session reference service
        mock_service_factory.create_session_reference_service.side_effect = Exception(
            "Session error"
        )

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("test.txt", session_id="session-123")

        assert result.is_success
        assert result.data.content == "file content"
        assert "Warning: Failed to add or update reference" in result.data.message
        assert "Session error" in result.data.message

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    def test_read_file_not_found(self, mock_get_root, mock_repo_create, mock_repo):
        """Test file not found error."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_repo.exists.return_value = False

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("missing.txt")

        assert not result.is_success
        assert "File not found" in result.error

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    def test_read_file_not_a_file(self, mock_get_root, mock_repo_create, mock_repo):
        """Test path is not a file error."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = False

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("directory")

        assert not result.is_success
        assert "Path is not a file" in result.error

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    def test_read_file_unicode_error(self, mock_get_root, mock_repo_create, mock_repo):
        """Test binary file error (UnicodeDecodeError)."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "reason"
        )

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("binary.bin")

        assert not result.is_success
        assert "Cannot decode file" in result.error
        assert "binary file" in result.error

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    def test_read_file_read_exception(self, mock_get_root, mock_repo_create, mock_repo):
        """Test general read exception."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.side_effect = Exception("Read error")

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("test.txt")

        assert not result.is_success
        assert "Failed to read file: Read error" in result.error

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    @patch("pipe.core.tools.read_file.SettingsFactory.get_settings")
    @patch("pipe.core.tools.read_file.ServiceFactory")
    def test_read_file_read_exception_with_session_msg(
        self,
        MockServiceFactory,
        mock_get_settings,
        mock_get_root,
        mock_repo_create,
        mock_repo,
        mock_settings,
        mock_service_factory,
    ):
        """Test read error combined with session message."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_get_settings.return_value = mock_settings
        MockServiceFactory.return_value = mock_service_factory

        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True

        # Session reference fails
        mock_service_factory.create_session_reference_service.side_effect = Exception(
            "Session error"
        )
        # File read also fails
        mock_repo.read_text.side_effect = Exception("Read error")

        with patch.dict(os.environ, {}, clear=True):
            result = read_file("test.txt", session_id="session-123")

        assert not result.is_success
        assert "Warning: Failed to add or update reference" in result.error
        assert "Session error" in result.error
        assert "Also, failed to read file: Read error" in result.error

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    def test_read_file_with_limit_offset(
        self, mock_get_root, mock_repo_create, mock_repo
    ):
        """Test that limit and offset are passed to repository."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "content"

        with patch.dict(os.environ, {}, clear=True):
            read_file("test.txt", limit=10, offset=5)

        mock_repo.read_text.assert_called_once_with("test.txt", limit=10, offset=5)

    @patch("pipe.core.tools.read_file.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_file.get_project_root")
    @patch("pipe.core.tools.read_file.SettingsFactory.get_settings")
    @patch("pipe.core.tools.read_file.ServiceFactory")
    @patch("os.path.getsize")
    def test_read_file_session_id_from_env(
        self,
        mock_getsize,
        MockServiceFactory,
        mock_get_settings,
        mock_get_root,
        mock_repo_create,
        mock_repo,
        mock_settings,
        mock_service_factory,
        mock_reference_service,
    ):
        """Test session_id fallback to environment variable."""
        mock_repo_create.return_value = mock_repo
        mock_get_root.return_value = "/project/root"
        mock_get_settings.return_value = mock_settings
        MockServiceFactory.return_value = mock_service_factory

        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "content"
        mock_getsize.return_value = 10

        # Call without session_id, but with environment variable
        with patch.dict(os.environ, {"PIPE_SESSION_ID": "env-session-id"}, clear=True):
            read_file("test.txt")

        mock_reference_service.add_reference_to_session.assert_called_once_with(
            "env-session-id", "/project/root/test.txt"
        )
