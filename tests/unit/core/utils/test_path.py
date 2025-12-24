import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_marker_in_start_dir(self, tmp_path):
        """Test when a marker file is present in the starting directory."""
        # Setup: Create a marker file in the temporary directory
        marker_file = tmp_path / "pyproject.toml"
        marker_file.touch()

        # Execute
        root = get_project_root(start_dir=str(tmp_path))

        # Verify
        assert root == str(tmp_path)

    def test_marker_in_parent_dir(self, tmp_path):
        """Test when a marker is present in a parent directory."""
        # Setup: Create a project structure
        # tmp_path/project (root with .git)
        # tmp_path/project/src/pipe (child)
        root_dir = tmp_path / "project"
        root_dir.mkdir()
        marker_dir = root_dir / ".git"
        marker_dir.mkdir()  # .git can be a directory

        child_dir = root_dir / "src" / "pipe"
        child_dir.mkdir(parents=True)

        # Execute: Search upward from child_dir
        root = get_project_root(start_dir=str(child_dir))

        # Verify: Should find the root_dir
        assert root == str(root_dir)

    def test_custom_markers(self, tmp_path):
        """Test searching for custom marker files."""
        # Setup: Create a custom marker file
        marker_file = tmp_path / "custom_marker.txt"
        marker_file.touch()

        # Execute
        root = get_project_root(start_dir=str(tmp_path), markers=("custom_marker.txt",))

        # Verify
        assert root == str(tmp_path)

    def test_default_none_uses_getcwd(self, tmp_path):
        """
        Test that get_project_root uses current working directory
        when start_dir is None.
        """
        # Setup: Create a marker in tmp_path and mock getcwd to point there
        marker_file = tmp_path / "pyproject.toml"
        marker_file.touch()

        with patch("os.getcwd", return_value=str(tmp_path)):
            # Execute
            root = get_project_root(start_dir=None)

            # Verify
            assert root == str(tmp_path)

    def test_fallback_logic(self):
        """
        Test fallback logic when no markers are found up to the
        filesystem root.
        """
        # Simulate reaching the filesystem root by mocking os.path.exists
        # to always return False
        with patch("os.path.exists", return_value=False):
            # Mock __file__ to control the fallback calculation
            test_file_path = "/abs/path/to/src/pipe/core/utils/path.py"
            with patch("pipe.core.utils.path.__file__", test_file_path):
                # Execute from a arbitrary directory
                root = get_project_root(start_dir="/abs/path/to/src/pipe")

                # Verify fallback logic:
                # script_dir = /abs/path/to/src/pipe/core/utils
                # expected = os.path.join(script_dir, "..", "..", "..")
                # -> /abs/path/to/src
                assert root == os.path.abspath("/abs/path/to/src")

    def test_marker_in_deep_structure(self, tmp_path):
        """Test finding a marker from deep within multiple subdirectories."""
        # Setup: Create a deep directory structure
        root_dir = tmp_path / "my_project"
        root_dir.mkdir()
        (root_dir / "pyproject.toml").touch()

        deep_dir = root_dir / "level1" / "level2" / "level3" / "level4" / "level5"
        deep_dir.mkdir(parents=True)

        # Execute
        root = get_project_root(start_dir=str(deep_dir))

        # Verify
        assert root == str(root_dir)

    def test_empty_markers_triggers_fallback(self, tmp_path):
        """
        Test that providing an empty markers tuple triggers
        immediate fallback logic.
        """
        # Setup
        root_dir = tmp_path / "project"
        root_dir.mkdir()

        # Execute with empty markers, which prevents finding anything
        # in the upward search
        fake_script_path = str(root_dir / "src" / "path.py")
        with patch("pipe.core.utils.path.__file__", fake_script_path):
            root = get_project_root(start_dir=str(root_dir), markers=())

            # Fallback: 3 levels up from fake_script_path's directory
            # fake_script_path = root_dir/src/path.py
            # script_dir = root_dir/src
            # expected = os.path.join(script_dir, "..", "..", "..")
            # -> parent of root_dir
            expected = os.path.abspath(
                os.path.join(str(root_dir / "src"), "..", "..", "..")
            )
            assert root == expected
