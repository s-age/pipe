import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_current_dir_has_marker(self, tmp_path):
        """Test finding root when it is the starting directory."""
        marker = "pyproject.toml"
        marker_file = tmp_path / marker
        marker_file.touch()

        root = get_project_root(start_dir=str(tmp_path), markers=(marker,))
        assert root == str(tmp_path)
        assert os.path.isabs(root)

    def test_get_project_root_parent_dir_has_marker(self, tmp_path):
        """Test finding root in a parent directory."""
        root_dir = tmp_path / "root"
        root_dir.mkdir()
        sub_dir = root_dir / "subdir" / "deep"
        sub_dir.mkdir(parents=True)

        marker = ".git"
        (root_dir / marker).mkdir()  # .git is often a directory

        root = get_project_root(start_dir=str(sub_dir), markers=(marker,))
        assert root == str(root_dir)

    def test_get_project_root_default_markers(self, tmp_path):
        """Test finding root using default markers (.git, pyproject.toml)."""
        root_dir = tmp_path / "project"
        root_dir.mkdir()
        sub_dir = root_dir / "src"
        sub_dir.mkdir()

        (root_dir / "pyproject.toml").touch()

        root = get_project_root(start_dir=str(sub_dir))
        assert root == str(root_dir)

    def test_get_project_root_no_start_dir(self, tmp_path, monkeypatch):
        """Test using current working directory when start_dir is None."""
        root_dir = tmp_path / "work"
        root_dir.mkdir()
        (root_dir / "pyproject.toml").touch()

        monkeypatch.chdir(root_dir)
        root = get_project_root()
        assert root == str(root_dir)

    def test_get_project_root_multiple_markers(self, tmp_path):
        """Test that it finds the first marker encountered while going up."""
        grandparent = tmp_path / "grandparent"
        parent = grandparent / "parent"
        child = parent / "child"
        child.mkdir(parents=True)

        (grandparent / "pyproject.toml").touch()
        (parent / ".git").mkdir()

        # Should find .git in parent first, as it's closer to child
        root = get_project_root(start_dir=str(child))
        assert root == str(parent)

    def test_get_project_root_fallback(self, tmp_path):
        """Test fallback when no markers are found up to filesystem root."""
        # Mock os.path.exists to always return False to trigger fallback
        with patch("os.path.exists", return_value=False):
            root = get_project_root(start_dir=str(tmp_path))

            # Calculate expected fallback relative to the script location
            import pipe.core.utils.path as path_module

            script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
            expected_fallback = os.path.abspath(
                os.path.join(script_dir, "..", "..", "..")
            )

            assert root == expected_fallback

    def test_get_project_root_reaches_fs_root(self):
        """Test behavior when reaching the filesystem root without finding markers."""
        # Using a very unlikely marker to ensure it reaches the root
        marker = "non_existent_marker_xyz_123"

        # Start from root (or as close as possible in a cross-platform way)
        start_dir = os.path.abspath(os.sep)

        root = get_project_root(start_dir=start_dir, markers=(marker,))

        # Should trigger fallback
        import pipe.core.utils.path as path_module

        script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
        expected_fallback = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

        assert root == expected_fallback
