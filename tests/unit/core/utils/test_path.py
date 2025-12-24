import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root utility function."""

    def test_get_project_root_marker_in_current_dir(self, tmp_path):
        """Test finding project root when marker is in the starting directory."""
        # Create a marker file in the temp directory
        marker_file = tmp_path / "pyproject.toml"
        marker_file.touch()

        # Call the function with start_dir set to temp directory
        result = get_project_root(start_dir=str(tmp_path))

        assert result == str(tmp_path)

    def test_get_project_root_marker_in_parent_dir(self, tmp_path):
        """Test finding project root when marker is in a parent directory."""
        # Create structure: parent_dir/child_dir
        parent_dir = tmp_path / "parent"
        child_dir = parent_dir / "child"
        child_dir.mkdir(parents=True)

        # Create marker in parent_dir
        marker_file = parent_dir / ".git"
        marker_file.mkdir()  # .git can be a directory

        # Call the function with start_dir set to child_dir
        result = get_project_root(start_dir=str(child_dir))

        assert result == str(parent_dir)

    def test_get_project_root_custom_marker(self, tmp_path):
        """Test finding project root using a custom marker."""
        # Create structure: parent_dir/child_dir
        parent_dir = tmp_path / "parent"
        child_dir = parent_dir / "child"
        child_dir.mkdir(parents=True)

        # Create custom marker in parent_dir
        marker_file = parent_dir / "my_custom_marker.txt"
        marker_file.touch()

        # Call with custom marker
        result = get_project_root(
            start_dir=str(child_dir), markers=("my_custom_marker.txt",)
        )

        assert result == str(parent_dir)

    @patch("os.getcwd")
    def test_get_project_root_default_start_dir(self, mock_getcwd, tmp_path):
        """Test that get_project_root defaults to current working directory."""
        # Setup temp dir with marker
        marker_file = tmp_path / "pyproject.toml"
        marker_file.touch()

        # Mock getcwd to return the temp dir
        mock_getcwd.return_value = str(tmp_path)

        # Call without start_dir
        result = get_project_root()

        assert result == str(tmp_path)
        mock_getcwd.assert_called_once()

    def test_get_project_root_fallback(self):
        """Test fallback behavior when no marker is found up to the root."""
        # Use a path that will reach the root without finding markers
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False

            # We use a path that is likely to exist but not have markers
            result = get_project_root(start_dir="/tmp")

            # The fallback logic is: 3 levels up from path.py's directory
            # We calculate what we expect based on the actual file location
            import pipe.core.utils.path

            path_file = pipe.core.utils.path.__file__
            script_dir = os.path.dirname(os.path.abspath(path_file))
            expected_fallback = os.path.abspath(
                os.path.join(script_dir, "..", "..", "..")
            )

            assert result == expected_fallback
