from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_found_at_start(self, tmp_path):
        """Test finding project root when marker is in the starting directory."""
        # Setup: Create a marker file in tmp_path
        (tmp_path / "pyproject.toml").touch()

        result = get_project_root(start_dir=str(tmp_path))

        assert result == str(tmp_path)

    def test_get_project_root_found_at_parent(self, tmp_path):
        """Test finding project root when marker is in a parent directory."""
        # Setup: project_root / subdir1 / subdir2
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        subdir = project_root / "subdir1" / "subdir2"
        subdir.mkdir(parents=True)

        result = get_project_root(start_dir=str(subdir))

        assert result == str(project_root)

    def test_get_project_root_with_start_dir_none(self, tmp_path, monkeypatch):
        """Test get_project_root with start_dir=None uses current working directory."""
        # Setup: Create project structure and marker
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").touch()

        # Change current working directory using monkeypatch
        monkeypatch.chdir(project_root)

        # When start_dir is None, it should use getcwd()
        result = get_project_root(start_dir=None)

        assert result == str(project_root)

    def test_get_project_root_custom_markers(self, tmp_path):
        """Test get_project_root with custom marker files."""
        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / "custom_marker.txt").touch()

        subdir = project_root / "src"
        subdir.mkdir()

        # Search with custom markers
        result = get_project_root(start_dir=str(subdir), markers=("custom_marker.txt",))

        assert result == str(project_root)

    def test_get_project_root_not_found_fallback(self, tmp_path):
        """Test fallback when no markers are found up to the filesystem root."""
        # Setup a directory with no markers
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Since we can't easily reach the REAL filesystem root and guarantee no markers exist
        # (especially .git in development environments), we test the logic that
        # it returns the fallback path when it fails to find markers.

        # We need to mock __file__ or the fallback logic to verify it.
        # The fallback is: os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
        # which is src/pipe/core/utils/path.py -> src/pipe/core/ -> src/pipe/ -> src/ -> root

        with patch(
            "pipe.core.utils.path.__file__", "/abs/path/to/src/pipe/core/utils/path.py"
        ):
            # Ensure it doesn't find any markers by using a marker that doesn't exist
            result = get_project_root(
                start_dir=str(empty_dir), markers=("NON_EXISTENT_MARKER",)
            )

            # Fallback for /abs/path/to/src/pipe/core/utils/path.py is /abs/path/to/src
            # script_dir = /abs/path/to/src/pipe/core/utils
            # 1. /abs/path/to/src/pipe/core
            # 2. /abs/path/to/src/pipe
            # 3. /abs/path/to/src
            assert result == "/abs/path/to/src"
