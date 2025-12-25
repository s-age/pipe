import os
from unittest.mock import patch

import pipe.core.utils.path as path_module
from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Test get_project_root utility function."""

    def test_get_project_root_finds_marker_at_start_dir(self, tmp_path):
        """Test finding a marker file in the starting directory."""
        # Setup: create a marker file in a temp directory
        (tmp_path / ".git").mkdir()

        root = get_project_root(start_dir=str(tmp_path))

        assert root == str(tmp_path)

    def test_get_project_root_finds_marker_in_parent(self, tmp_path):
        """Test finding a marker file in a parent directory."""
        # Setup:
        # tmp_path/ (root)
        # ├── .git/
        # └── sub1/
        #     └── sub2/
        (tmp_path / ".git").mkdir()
        sub_dir = tmp_path / "sub1" / "sub2"
        sub_dir.mkdir(parents=True)

        root = get_project_root(start_dir=str(sub_dir))

        assert root == str(tmp_path)

    def test_get_project_root_custom_markers(self, tmp_path):
        """Test finding a custom marker file."""
        # Setup:
        # tmp_path/ (root)
        # └── my_marker.txt
        (tmp_path / "my_marker.txt").touch()

        root = get_project_root(start_dir=str(tmp_path), markers=("my_marker.txt",))

        assert root == str(tmp_path)

    def test_get_project_root_multiple_markers(self, tmp_path):
        """Test finding the nearest marker among multiple specified markers."""
        # Setup:
        # tmp_path/ (root)
        # ├── .git/
        # └── sub/
        #     ├── pyproject.toml
        #     └── target/
        (tmp_path / ".git").mkdir()
        sub_dir = tmp_path / "sub"
        sub_dir.mkdir()
        (sub_dir / "pyproject.toml").touch()
        target_dir = sub_dir / "target"
        target_dir.mkdir()

        # Should find pyproject.toml in sub/ first, not .git in tmp_path/
        root = get_project_root(start_dir=str(target_dir))

        assert root == str(sub_dir)

    def test_get_project_root_default_cwd(self, tmp_path):
        """Test that start_dir=None uses the current working directory."""
        # Setup: create a marker in tmp_path and change CWD
        (tmp_path / "pyproject.toml").touch()

        with patch("os.getcwd", return_value=str(tmp_path)):
            root = get_project_root(start_dir=None)
            assert root == str(tmp_path)

    def test_get_project_root_empty_markers(self, tmp_path):
        """Test that empty markers lead to fallback logic."""
        (tmp_path / ".git").mkdir()
        script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
        expected_fallback = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

        # Even with .git present, if markers is empty, it should fallback
        root = get_project_root(start_dir=str(tmp_path), markers=())
        assert root == expected_fallback

    def test_get_project_root_fallback(self, tmp_path):
        """Test fallback logic when no markers are found.

        The fallback logic assumes the root is 3 levels up from the script location.
        """
        # Calculate the expected fallback path
        script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
        expected_fallback = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

        # We use a directory that definitely has no markers up to the filesystem root
        with patch("os.path.exists", return_value=False):
            root = get_project_root(start_dir=str(tmp_path))
            assert root == expected_fallback

    def test_get_project_root_stops_at_filesystem_root(self):
        """Test that the upward search stops at the filesystem root."""
        script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
        expected_fallback = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

        with patch("os.path.exists", return_value=False):
            # If it reaches the root, it should break the while loop and return fallback
            # We use "/" for Unix systems as a root example
            root = get_project_root(start_dir="/")
            assert root == expected_fallback
