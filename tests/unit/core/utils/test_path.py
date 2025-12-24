import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_current_dir(self, tmp_path):
        """Test finding root when marker is in the current directory."""
        marker = "pyproject.toml"
        (tmp_path / marker).touch()

        result = get_project_root(start_dir=str(tmp_path))
        assert result == str(tmp_path)

    def test_get_project_root_parent_dir(self, tmp_path):
        """Test finding root when marker is in a parent directory."""
        root_dir = tmp_path / "project_root"
        root_dir.mkdir()
        (root_dir / ".git").mkdir()

        sub_dir = root_dir / "src" / "pipe"
        sub_dir.mkdir(parents=True)

        result = get_project_root(start_dir=str(sub_dir))
        assert result == str(root_dir)

    def test_get_project_root_multiple_markers(self, tmp_path):
        """Test finding root when multiple markers are present."""
        (tmp_path / ".git").mkdir()
        (tmp_path / "pyproject.toml").touch()

        result = get_project_root(start_dir=str(tmp_path))
        assert result == str(tmp_path)

    def test_get_project_root_custom_markers(self, tmp_path):
        """Test finding root with custom markers."""
        marker = "root_marker.txt"
        (tmp_path / marker).touch()

        result = get_project_root(start_dir=str(tmp_path), markers=(marker,))
        assert result == str(tmp_path)

    def test_get_project_root_default_cwd(self, tmp_path):
        """Test using current working directory as default start_dir."""
        marker = "pyproject.toml"
        (tmp_path / marker).touch()

        with patch("os.getcwd", return_value=str(tmp_path)):
            # os.path.abspath(os.getcwd()) will be called
            result = get_project_root()
            assert result == str(tmp_path)

    def test_get_project_root_fallback(self):
        """Test fallback logic when no markers are found."""
        # Mock os.path.exists to always return False to trigger fallback
        with patch("os.path.exists", return_value=False):
            # Mock __file__ in the module to a known path
            # src/pipe/core/utils/path.py
            mock_file = "/project/src/pipe/core/utils/path.py"
            with patch("pipe.core.utils.path.__file__", mock_file):
                # Use real abspath for normalization but mock it
                # to handle our virtual paths
                original_abspath = os.path.abspath

                def mock_abspath(path):
                    if path.startswith("/project"):
                        # Use normpath to simulate abspath
                        # normalization on virtual paths
                        return os.path.normpath(path)
                    return original_abspath(path)

                with patch("os.path.abspath", side_effect=mock_abspath):
                    result = get_project_root(start_dir="/some/other/path")

                    # script_dir = dirname(abspath(mock_file))
                    #            = /project/src/pipe/core/utils
                    # fallback = script_dir/../../.. = /project/src
                    expected = "/project/src"
                    assert result == expected

    def test_get_project_root_reach_root_no_marker(self, tmp_path):
        """Test behavior when reaching filesystem root without finding any marker."""
        start_dir = tmp_path / "a" / "b"
        start_dir.mkdir(parents=True)

        # Mock os.path.exists to return False only for paths under tmp_path
        # to ensure it doesn't find real .git or pyproject.toml in parent dirs
        # if the test is run inside a git repo.
        original_exists = os.path.exists

        def mock_exists(p):
            if str(p).startswith(str(tmp_path)):
                return False
            return original_exists(p)

        # Mock dirname to stop at tmp_path to simulate filesystem root for the loop
        original_dirname = os.path.dirname

        def mock_dirname(p):
            if p == str(tmp_path):
                return p
            return original_dirname(p)

        with patch("os.path.exists", side_effect=mock_exists):
            with patch("os.path.dirname", side_effect=mock_dirname):
                mock_script_path = str(tmp_path / "x" / "y" / "z" / "script.py")
                with patch("pipe.core.utils.path.__file__", mock_script_path):
                    # Use normpath for normalization
                    with patch("os.path.abspath", side_effect=os.path.normpath):
                        result = get_project_root(start_dir=str(start_dir))
                        # Should hit the fallback
                        # script_dir = tmp_path/x/y/z
                        # fallback = script_dir/../../.. = tmp_path
                        assert result == str(tmp_path)
