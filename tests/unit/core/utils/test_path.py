import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_finds_git_marker(self, tmp_path):
        """Test that get_project_root finds the root based on .git directory."""
        # Create a dummy project structure
        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        sub_dir = project_root / "src" / "pipe" / "core"
        sub_dir.mkdir(parents=True)

        root = get_project_root(start_dir=str(sub_dir))
        assert root == str(project_root)

    def test_get_project_root_finds_pyproject_marker(self, tmp_path):
        """Test that get_project_root finds the root based on pyproject.toml file."""
        # Create a dummy project structure
        project_root = tmp_path / "another_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").touch()

        sub_dir = project_root / "tests" / "unit"
        sub_dir.mkdir(parents=True)

        root = get_project_root(start_dir=str(sub_dir))
        assert root == str(project_root)

    def test_get_project_root_with_custom_markers(self, tmp_path):
        """Test that get_project_root works with custom markers."""
        project_root = tmp_path / "custom_project"
        project_root.mkdir()
        (project_root / "my_marker.txt").touch()

        sub_dir = project_root / "subdir"
        sub_dir.mkdir()

        root = get_project_root(start_dir=str(sub_dir), markers=("my_marker.txt",))
        assert root == str(project_root)

    def test_get_project_root_defaults_to_cwd(self, tmp_path):
        """Test that get_project_root defaults to current working directory."""
        project_root = tmp_path / "cwd_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").touch()

        with patch("os.getcwd", return_value=str(project_root)):
            # os.path.abspath(os.getcwd()) will use our patched getcwd
            root = get_project_root()
            assert root == str(project_root)

    def test_get_project_root_fallback_no_markers(self, tmp_path):
        """Test the fallback logic when no markers are found up to filesystem root."""
        # Start from a directory that has no markers in its ancestry
        # Using a directory that is definitely not in a project root
        root_dir = tmp_path / "no_markers_anywhere"
        root_dir.mkdir()

        # To ensure we don't accidentally find real project markers,
        # we can use a completely empty directory and mock markers.
        # However, the easiest way to test fallback is to mock os.path.exists
        # to always return False for markers.

        with patch("os.path.exists", return_value=False):
            root = get_project_root(start_dir=str(root_dir))

            # The fallback assumes 3 levels up from the script location.
            # script_dir = src/pipe/core/utils
            # fallback = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
            # We expect it to be some path ending in src/pipe (relative to our script)
            assert root.endswith(os.path.sep + "src") or root.endswith("src")

    def test_get_project_root_stops_at_filesystem_root(self):
        """Test that the loop stops at the filesystem root."""
        # This is implicitly tested by the fallback test, but we can be more explicit
        # if we can mock os.path.dirname to reach the root quickly.

        # Passing the actual filesystem root as start_dir
        root_path = os.path.abspath(os.sep)

        # Mock os.path.exists to return False so it triggers the "Reached filesystem root" break
        with patch("os.path.exists", return_value=False):
            root = get_project_root(start_dir=root_path)
            # Should trigger fallback
            assert root is not None
