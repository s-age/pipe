"""
Unit tests for pipe.core.utils.path module.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_with_marker_in_current_dir(self, tmp_path):
        """
        Test that get_project_root finds the root when a marker is in the
        starting directory.
        """
        # Create a marker file
        (tmp_path / ".git").mkdir()

        root = get_project_root(start_dir=str(tmp_path))

        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_searching_upward(self, tmp_path):
        """
        Test that get_project_root searches upward to find the root.
        """
        # Create a structure: tmp_path/.git, tmp_path/subdir1/subdir2
        (tmp_path / "pyproject.toml").touch()
        subdir = tmp_path / "subdir1" / "subdir2"
        subdir.mkdir(parents=True)

        root = get_project_root(start_dir=str(subdir))

        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_with_custom_marker(self, tmp_path):
        """
        Test that get_project_root works with custom markers.
        """
        # Create a custom marker
        (tmp_path / "my_marker.txt").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Should find it with custom marker
        root = get_project_root(start_dir=str(subdir), markers=("my_marker.txt",))
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

        # Should NOT find it with default markers (and hit fallback)
        # We don't assert exactly where the fallback goes here,
        # just that it's not tmp_path
        root_default = get_project_root(start_dir=str(subdir))
        assert os.path.abspath(root_default) != os.path.abspath(str(tmp_path))

    def test_get_project_root_default_start_dir(self, tmp_path):
        """
        Test that get_project_root uses os.getcwd() when start_dir is None.
        """
        (tmp_path / ".git").mkdir()

        with patch("os.getcwd", return_value=str(tmp_path)):
            # os.path.abspath(os.getcwd()) will be called
            root = get_project_root(start_dir=None)
            assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_get_project_root_fallback(self, tmp_path):
        """
        Test the fallback logic when no markers are found.
        """
        # Create a directory with no markers and reach filesystem root
        # We simulate reaching root by mocking os.path.dirname
        # to return the same path
        test_dir = os.path.abspath(str(tmp_path))
        original_dirname = os.path.dirname

        with patch("os.path.exists", return_value=False):
            with patch(
                "os.path.dirname",
                side_effect=lambda x: x if x == test_dir else original_dirname(x),
            ):
                # This will break the while loop immediately
                # because parent_dir == current_dir
                root = get_project_root(start_dir=test_dir)

                # Check that fallback logic was executed
                # script_dir is src/pipe/core/utils
                # fallback is script_dir/../../../
                import pipe.core.utils.path as path_module

                script_dir = original_dirname(os.path.abspath(path_module.__file__))
                expected_fallback = os.path.abspath(
                    os.path.join(script_dir, "..", "..", "..")
                )

                assert root == expected_fallback

    def test_get_project_root_traverses_to_fs_root(self, tmp_path):
        """
        Test that the traversal stops at the filesystem root.
        """
        # We want to ensure it doesn't infinite loop
        # Mocking os.path.dirname to simulate reaching root ('/' or 'C:\')
        original_dirname = os.path.dirname
        with patch("os.path.exists", return_value=False):
            with patch("os.path.dirname") as mock_dirname:

                def side_effect(path):
                    if path == "/some/path":
                        return "/parent"
                    if path == "/parent":
                        return "/parent"  # root
                    return original_dirname(path)

                mock_dirname.side_effect = side_effect

                # This should execute the loop, then break, then hit fallback
                get_project_root(start_dir="/some/path")

                # dirname called for /some/path, then /parent, then fallback
                assert mock_dirname.call_count >= 2
