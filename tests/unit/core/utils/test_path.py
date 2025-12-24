"""
Unit tests for path utility functions.
"""

import os

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_find_root_with_default_markers(self, tmp_path):
        """Test finding the project root with default markers (.git, pyproject.toml)."""
        # Create a mock project structure:
        # root/
        #   .git/
        #   subdir/
        #     subsubdir/
        root = tmp_path / "project_root"
        root.mkdir()
        (root / ".git").mkdir()

        subdir = root / "subdir" / "subsubdir"
        subdir.mkdir(parents=True)

        # Call with subdir as start_dir
        found_root = get_project_root(start_dir=str(subdir))

        assert os.path.abspath(found_root) == os.path.abspath(str(root))

    def test_find_root_with_pyproject_toml(self, tmp_path):
        """Test finding the project root with pyproject.toml."""
        root = tmp_path / "project_root_pyproject"
        root.mkdir()
        (root / "pyproject.toml").touch()

        subdir = root / "subdir"
        subdir.mkdir()

        found_root = get_project_root(start_dir=str(subdir))

        assert os.path.abspath(found_root) == os.path.abspath(str(root))

    def test_find_root_with_custom_markers(self, tmp_path):
        """Test finding the project root with custom markers."""
        root = tmp_path / "custom_project"
        root.mkdir()
        (root / "my_marker.txt").touch()

        subdir = root / "subdir"
        subdir.mkdir()

        # Call with custom markers
        found_root = get_project_root(start_dir=str(subdir), markers=("my_marker.txt",))

        assert os.path.abspath(found_root) == os.path.abspath(str(root))

    def test_find_root_start_dir_none(self, tmp_path, monkeypatch):
        """Test finding the project root when start_dir is None (uses cwd)."""
        root = tmp_path / "cwd_project"
        root.mkdir()
        (root / ".git").mkdir()

        subdir = root / "subdir"
        subdir.mkdir()

        # Change CWD to subdir
        monkeypatch.chdir(subdir)

        # Call with start_dir=None
        found_root = get_project_root(start_dir=None)

        assert os.path.abspath(found_root) == os.path.abspath(str(root))

    def test_marker_at_start_dir(self, tmp_path):
        """Test finding the project root when marker is in the start_dir itself."""
        root = tmp_path / "marker_at_start"
        root.mkdir()
        (root / ".git").mkdir()

        found_root = get_project_root(start_dir=str(root))

        assert os.path.abspath(found_root) == os.path.abspath(str(root))

    def test_fallback_to_script_location(self, tmp_path):
        """Test fallback behavior when no markers are found up to filesystem root."""
        # We need to search from a directory that has no markers in its parents.
        # tmp_path is usually deep enough, but we should be careful.
        # We can mock os.path.exists to always return False for markers.

        # To truly test the fallback logic, we can search from the root directory "/"
        # where we assume no .git or pyproject.toml exists.
        markers = ("non_existent_marker_123456789",)
        found_root = get_project_root(start_dir="/", markers=markers)

        # The fallback is script_dir + "../../.."
        # script_dir = src/pipe/core/utils
        # fallback = src/

        # Let's check where the actual path utility is.
        import pipe.core.utils.path

        actual_file = os.path.abspath(pipe.core.utils.path.__file__)
        actual_script_dir = os.path.dirname(actual_file)
        expected = os.path.abspath(os.path.join(actual_script_dir, "..", "..", ".."))

        assert os.path.abspath(found_root) == expected
