"""
Unit tests for the path utility module.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for the get_project_root function."""

    def test_get_project_root_from_current_dir(self, tmp_path):
        """Test finding the project root when a marker is in the start directory."""
        # Setup: Create a marker in the tmp_path
        marker = "pyproject.toml"
        (tmp_path / marker).touch()

        # Execute
        root = get_project_root(start_dir=str(tmp_path))

        # Verify
        assert root == str(tmp_path)

    def test_get_project_root_from_nested_dir(self, tmp_path):
        """Test finding the project root from a nested subdirectory."""
        # Setup: Create a marker in the tmp_path and a nested directory
        marker = ".git"
        (tmp_path / marker).mkdir()
        nested_dir = tmp_path / "subdir1" / "subdir2"
        nested_dir.mkdir(parents=True)

        # Execute
        root = get_project_root(start_dir=str(nested_dir))

        # Verify
        assert root == str(tmp_path)

    def test_get_project_root_with_custom_markers(self, tmp_path):
        """Test finding the project root using custom marker files."""
        # Setup: Create a custom marker
        marker = "my_custom_marker"
        (tmp_path / marker).touch()

        # Execute
        root = get_project_root(start_dir=str(tmp_path), markers=(marker,))

        # Verify
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

    def test_get_project_root_default_start_dir(self, tmp_path, monkeypatch):
        """Test finding the project root using the default starting directory (CWD)."""
        # Setup: Create a marker in tmp_path and change CWD to it
        marker = "pyproject.toml"
        (tmp_path / marker).touch()
        monkeypatch.chdir(tmp_path)

        # Execute
        root = get_project_root()

        # Verify
        assert root == str(tmp_path)

    def test_get_project_root_empty_markers(self, tmp_path):
        """Test that empty markers lead to fallback logic."""
        (tmp_path / ".git").mkdir()

        # Even with .git present, if markers is empty, it should fallback
        with patch("os.path.exists", return_value=False):
            root = get_project_root(start_dir=str(tmp_path), markers=())
            # Fallback should be returned (absolute path)
            assert os.path.isabs(root)

    def test_get_project_root_fallback(self):
        """Test the fallback logic when no markers are found up to the root."""
        with patch("os.path.exists", return_value=False):
            with patch(
                "pipe.core.utils.path.__file__", "/mock/src/pipe/core/utils/path.py"
            ):
                # Fallback is script_dir ( /mock/src/pipe/core/utils ) + "../../.."
                # utils -> core -> pipe -> src
                root = get_project_root(start_dir="/mock/start")

                assert root.endswith("src")
                assert "mock" in root

    def test_get_project_root_reaches_filesystem_root(self, tmp_path):
        """Test that the search stops and falls back when the filesystem root is reached."""
        # Start from a path and ensure we don't find anything
        with patch("os.path.exists", return_value=False):
            # This should trigger the break in the while loop when parent_dir == current_dir
            root = get_project_root(start_dir=str(tmp_path))

            # Should return the fallback path
            assert root is not None
            assert os.path.isabs(root)
