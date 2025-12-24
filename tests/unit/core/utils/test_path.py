import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_with_marker_in_current_dir(self, tmp_path):
        """Test finding project root when marker is in the starting directory."""
        # Create a marker file
        marker = ".git"
        (tmp_path / marker).mkdir()

        result = get_project_root(start_dir=str(tmp_path), markers=(marker,))

        assert result == str(tmp_path)
        assert os.path.isabs(result)

    def test_get_project_root_with_marker_in_parent_dir(self, tmp_path):
        """Test finding project root when marker is in a parent directory."""
        # Create a marker file in the root
        marker = "pyproject.toml"
        (tmp_path / marker).touch()

        # Create a nested directory structure
        subdir = tmp_path / "src" / "pipe" / "core"
        subdir.mkdir(parents=True)

        result = get_project_root(start_dir=str(subdir), markers=(marker,))

        assert result == str(tmp_path)

    def test_get_project_root_with_custom_markers(self, tmp_path):
        """Test finding project root using custom markers."""
        marker = "my_custom_marker"
        (tmp_path / marker).touch()

        result = get_project_root(start_dir=str(tmp_path), markers=(marker,))

        assert result == str(tmp_path)

    def test_get_project_root_default_start_dir(self, tmp_path, monkeypatch):
        """Test finding project root when start_dir is None (defaults to cwd)."""
        marker = ".git"
        (tmp_path / marker).mkdir()

        # Change CWD to the tmp_path
        monkeypatch.chdir(tmp_path)

        result = get_project_root(markers=(marker,))

        assert result == str(tmp_path)

    def test_get_project_root_multiple_markers(self, tmp_path):
        """Test that any of the provided markers can identify the project root."""
        # Create only one of the default markers
        (tmp_path / "pyproject.toml").touch()

        result = get_project_root(start_dir=str(tmp_path))

        assert result == str(tmp_path)

    def test_get_project_root_fallback(self, tmp_path):
        """Test fallback behavior when no markers are found."""
        # Use a directory that definitely has no markers up to root
        with patch("os.path.exists", return_value=False):
            result = get_project_root(start_dir=str(tmp_path))

            # The fallback logic uses its own __file__, which is path.py
            import pipe.core.utils.path

            # We need to handle cases where __file__ might be None or not present,
            # though in standard execution it should be there.
            script_file = pipe.core.utils.path.__file__
            assert script_file is not None
            script_dir = os.path.dirname(os.path.abspath(script_file))
            expected = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

            assert result == expected

    def test_get_project_root_reached_filesystem_root(self, tmp_path):
        """Test behavior when search reaches the filesystem root."""
        # Mock os.path.dirname to return the same directory (simulating filesystem root)
        # and os.path.exists to return False.
        with (
            patch("os.path.dirname") as mock_dirname,
            patch("os.path.exists", return_value=False),
        ):
            # Simulate filesystem root by returning the same path
            mock_dirname.side_effect = lambda x: x

            result = get_project_root(start_dir=str(tmp_path))

            # Should still hit fallback
            import pipe.core.utils.path

            script_file = pipe.core.utils.path.__file__
            assert script_file is not None
            script_dir = os.path.dirname(os.path.abspath(script_file))
            expected = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

            assert result == expected
