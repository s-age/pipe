import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_find_root_in_start_dir(self, tmp_path):
        """Test finding root when marker is in starting directory."""
        # Create a marker in the temp directory
        (tmp_path / "pyproject.toml").touch()

        root = get_project_root(start_dir=str(tmp_path))
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_find_root_in_parent_dir(self, tmp_path):
        """Test finding root when marker is in a parent directory."""
        root_dir = tmp_path / "project"
        root_dir.mkdir()
        subdir = root_dir / "src" / "pipe"
        subdir.mkdir(parents=True)

        # Create a marker in the root directory
        (root_dir / ".git").mkdir()

        root = get_project_root(start_dir=str(subdir))
        assert os.path.abspath(root) == os.path.abspath(str(root_dir))

    def test_find_root_with_custom_markers(self, tmp_path):
        """Test finding the project root with custom markers."""
        (tmp_path / "custom_marker").touch()

        root = get_project_root(start_dir=str(tmp_path), markers=("custom_marker",))
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_find_root_default_start_dir(self, tmp_path, monkeypatch):
        """Test finding root using the default starting directory (CWD)."""
        (tmp_path / "pyproject.toml").touch()

        # Change the current working directory to the temp path
        monkeypatch.chdir(tmp_path)

        root = get_project_root()
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_fallback_to_script_location(self):
        """Test the fallback logic when no markers are found."""
        # Mock os.path.exists to always return False for the markers
        # and mock os.path.dirname to simulate reaching filesystem root
        # This will force the function to break the loop and hit fallback
        with patch("os.path.exists", return_value=False):
            # We don't need to mock os.path.dirname if we use a path
            # that eventually reaches root
            # But it's safer to mock it to break the loop quickly
            with patch("os.path.dirname", side_effect=lambda p: p):
                root = get_project_root(start_dir="/some/path")

                # The fallback is hardcoded relative to the path.py file.
                # Just verify it's an absolute path.
                assert os.path.isabs(root)

    def test_reach_filesystem_root(self, tmp_path):
        """Test that the loop terminates when filesystem root is reached."""
        # Mocking exists is easier
        with patch("os.path.exists", return_value=False):
            # This should hit the fallback logic
            root = get_project_root(start_dir=str(tmp_path))
            assert os.path.isabs(root)
