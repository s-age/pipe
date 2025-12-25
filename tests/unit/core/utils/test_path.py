"""
Unit tests for get_project_root utility.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Test get_project_root function."""

    def test_find_marker_in_start_dir(self, tmp_path):
        """Test when the marker is in the starting directory."""
        # Setup: Create a marker in the temp directory
        (tmp_path / "pyproject.toml").touch()

        # Execute
        root = get_project_root(start_dir=str(tmp_path))

        # Verify
        assert root == str(os.path.abspath(tmp_path))

    def test_find_marker_in_parent_dir(self, tmp_path):
        """Test when the marker is in a parent directory."""
        # Setup: Create a marker in the root, and a deep subdirectory
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        nested_dir = project_root / "src" / "pipe" / "core"
        nested_dir.mkdir(parents=True)

        # Execute
        root = get_project_root(start_dir=str(nested_dir))

        # Verify
        assert root == str(os.path.abspath(project_root))

    def test_custom_markers(self, tmp_path):
        """Test searching for custom marker files."""
        # Setup: Create a custom marker
        (tmp_path / "custom_marker.txt").touch()

        # Execute
        root = get_project_root(start_dir=str(tmp_path), markers=("custom_marker.txt",))

        # Verify
        assert root == str(os.path.abspath(tmp_path))

    def test_default_start_dir_uses_cwd(self, tmp_path, monkeypatch):
        """Test that start_dir defaults to current working directory."""
        # Setup: Create a marker and change CWD
        (tmp_path / "pyproject.toml").touch()
        monkeypatch.chdir(tmp_path)

        # Execute
        root = get_project_root()

        # Verify
        assert root == str(os.path.abspath(tmp_path))

    def test_fallback_logic(self):
        """Test the fallback logic when no markers are found."""
        # Setup: Mock os.path.exists to always return False to trigger fallback
        with patch("os.path.exists", return_value=False):
            # Also mock os.path.dirname for the loop to terminate quickly if it somehow loops
            # But the loop should terminate when it reaches the filesystem root.
            # To be safe and fast, we can start from root.
            root = get_project_root(start_dir="/")

            # Expected: 3 levels up from src/pipe/core/utils/path.py -> src
            import pipe.core.utils.path as path_module

            script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
            expected_fallback = os.path.abspath(
                os.path.join(script_dir, "..", "..", "..")
            )

            assert root == expected_fallback

    def test_reaches_filesystem_root(self):
        """Test that the function handles reaching the filesystem root without markers."""
        # Using a marker that definitely doesn't exist
        with patch("os.path.exists", return_value=False):
            # This should trigger the break when parent_dir == current_dir
            # and then return the fallback.
            root = get_project_root(start_dir="/", markers=("nonexistent_marker",))

            import pipe.core.utils.path as path_module

            script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
            expected_fallback = os.path.abspath(
                os.path.join(script_dir, "..", "..", "..")
            )

            assert root == expected_fallback
