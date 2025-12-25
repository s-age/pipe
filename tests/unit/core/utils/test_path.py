import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_with_marker_at_start_dir(self, tmp_path):
        """Test finding marker in the start directory."""
        marker = ".git"
        (tmp_path / marker).mkdir()

        root = get_project_root(start_dir=str(tmp_path), markers=(marker,))

        assert root == os.path.abspath(str(tmp_path))

    def test_get_project_root_with_marker_upward(self, tmp_path):
        """Test finding marker in a parent directory."""
        root_dir = tmp_path / "project"
        root_dir.mkdir()
        (root_dir / "pyproject.toml").touch()

        sub_dir = root_dir / "src" / "pipe" / "core"
        sub_dir.mkdir(parents=True)

        root = get_project_root(start_dir=str(sub_dir))

        assert root == os.path.abspath(str(root_dir))

    def test_get_project_root_with_custom_markers(self, tmp_path):
        """Test finding custom marker files."""
        (tmp_path / "custom_marker").touch()

        sub_dir = tmp_path / "subdir"
        sub_dir.mkdir()

        root = get_project_root(start_dir=str(sub_dir), markers=("custom_marker",))

        assert root == os.path.abspath(str(tmp_path))

    def test_get_project_root_default_cwd(self, tmp_path):
        """Test default start_dir behavior (using cwd)."""
        marker_dir = tmp_path / "project"
        marker_dir.mkdir()
        (marker_dir / ".git").mkdir()

        sub_dir = marker_dir / "a" / "b"
        sub_dir.mkdir(parents=True)

        with patch("os.getcwd", return_value=str(sub_dir)):
            root = get_project_root()
            assert root == os.path.abspath(str(marker_dir))

    def test_get_project_root_fallback(self):
        """Test fallback logic when no markers are found."""
        with patch("os.path.exists", return_value=False):
            root = get_project_root(start_dir="/")

            import pipe.core.utils.path as path_module

            script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
            expected_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

            assert root == expected_root

    def test_get_project_root_reaches_fs_root(self, tmp_path):
        """Test when searching reaches filesystem root without finding markers."""
        root = get_project_root(
            start_dir=str(tmp_path), markers=("non-existent-marker",)
        )

        import pipe.core.utils.path as path_module

        script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
        expected_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

        assert root == expected_root
