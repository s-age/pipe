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

        sub_dir = root_dir / "src" / "pipe" / "core"
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

    def test_get_project_root_with_file_as_start_dir(self, tmp_path):
        """Test searching upward when start_dir is a file path."""
        root_dir = tmp_path / "project"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        file_path = root_dir / "some_file.py"
        file_path.touch()

        root = get_project_root(start_dir=str(file_path))
        assert os.path.abspath(root) == os.path.abspath(str(root_dir))

    def test_get_project_root_reaches_filesystem_root(self, monkeypatch):
        """Test behavior when searching reaches the filesystem root without markers."""
        # Mock os.path.exists to always return False
        monkeypatch.setattr(os.path, "exists", lambda _: False)

        # Mock os.path.dirname to simulate reaching the root
        real_dirname = os.path.dirname

        def mock_dirname(path):
            if path == "/mock/root":
                return path
            return real_dirname(path)

        monkeypatch.setattr(os.path, "dirname", mock_dirname)

        # Mock abspath to handle our mock root
        real_abspath = os.path.abspath

        def mock_abspath(p):
            return p if p == "/mock/root" else real_abspath(p)

        monkeypatch.setattr(os.path, "abspath", mock_abspath)

        # This should break the loop and go to fallback
        root = get_project_root(start_dir="/mock/root")

        assert os.path.isabs(root)
        # Ensure it returns something sensible (not an infinite loop)
        assert len(root) > 0

    def test_get_project_root_fallback_logic(self):
        """Test fallback behavior directly by mocking the loop to fail."""
        with patch("os.path.exists", return_value=False):
            # Mock dirname to return its input to force immediate loop break
            with patch("os.path.dirname", side_effect=lambda p: p):
                root = get_project_root(start_dir="/some/path")

        assert os.path.isabs(root)
        # Should be a path within the project
        assert "pipe" in root or "src" in root

    def test_get_project_root_multiple_markers(self, tmp_path):
        """Test that it finds the first marker it encounters upward."""
        grandparent = tmp_path / "grandparent"
        grandparent.mkdir()
        (grandparent / "pyproject.toml").touch()

        parent = grandparent / "parent"
        parent.mkdir()
        (parent / ".git").mkdir()

        child = parent / "child"
        child.mkdir()

        # Should find .git in 'parent' first
        root = get_project_root(start_dir=str(child))
        assert os.path.abspath(root) == os.path.abspath(str(parent))

        # If we only look for pyproject.toml, it should find it in 'grandparent'
        root = get_project_root(start_dir=str(child), markers=("pyproject.toml",))
        assert os.path.abspath(root) == os.path.abspath(str(grandparent))
