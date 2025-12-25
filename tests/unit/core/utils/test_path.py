import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_with_marker_in_start_dir(self, tmp_path):
        """Test finding project root when marker is in the start directory."""
        # Setup: Create a directory with a marker file
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").touch()

        # Execute
        root = get_project_root(start_dir=str(project_dir))

        # Verify
        assert root == str(project_dir)

    def test_get_project_root_with_marker_in_parent_dir(self, tmp_path):
        """Test finding project root by searching upward."""
        # Setup: Create project_root/subdir/subsubdir and put marker in project_root
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        subdir = project_dir / "subdir"
        subdir.mkdir()
        subsubdir = subdir / "subsubdir"
        subsubdir.mkdir()

        # Execute
        root = get_project_root(start_dir=str(subsubdir))

        # Verify
        assert root == str(project_dir)

    def test_get_project_root_with_custom_markers(self, tmp_path):
        """Test finding project root with custom marker files."""
        # Setup: Create a directory with a custom marker
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "custom_marker.txt").touch()

        # Execute
        root = get_project_root(
            start_dir=str(project_dir), markers=("custom_marker.txt",)
        )

        # Verify
        assert root == str(project_dir)

    def test_get_project_root_defaults_to_cwd(self, tmp_path):
        """Test that start_dir defaults to current working directory."""
        # Setup: Create a directory with a marker and mock getcwd to it
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").touch()

        with patch("os.getcwd", return_value=str(project_dir)):
            # Execute
            root = get_project_root()

            # Verify
            assert root == str(project_dir)

    def test_get_project_root_fallback_to_script_location(self, tmp_path):
        """Test fallback logic when no markers are found up to filesystem root."""
        # Setup: Use a temporary directory as root to ensure no markers are found
        # We need to mock os.path.exists to always return False for markers
        # and also handle the upward traversal.
        # However, a simpler way is to mock the loop or the markers.

        # We want to test this part:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # return os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

        # Let's mock os.path.exists to never find markers
        with patch("os.path.exists", return_value=False):
            # Also mock os.path.dirname to simulate reaching filesystem root quickly
            # to avoid infinite loop or long traversal if abspath behaves unexpectedly
            with patch("os.path.dirname") as mock_dirname:
                # First call to dirname returns '/', second call returns '/' (root)
                mock_dirname.side_effect = lambda p: "/" if p != "/" else "/"

                # Execute
                root = get_project_root(start_dir="/some/path")

                # Verify it calls the fallback
                # The fallback is calculated based on pipe/core/utils/path.py
                # 3 levels up from src/pipe/core/utils is src/
                import pipe.core.utils.path as path_module

                script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
                expected_fallback = os.path.abspath(
                    os.path.join(script_dir, "..", "..", "..")
                )

                assert root == expected_fallback
