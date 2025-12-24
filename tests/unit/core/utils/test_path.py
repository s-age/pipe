import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_with_marker_in_start_dir(self, tmp_path):
        """Test finding marker in the starting directory."""
        marker = ".git"
        (tmp_path / marker).mkdir()

        # We use str(tmp_path.resolve()) to ensure comparison with absolute path
        root = get_project_root(start_dir=str(tmp_path), markers=(marker,))
        assert root == str(tmp_path.resolve())

    def test_get_project_root_with_marker_in_parent_dir(self, tmp_path):
        """Test finding marker in the parent directory."""
        marker = "pyproject.toml"
        (tmp_path / marker).touch()
        subdir = tmp_path / "a" / "b" / "c"
        subdir.mkdir(parents=True)

        root = get_project_root(start_dir=str(subdir), markers=(marker,))
        assert root == str(tmp_path.resolve())

    def test_get_project_root_default_markers(self, tmp_path):
        """Test with default markers (.git)."""
        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        root = get_project_root(start_dir=str(subdir))
        assert root == str(tmp_path.resolve())

    def test_get_project_root_default_start_dir(self, tmp_path, monkeypatch):
        """Test using current working directory as default start_dir."""
        (tmp_path / "pyproject.toml").touch()
        subdir = tmp_path / "current"
        subdir.mkdir()

        # Use monkeypatch to safely change CWD
        monkeypatch.chdir(subdir)
        root = get_project_root()
        assert root == str(tmp_path.resolve())

    def test_get_project_root_fallback(self, tmp_path):
        """Test fallback logic when no markers are found."""
        # Mock os.path.exists locally in the path module to always return False
        # for any marker check inside the loop, forcing it to reach the filesystem root.
        with patch("pipe.core.utils.path.os.path.exists", return_value=False):
            root = get_project_root(start_dir=str(tmp_path))

            # Fallback is 3 levels up from the location of pipe/core/utils/path.py
            import pipe.core.utils.path as path_module

            script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
            expected = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
            assert root == expected

    def test_get_project_root_custom_markers(self, tmp_path):
        """Test with custom marker list."""
        marker = "custom_marker_file"
        (tmp_path / marker).touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Should find custom marker
        root = get_project_root(start_dir=str(subdir), markers=(marker,))
        assert root == str(tmp_path.resolve())

        # Should NOT find if custom marker is not in markers list
        # We wrap the real os.path.exists to avoid affecting other parts of the system
        real_exists = os.path.exists

        def side_effect(path):
            # If checking for standard markers that might exist in the real FS
            # above the tmp_path, we return False to force the search to continue.
            if any(m in os.path.basename(path) for m in [".git", "pyproject.toml"]):
                return False
            return real_exists(path)

        with patch("pipe.core.utils.path.os.path.exists", side_effect=side_effect):
            root = get_project_root(start_dir=str(subdir), markers=("other_marker",))

            import pipe.core.utils.path as path_module

            script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
            expected = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
            assert root == expected

    def test_get_project_root_reaches_fs_root(self):
        """Test break condition when reaching filesystem root."""
        # Mock os.path.dirname and os.path.exists locally in the path module
        with patch("pipe.core.utils.path.os.path.dirname") as mock_dirname:
            mock_dirname.return_value = "/mock_root"
            with patch("pipe.core.utils.path.os.path.exists", return_value=False):
                # start_dir is same as dirname return value to trigger break immediately
                root = get_project_root(start_dir="/mock_root")

                # Should hit fallback
                import pipe.core.utils.path as path_module

                script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
                expected = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
                assert root == expected
