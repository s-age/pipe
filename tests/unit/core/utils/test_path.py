"""
Unit tests for path utility functions.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Test get_project_root function."""

    def test_get_project_root_default_cwd(self, tmp_path, monkeypatch):
        """Test finding root when .git exists in the current working directory."""
        # Setup: Create a .git directory in tmp_path
        (tmp_path / ".git").mkdir()

        # Action: Call get_project_root from tmp_path using cwd
        monkeypatch.chdir(tmp_path)
        root = get_project_root()

        # Assert: Should return tmp_path as the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_with_absolute_path(self, tmp_path):
        """Test finding root with pyproject.toml in parent of absolute path."""
        # Setup: Create pyproject.toml in tmp_path and a subdirectory
        (tmp_path / "pyproject.toml").touch()
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)

        # Action: Call get_project_root with start_dir as absolute path
        root = get_project_root(start_dir=str(subdir))

        # Assert: Should return tmp_path as the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_with_relative_path(self, tmp_path, monkeypatch):
        """Test finding root when start_dir is provided as a relative path."""
        # Setup: Create .git in tmp_path and subdirectories
        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)

        # Action: Call get_project_root with relative path
        monkeypatch.chdir(tmp_path)
        root = get_project_root(start_dir="subdir/nested")

        # Assert: Should return tmp_path as the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_marker_in_start_dir(self, tmp_path):
        """Test finding root when the marker is exactly in the start_dir."""
        # Setup: Create .git in tmp_path
        (tmp_path / ".git").mkdir()

        # Action: Call get_project_root with start_dir containing the marker
        root = get_project_root(start_dir=str(tmp_path))

        # Assert: Should return tmp_path as the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_custom_markers(self, tmp_path):
        """Test finding root using non-default custom marker files."""
        # Setup: Create a custom marker in tmp_path
        (tmp_path / "my_custom_root").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Action: Call get_project_root with custom markers
        root = get_project_root(start_dir=str(subdir), markers=("my_custom_root",))

        # Assert: Should return tmp_path as the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_multiple_markers_priority(self, tmp_path):
        """Test priority when multiple markers exist at different levels."""
        # Setup:
        # tmp_path/pyproject.toml
        # tmp_path/subdir/.git
        # If we start from tmp_path/subdir/nested, it should find .git first
        (tmp_path / "pyproject.toml").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / ".git").mkdir()
        nested = subdir / "nested"
        nested.mkdir()

        # Action: Search from nested
        root = get_project_root(start_dir=str(nested))

        # Assert: Should find .git in subdir first
        assert os.path.abspath(root) == os.path.abspath(str(subdir))

    def test_get_project_root_fallback(self):
        """Test fallback behavior when no markers are found up to filesystem root."""
        # To simulate reaching the filesystem root without finding markers,
        # we can mock os.path.exists to always return False for any marker.

        with patch("os.path.exists", return_value=False):
            root = get_project_root(markers=("non_existent_marker",))

        # Assert: The result should match the fallback logic:
        # 3 levels up from src/pipe/core/utils/path.py
        import pipe.core.utils.path as path_module

        script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
        expected_fallback = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

        assert root == expected_fallback

    def test_get_project_root_filesystem_root(self):
        """Test behavior when reaching the filesystem root."""
        # We want to test the loop termination when parent_dir == current_dir.
        # We mock os.path.dirname to return the same value after one call.
        # And ensure os.path.exists always returns False for markers.

        original_dirname = os.path.dirname

        def side_effect_dirname(path):
            if path == "/mock/root":
                return "/mock/root"
            return original_dirname(path)

        with (
            patch("os.path.exists", return_value=False),
            patch("os.path.dirname", side_effect=side_effect_dirname),
            patch("os.path.abspath", side_effect=lambda x: x),
        ):
            # This should trigger the break in the while loop and go to fallback
            # because start_dir="/mock/root" makes dirname("/mock/root") == "/mock/root"
            root = get_project_root(start_dir="/mock/root")

        # Assert: Should hit fallback. Since we mocked abspath to return input as-is,
        # and script_dir will be dirname(abspath(__file__)).
        # path_module.__file__ will be processed by our mocked abspath (identity)
        # and then by our mocked dirname.
        import pipe.core.utils.path as path_module

        script_dir = side_effect_dirname(path_module.__file__)
        expected_fallback = os.path.join(script_dir, "..", "..", "..")

        assert root == expected_fallback
