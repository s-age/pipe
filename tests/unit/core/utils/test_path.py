"""Tests for the path utility module."""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Test get_project_root function."""

    def test_find_root_with_git_marker(self, tmp_path):
        """Test finding project root with .git marker."""
        # Create a mock project structure
        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        subdir = project_root / "src" / "pipe"
        subdir.mkdir(parents=True)

        # Test finding root from subdir
        root = get_project_root(start_dir=str(subdir))
        assert root == os.path.abspath(str(project_root))

    def test_find_root_with_pyproject_marker(self, tmp_path):
        """Test finding project root with pyproject.toml marker."""
        project_root = tmp_path / "another_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").touch()

        subdir = project_root / "tests" / "unit"
        subdir.mkdir(parents=True)

        root = get_project_root(start_dir=str(subdir))
        assert root == os.path.abspath(str(project_root))

    def test_find_root_custom_marker(self, tmp_path):
        """Test finding project root with a custom marker."""
        project_root = tmp_path / "custom_project"
        project_root.mkdir()
        (project_root / "my_marker.txt").touch()

        subdir = project_root / "subdir"
        subdir.mkdir()

        root = get_project_root(start_dir=str(subdir), markers=("my_marker.txt",))
        assert root == os.path.abspath(str(project_root))

    def test_start_dir_none_uses_getcwd(self, tmp_path, monkeypatch):
        """Test that start_dir=None uses current working directory."""
        project_root = tmp_path / "cwd_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").touch()

        # Mock os.getcwd to return our project_root
        monkeypatch.setattr(os, "getcwd", lambda: str(project_root))

        root = get_project_root(start_dir=None)
        assert root == os.path.abspath(str(project_root))

    def test_fallback_when_no_marker_found(self):
        """Test fallback logic when no markers are found up to filesystem root."""
        # Mock os.path.exists to always return False to force reaching root
        # Mock os.path.dirname and os.path.abspath to simulate behavior

        orig_dirname = os.path.dirname
        orig_abspath = os.path.abspath

        with patch("os.path.exists", return_value=False):
            with patch("os.path.dirname") as mock_dirname:
                with patch("os.path.abspath") as mock_abspath:
                    # We need to simulate reaching the root "/"
                    # Let's mock it to return the same path if we are at "/root"
                    mock_dirname.side_effect = lambda x: (
                        x if x == "/root" else orig_dirname(x)
                    )

                    # Now the fallback part:
                    # script_dir = os.path.dirname(os.path.abspath(__file__))
                    def custom_abspath(x):
                        # Catch both relative and absolute paths for the script
                        if "src/pipe/core/utils/path.py" in str(x):
                            return "/mock/project/src/pipe/core/utils/path.py"
                        return orig_abspath(x)

                    mock_abspath.side_effect = custom_abspath

                    root = get_project_root(start_dir="/root/a/b")

                    # script_dir = dirname("/mock/project/src/pipe/core/utils/path.py")
                    # -> "/mock/project/src/pipe/core/utils"
                    # return abspath(join(script_dir, "..", "..", ".."))
                    # 1. .. -> /mock/project/src/pipe/core
                    # 2. .. -> /mock/project/src/pipe
                    # 3. .. -> /mock/project/src

                    assert root == "/mock/project/src"

    def test_find_root_at_start_dir(self, tmp_path):
        """Test finding project root when start_dir itself contains the marker."""
        (tmp_path / "pyproject.toml").touch()
        root = get_project_root(start_dir=str(tmp_path))
        assert root == os.path.abspath(str(tmp_path))
