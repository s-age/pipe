import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_marker_in_start_dir(self, tmp_path):
        """Test when marker is present in the starting directory."""
        # Setup
        marker_file = tmp_path / "pyproject.toml"
        marker_file.touch()

        # Execute
        root = get_project_root(start_dir=str(tmp_path))

        # Verify
        assert root == str(tmp_path)

    def test_marker_in_parent_dir(self, tmp_path):
        """Test when marker is present in a parent directory."""
        # Setup
        root_dir = tmp_path / "project"
        root_dir.mkdir()
        marker_file = root_dir / ".git"
        marker_file.mkdir()  # .git can be a directory

        child_dir = root_dir / "src" / "pipe"
        child_dir.mkdir(parents=True)

        # Execute
        root = get_project_root(start_dir=str(child_dir))

        # Verify
        assert root == str(root_dir)

    def test_custom_markers(self, tmp_path):
        """Test with custom marker files."""
        # Setup
        marker_file = tmp_path / "custom_marker.txt"
        marker_file.touch()

        # Execute
        root = get_project_root(start_dir=str(tmp_path), markers=("custom_marker.txt",))

        # Verify
        assert root == str(tmp_path)

    def test_default_none_uses_getcwd(self, tmp_path):
        """Test that get_project_root uses getcwd when start_dir is None."""
        # Setup
        marker_file = tmp_path / "pyproject.toml"
        marker_file.touch()

        with patch("os.getcwd", return_value=str(tmp_path)):
            # Execute
            root = get_project_root(start_dir=None)

            # Verify
            assert root == str(tmp_path)

    def test_fallback_logic(self, tmp_path):
        """Test fallback logic when no markers are found up to the root."""
        # We simulate reaching the filesystem root by mocking os.path.exists
        # to always return False.
        with patch("os.path.exists", return_value=False):
            # We also need to mock __file__ in the module
            test_file_path = "/abs/path/to/src/pipe/core/utils/path.py"
            with patch("pipe.core.utils.path.__file__", test_file_path):
                # Execute
                root = get_project_root(start_dir="/abs/path/to/src/pipe")

                # Verify fallback:
                # script_dir = /abs/path/to/src/pipe/core/utils
                # root = os.path.join(script_dir, "..", "..", "..")
                # /abs/path/to/src/pipe/core/utils -> /abs/path/to/src/pipe/core
                # -> /abs/path/to/src/pipe -> /abs/path/to/src
                assert root == os.path.abspath("/abs/path/to/src")

    def test_marker_in_deep_structure(self, tmp_path):
        """Test finding marker from deep within subdirectories."""
        # Setup
        root_dir = tmp_path / "my_project"
        root_dir.mkdir()
        (root_dir / "pyproject.toml").touch()

        deep_dir = root_dir / "a" / "b" / "c" / "d" / "e"
        deep_dir.mkdir(parents=True)

        # Execute
        root = get_project_root(start_dir=str(deep_dir))

        # Verify
        assert root == str(root_dir)

    def test_get_project_root_empty_markers_triggers_fallback(self, tmp_path):
        """Test that empty markers list triggers fallback logic."""
        # Setup
        root_dir = tmp_path / "project"
        root_dir.mkdir()
        (root_dir / "pyproject.toml").touch()

        # Execute with empty markers
        with patch("pipe.core.utils.path.__file__", str(root_dir / "src" / "path.py")):
            # markers=() means it will never find a marker and go to fallback
            root = get_project_root(start_dir=str(root_dir), markers=())

            # Fallback: 3 levels up from root_dir/src
            # root_dir/src -> root_dir -> tmp_path -> tmp_path's parent
            expected = os.path.abspath(
                os.path.join(str(root_dir / "src"), "..", "..", "..")
            )
            assert root == expected
