"""Unit tests for the read_many_files tool."""

import os
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.read_many_files_result import ReadManyFilesResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.read_many_files import read_many_files


class TestReadManyFiles:
    """Unit tests for read_many_files tool."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture for a mocked file repository."""
        repo = MagicMock()
        repo.is_dir.return_value = False
        repo.glob.return_value = []
        repo.read_text.return_value = "content"
        return repo

    @pytest.fixture
    def mock_reference_service(self):
        """Fixture for a mocked reference service."""
        return MagicMock()

    @pytest.fixture
    def mock_service_factory(self, mock_reference_service):
        """Fixture for a mocked service factory."""
        factory = MagicMock()
        factory.create_session_reference_service.return_value = mock_reference_service
        return factory

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_read_single_file(self, mock_repo_create, mock_get_root, mock_repo):
        """Test reading a single file successfully."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = ["/project/file1.txt"]
        mock_repo.read_text.return_value = "file1 content"

        result = read_many_files(paths=["file1.txt"])

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, ReadManyFilesResult)
        assert len(result.data.files) == 1
        assert result.data.files[0].path == "/project/file1.txt"
        assert result.data.files[0].content == "file1 content"
        assert result.data.files[0].error is None

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_read_multiple_files(self, mock_repo_create, mock_get_root, mock_repo):
        """Test reading multiple files successfully."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        # Mock glob to return different files for different calls if needed,
        # but here we just return all at once for simplicity
        mock_repo.glob.side_effect = [
            ["/project/file1.txt"],
            ["/project/file2.txt"],
        ]
        mock_repo.read_text.side_effect = ["content1", "content2"]

        result = read_many_files(paths=["file1.txt", "file2.txt"])

        assert result.is_success
        assert len(result.data.files) == 2
        paths = [f.path for f in result.data.files]
        assert "/project/file1.txt" in paths
        assert "/project/file2.txt" in paths

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_read_directory(self, mock_repo_create, mock_get_root, mock_repo):
        """Test reading a directory (should trigger recursive glob)."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.is_dir.side_effect = lambda p: p == "src"
        mock_repo.glob.return_value = ["/project/src/a.py", "/project/src/b.py"]

        result = read_many_files(paths=["src"])

        assert result.is_success
        assert len(result.data.files) == 2
        # Verify that glob was called with the directory pattern
        mock_repo.glob.assert_called_once_with(
            "src/**/*",
            search_path="/project",
            recursive=True,
            respect_gitignore=False,
        )

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_filtering_exclude(self, mock_repo_create, mock_get_root, mock_repo):
        """Test that exclude patterns work correctly."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = [
            "/project/src/main.py",
            "/project/src/test.py",
            "/project/README.md",
        ]

        # Exclude test files
        result = read_many_files(paths=["**/*"], exclude=["*test.py"])

        assert result.is_success
        paths = [os.path.relpath(f.path, "/project") for f in result.data.files]
        assert "src/main.py" in paths
        assert "README.md" in paths
        assert "src/test.py" not in paths

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_filtering_include(self, mock_repo_create, mock_get_root, mock_repo):
        """Test that include patterns work correctly."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = [
            "/project/src/main.py",
            "/project/src/main.js",
            "/project/README.md",
        ]

        # Include only .py files
        result = read_many_files(paths=["**/*"], include=["*.py"])

        assert result.is_success
        assert len(result.data.files) == 1
        assert result.data.files[0].path == "/project/src/main.py"

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_max_files_truncation(self, mock_repo_create, mock_get_root, mock_repo):
        """Test that max_files limit truncates the result and adds a message."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = [f"/project/file{i}.txt" for i in range(10)]

        result = read_many_files(paths=["*.txt"], max_files=3)

        assert result.is_success
        assert len(result.data.files) == 3
        assert "Found 10 files but showing only the first 3" in result.data.message

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_no_files_found(self, mock_repo_create, mock_get_root, mock_repo):
        """Test behavior when no files match the criteria."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = []

        result = read_many_files(paths=["nonexistent"])

        assert result.is_success
        assert len(result.data.files) == 0
        assert "No files found" in result.data.message

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_many_files.SettingsFactory.get_settings")
    @patch("pipe.core.tools.read_many_files.ServiceFactory")
    def test_reference_tracking(
        self,
        mock_service_factory_class,
        mock_get_settings,
        mock_repo_create,
        mock_get_root,
        mock_repo,
        mock_reference_service,
    ):
        """Test that references are added to the session."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = ["/project/file1.txt"]

        # Setup service factory mock
        mock_factory_instance = MagicMock()
        mock_service_factory_class.return_value = mock_factory_instance
        mock_factory_instance.create_session_reference_service.return_value = (
            mock_reference_service
        )

        result = read_many_files(paths=["file1.txt"], session_id="session-123")

        assert result.is_success
        mock_reference_service.add_multiple_references.assert_called_once_with(
            "session-123", ["/project/file1.txt"]
        )

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_unicode_decode_error(self, mock_repo_create, mock_get_root, mock_repo):
        """Test handling of binary files (UnicodeDecodeError)."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = ["/project/binary.bin"]
        mock_repo.read_text.side_effect = UnicodeDecodeError(
            "utf-8", b"\xff", 0, 1, "invalid"
        )

        result = read_many_files(paths=["binary.bin"])

        assert result.is_success
        assert len(result.data.files) == 1
        assert result.data.files[0].content is None
        assert "Cannot decode file as text" in result.data.files[0].error

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_file_read_exception(self, mock_repo_create, mock_get_root, mock_repo):
        """Test handling of general exceptions during file reading."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = ["/project/error.txt"]
        mock_repo.read_text.side_effect = Exception("Permission denied")

        result = read_many_files(paths=["error.txt"])

        assert result.is_success
        assert len(result.data.files) == 1
        assert "Failed to read file: Permission denied" in result.data.files[0].error

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_general_exception_handling(self, mock_repo_create, mock_get_root):
        """Test that unexpected exceptions in the tool are caught."""
        mock_get_root.return_value = "/project"
        mock_repo = MagicMock()
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.side_effect = Exception("Unexpected crash")

        result = read_many_files(paths=["*"])

        assert not result.is_success
        assert "Error in read_many_files tool: Unexpected crash" in result.error

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    @patch("pipe.core.tools.read_many_files.SettingsFactory.get_settings")
    def test_reference_service_setup_failure(
        self, mock_get_settings, mock_repo_create, mock_get_root, mock_repo
    ):
        """Test that reference service setup failure is handled gracefully."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = ["/project/file1.txt"]
        mock_get_settings.side_effect = Exception("Settings error")

        # Should not raise exception, just continue without reference tracking
        result = read_many_files(paths=["file1.txt"], session_id="session-123")

        assert result.is_success
        assert len(result.data.files) == 1

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_add_references_failure(self, mock_repo_create, mock_get_root, mock_repo):
        """Test that failure to add references is handled gracefully."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = ["/project/file1.txt"]

        mock_ref_service = MagicMock()
        mock_ref_service.add_multiple_references.side_effect = Exception("DB error")

        # Should not raise exception, just continue
        result = read_many_files(
            paths=["file1.txt"],
            session_id="session-123",
            reference_service=mock_ref_service,
        )

        assert result.is_success
        assert len(result.data.files) == 1
        mock_ref_service.add_multiple_references.assert_called_once()

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_default_excludes(self, mock_repo_create, mock_get_root, mock_repo):
        """Test that default excludes are applied."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = [
            "/project/src/app.py",
            "/project/.git/config",
            "/project/__pycache__/app.cpython-310.pyc",
        ]

        # useDefaultExcludes is True by default
        result = read_many_files(paths=["**/*"])

        assert result.is_success
        paths = [os.path.relpath(f.path, "/project") for f in result.data.files]
        assert "src/app.py" in paths
        assert ".git/config" not in paths
        assert "__pycache__/app.cpython-310.pyc" not in paths

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_disable_default_excludes(self, mock_repo_create, mock_get_root, mock_repo):
        """Test that default excludes can be disabled."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo

        mock_repo.glob.return_value = [
            "/project/src/app.py",
            "/project/.git/config",
        ]

        result = read_many_files(paths=["**/*"], useDefaultExcludes=False)

        assert result.is_success
        paths = [os.path.relpath(f.path, "/project") for f in result.data.files]
        assert "src/app.py" in paths
        assert ".git/config" in paths

    @patch("pipe.core.tools.read_many_files.get_project_root")
    @patch("pipe.core.tools.read_many_files.FileRepositoryFactory.create")
    def test_session_id_from_env(self, mock_repo_create, mock_get_root, mock_repo):
        """Test that session_id is picked up from environment if not provided."""
        mock_get_root.return_value = "/project"
        mock_repo_create.return_value = mock_repo
        mock_repo.glob.return_value = ["/project/file1.txt"]

        with patch.dict(os.environ, {"PIPE_SESSION_ID": "env-session-id"}):
            # We need to mock ServiceFactory to avoid real settings loading
            with patch("pipe.core.tools.read_many_files.ServiceFactory") as mock_sf:
                mock_ref_service = MagicMock()
                mock_sf.return_value.create_session_reference_service.return_value = (
                    mock_ref_service
                )
                # Also mock SettingsFactory
                with patch(
                    "pipe.core.tools.read_many_files.SettingsFactory.get_settings"
                ):
                    result = read_many_files(paths=["file1.txt"])

                    assert result.is_success
                    mock_ref_service.add_multiple_references.assert_called_once_with(
                        "env-session-id", ["/project/file1.txt"]
                    )
