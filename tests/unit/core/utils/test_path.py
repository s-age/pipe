"""
Unit tests for pipe.core.utils.path.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    @patch("os.path.exists")
    @patch("os.path.abspath")
    def test_get_project_root_found_in_start_dir(self, mock_abspath, mock_exists):
        """Test finding marker in the starting directory."""
        mock_abspath.side_effect = lambda x: x
        # Marker exists in the start_dir
        mock_exists.side_effect = lambda p: p == "/path/to/project/.git"

        result = get_project_root(start_dir="/path/to/project")

        assert result == "/path/to/project"
        assert mock_exists.call_count >= 1

    @patch("os.path.exists")
    @patch("os.path.abspath")
    @patch("os.path.dirname")
    def test_get_project_root_found_in_parent(
        self, mock_dirname, mock_abspath, mock_exists
    ):
        """Test finding marker in the parent directory."""
        mock_abspath.side_effect = lambda x: x
        mock_dirname.side_effect = {
            "/path/to/project/subdir": "/path/to/project",
            "/path/to/project": "/path/to",
        }.get

        # .git only exists in /path/to/project
        def side_effect_exists(path):
            return path == "/path/to/project/.git"

        mock_exists.side_effect = side_effect_exists

        result = get_project_root(start_dir="/path/to/project/subdir")

        assert result == "/path/to/project"

    @patch("os.getcwd")
    @patch("os.path.exists")
    @patch("os.path.abspath")
    def test_get_project_root_default_start_dir(
        self, mock_abspath, mock_exists, mock_getcwd
    ):
        """Test using default start_dir (os.getcwd)."""
        mock_getcwd.return_value = "/current/working/dir"
        mock_abspath.side_effect = lambda x: x

        def side_effect_exists(p):
            return p == "/current/working/dir/pyproject.toml"

        mock_exists.side_effect = side_effect_exists

        result = get_project_root()

        assert result == "/current/working/dir"
        mock_getcwd.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.abspath")
    def test_get_project_root_custom_markers(self, mock_abspath, mock_exists):
        """Test using custom marker files."""
        mock_abspath.side_effect = lambda x: x
        custom_markers = ("requirements.txt", "setup.py")
        mock_exists.side_effect = lambda p: p == "/project/setup.py"

        result = get_project_root(start_dir="/project", markers=custom_markers)

        assert result == "/project"

    @patch("os.path.exists")
    @patch("os.path.abspath")
    @patch("os.path.dirname")
    def test_get_project_root_fallback(self, mock_dirname, mock_abspath, mock_exists):
        """Test fallback logic when no markers are found up to the root."""
        # Setup mocks to reach filesystem root
        mock_abspath.side_effect = (
            lambda x: x if not x.endswith("..") else "/fallback/root"
        )

        # Simulate reaching filesystem root: dirname("/") == "/"
        def side_effect_dirname_root(path):
            if path == "/":
                return "/"
            return os.path.dirname(path)

        mock_dirname.side_effect = side_effect_dirname_root

        # No markers exist anywhere
        mock_exists.return_value = False

        # We need to control __file__ indirectly by mocking abspath and dirname
        def abspath_side_effect(path):
            if path.endswith("path.py"):
                return "/root/src/pipe/core/utils/path.py"
            if ".." in path:
                return "/root"
            return path

        def dirname_side_effect(p):
            if p.endswith("path.py"):
                return "/root/src/pipe/core/utils"
            return "/"

        mock_abspath.side_effect = abspath_side_effect
        mock_dirname.side_effect = dirname_side_effect

        result = get_project_root(start_dir="/some/other/place")

        # Expected: script_dir is /root/src/pipe/core/utils
        # join(script_dir, "..", "..", "..") -> /root
        assert result == "/root"
