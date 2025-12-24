"""
Unit tests for the path utility module.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for the get_project_root function."""

    def test_find_root_with_git_marker(self, tmp_path):
        """Test that get_project_root finds a directory with a .git marker."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        # Search from the project directory itself
        root = get_project_root(start_dir=str(project_dir))
        assert os.path.abspath(root) == os.path.abspath(str(project_dir))

    def test_find_root_with_pyproject_marker(self, tmp_path):
        """Test that get_project_root finds a directory with a pyproject.toml marker."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").touch()

        # Search from the project directory itself
        root = get_project_root(start_dir=str(project_dir))
        assert os.path.abspath(root) == os.path.abspath(str(project_dir))

    def test_find_root_upward_search(self, tmp_path):
        """Test that get_project_root searches upward to find a marker."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        sub_dir = project_dir / "src" / "deep" / "nested" / "dir"
        sub_dir.mkdir(parents=True)

        # Search from a deep subdirectory
        root = get_project_root(start_dir=str(sub_dir))
        assert os.path.abspath(root) == os.path.abspath(str(project_dir))

    def test_custom_markers(self, tmp_path):
        """Test that get_project_root works with custom markers."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "my_marker.txt").touch()

        root = get_project_root(start_dir=str(project_dir), markers=("my_marker.txt",))
        assert os.path.abspath(root) == os.path.abspath(str(project_dir))

    def test_start_dir_defaults_to_cwd(self, tmp_path, monkeypatch):
        """Test that start_dir defaults to the current working directory."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        # Change CWD to the project directory
        monkeypatch.chdir(project_dir)

        # Call without start_dir
        root = get_project_root()
        assert os.path.abspath(root) == os.path.abspath(str(project_dir))

    def test_root_reached_without_marker_falls_back(self, tmp_path):
        """Test that the function falls back when no marker is found even at root."""
        # Use a directory that definitely has no markers above it
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # We mock __file__ indirectly by checking the fallback logic
        # Since we can't easily change the filesystem root in a portable way,
        # we'll use a mocked script location approach.

        with patch("os.path.exists", return_value=False):
            with patch("os.path.dirname") as mock_dirname:
                # Mock the loop break by returning same dir
                def mock_dir(x):
                    return x if x == str(empty_dir) else os.path.split(x)[0]

                mock_dirname.side_effect = mock_dir

                # The fallback assumes 3 levels up from path.py
                # path.py is at src/pipe/core/utils/path.py
                # 3 levels up is src/
                root = get_project_root(start_dir=str(empty_dir))

                # Instead of verifying the exact absolute path
                # (which depends on environment),
                # we verify that it's calculated relative to this file's script_dir
                import pipe.core.utils.path as path_module

                script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
                expected_fallback = os.path.abspath(
                    os.path.join(script_dir, "..", "..", "..")
                )
                assert os.path.abspath(root) == expected_fallback

    def test_multiple_markers(self, tmp_path):
        """Test that it finds the first available marker when multiple exist."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()
        (project_dir / "pyproject.toml").touch()

        root = get_project_root(start_dir=str(project_dir))
        assert os.path.abspath(root) == os.path.abspath(str(project_dir))
