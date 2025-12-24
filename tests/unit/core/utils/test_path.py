"""
Unit tests for the path utility module.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_find_root_with_git_marker(self, tmp_path):
        """Test finding root when .git directory exists."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        root = get_project_root(start_dir=str(project_dir))

        assert root == str(project_dir)

    def test_find_root_with_pyproject_marker(self, tmp_path):
        """Test finding root when pyproject.toml exists."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").touch()

        root = get_project_root(start_dir=str(project_dir))

        assert root == str(project_dir)

    def test_find_root_from_nested_subdirectory(self, tmp_path):
        """Test finding root from a deeply nested subdirectory."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        sub_dir = project_dir / "src" / "pipe" / "core" / "utils"
        sub_dir.mkdir(parents=True)

        root = get_project_root(start_dir=str(sub_dir))

        assert root == str(project_dir)

    def test_find_root_with_custom_markers(self, tmp_path):
        """Test finding root using custom marker files."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "my_marker.txt").touch()

        root = get_project_root(start_dir=str(project_dir), markers=("my_marker.txt",))

        assert root == str(project_dir)

    def test_find_root_default_cwd(self, tmp_path):
        """Test finding root using current working directory as default."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        with patch("os.getcwd", return_value=str(project_dir)):
            root = get_project_root()
            assert root == str(project_dir)

    def test_find_root_fallback(self):
        """
        Test fallback behavior when no markers are found up to the filesystem root.
        The fallback should be 3 levels up from path.py.
        """
        # Create a unique marker that definitely doesn't exist
        unique_markers = ("__non_existent_marker_xyz__",)

        # Mocking os.path.exists to always return False for these markers
        # to ensure it reaches the filesystem root.
        with patch("os.path.exists", return_value=False):
            root = get_project_root(markers=unique_markers)

            # Fallback logic:
            # path.py is at src/pipe/core/utils/path.py
            # 1 level up: src/pipe/core/utils/
            # 2 levels up: src/pipe/core/
            # 3 levels up: src/pipe/
            # Wait, the code says:
            # script_dir = os.path.dirname(os.path.abspath(__file__))
            # script_dir is src/pipe/core/utils
            # return os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
            # -> src/pipe/core/utils -> src/pipe/core -> src/pipe -> src
            import src.pipe.core.utils.path as path_module

            expected_fallback = os.path.abspath(
                os.path.join(
                    os.path.dirname(os.path.abspath(path_module.__file__)),
                    "..",
                    "..",
                    "..",
                )
            )
            assert root == expected_fallback
