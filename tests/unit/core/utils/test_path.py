"""
Unit tests for src/pipe/core/utils/path.py.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_with_git(self, tmp_path):
        """Test finding root when .git directory exists."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        root = get_project_root(start_dir=str(tmp_path))
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_with_pyproject(self, tmp_path):
        """Test finding root when pyproject.toml exists."""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.touch()

        root = get_project_root(start_dir=str(tmp_path))
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_upward_search(self, tmp_path):
        """Test searching upward from a subdirectory."""
        root_dir = tmp_path / "project"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        sub_dir = root_dir / "src" / "pipe"
        sub_dir.mkdir(parents=True)

        root = get_project_root(start_dir=str(sub_dir))
        assert os.path.abspath(root) == os.path.abspath(str(root_dir))

    def test_get_project_root_custom_markers(self, tmp_path):
        """Test finding root with custom markers."""
        marker_file = tmp_path / "my_marker.txt"
        marker_file.touch()

        root = get_project_root(start_dir=str(tmp_path), markers=("my_marker.txt",))
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_default_cwd(self, tmp_path, monkeypatch):
        """Test using current working directory as default start_dir."""
        (tmp_path / ".git").mkdir()

        # Use monkeypatch to safely mock os.getcwd
        monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))

        root = get_project_root(start_dir=None)
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_reaches_filesystem_root(self, tmp_path, monkeypatch):
        """Test behavior when searching reaches the filesystem root."""
        start_dir = tmp_path / "no_markers"
        start_dir.mkdir()

        # Mock os.path.exists to return False to force reaching root
        monkeypatch.setattr("os.path.exists", lambda _: False)

        # Mock os.path.dirname to simulate reaching root by returning same path
        # We use a wrapper to only trigger this on a specific "root" path
        # to avoid infinite loop if dirname is used elsewhere
        real_dirname = os.path.dirname

        def mock_dirname(path):
            if path == "/mock/root":
                return path
            return real_dirname(path)

        monkeypatch.setattr("os.path.dirname", mock_dirname)

        # Call with our mock root
        root = get_project_root(start_dir="/mock/root")

        # It should break the loop and return the fallback path
        assert os.path.isabs(root)
        assert root.endswith("src")

    def test_get_project_root_fallback(self, tmp_path):
        """Test fallback behavior when no markers are found."""
        # Setup: Use a directory where no markers exist
        no_marker_dir = tmp_path / "none"
        no_marker_dir.mkdir()

        # Mock os.path.exists to return False during the search loop
        # We use patch instead of monkeypatch to limit scope easily
        with patch("os.path.exists", return_value=False):
            root = get_project_root(start_dir=str(no_marker_dir))

        # The fallback should be 3 levels up from path.py (which is .../src)
        assert os.path.isabs(root)
        assert root.endswith("src")
