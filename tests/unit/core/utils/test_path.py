import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Test get_project_root utility function."""

    def test_finds_git_marker(self, tmp_path):
        """Test finding the project root with a .git marker."""
        root = tmp_path / "project"
        root.mkdir()
        (root / ".git").mkdir()

        subdir = root / "src" / "pipe"
        subdir.mkdir(parents=True)

        # Test from root
        assert get_project_root(start_dir=str(root)) == str(root)

        # Test from subdir
        assert get_project_root(start_dir=str(subdir)) == str(root)

    def test_finds_pyproject_marker(self, tmp_path):
        """Test finding the project root with a pyproject.toml marker."""
        root = tmp_path / "project"
        root.mkdir()
        (root / "pyproject.toml").touch()

        subdir = root / "tests"
        subdir.mkdir()

        assert get_project_root(start_dir=str(subdir)) == str(root)

    def test_custom_markers(self, tmp_path):
        """Test finding the project root with custom markers."""
        root = tmp_path / "project"
        root.mkdir()
        (root / "my_marker.txt").touch()

        assert get_project_root(start_dir=str(root), markers=("my_marker.txt",)) == str(
            root
        )

    def test_default_start_dir(self, tmp_path):
        """Test that get_project_root uses current working directory by default."""
        root = tmp_path / "project"
        root.mkdir()
        (root / ".git").mkdir()

        with patch("os.getcwd", return_value=str(root)):
            # start_dir=None defaults to os.getcwd()
            assert get_project_root() == str(root)

    def test_fallback_when_no_markers_found(self):
        """Test fallback behavior when no markers are found up to the filesystem root."""
        # Use a non-existent marker to ensure we hit the fallback
        with patch("os.path.exists", return_value=False):
            root = get_project_root(
                start_dir="/some/random/path", markers=("non_existent_marker",)
            )
            assert os.path.isabs(root)
            assert isinstance(root, str)
            # The fallback path is calculated from the script location.
            # We don't check exact value to avoid environment dependency.
