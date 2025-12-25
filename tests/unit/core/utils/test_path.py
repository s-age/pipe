import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_finds_git_marker(self, tmp_path):
        """Test that .git marker is found from a subdirectory."""
        # Setup:
        # tmp_path/
        # ├── .git/
        # └── sub/
        #     └── dir/
        root_dir = tmp_path
        (root_dir / ".git").mkdir()
        sub_dir = root_dir / "sub" / "dir"
        sub_dir.mkdir(parents=True)

        result = get_project_root(start_dir=str(sub_dir))
        assert os.path.abspath(result) == os.path.abspath(str(root_dir))

    def test_get_project_root_finds_pyproject_marker(self, tmp_path):
        """Test that pyproject.toml marker is found."""
        # Setup:
        # tmp_path/
        # ├── pyproject.toml
        # └── sub/
        root_dir = tmp_path
        (root_dir / "pyproject.toml").touch()
        sub_dir = root_dir / "sub"
        sub_dir.mkdir()

        result = get_project_root(start_dir=str(sub_dir))
        assert os.path.abspath(result) == os.path.abspath(str(root_dir))

    def test_get_project_root_custom_markers(self, tmp_path):
        """Test that custom markers are recognized."""
        # Setup:
        # tmp_path/
        # └── my_marker.txt
        root_dir = tmp_path
        (root_dir / "my_marker.txt").touch()
        markers = ("my_marker.txt",)

        result = get_project_root(start_dir=str(root_dir), markers=markers)
        assert os.path.abspath(result) == os.path.abspath(str(root_dir))

    def test_get_project_root_from_cwd(self, tmp_path):
        """Test that search starts from cwd when start_dir is None."""
        root_dir = tmp_path
        (root_dir / ".git").mkdir()
        sub_dir = root_dir / "sub"
        sub_dir.mkdir()

        with patch("os.getcwd", return_value=str(sub_dir)):
            result = get_project_root(start_dir=None)
            assert os.path.abspath(result) == os.path.abspath(str(root_dir))

    def test_get_project_root_fallback(self, tmp_path):
        """Test fallback logic when no markers are found."""
        # Use a temporary directory as root-like environment
        # and mock os.path.exists to always return False for markers
        with patch("os.path.exists", return_value=False):
            result = get_project_root(start_dir=str(tmp_path))

            # The fallback logic is script-relative:
            # os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
            # script_dir is src/pipe/core/utils/
            # .../src/pipe/core/utils/.. -> .../src/pipe/core
            # .../src/pipe/core/.. -> .../src/pipe
            # .../src/pipe/.. -> .../src

            # Verify it's an absolute path
            assert os.path.isabs(result)
            # And it should contain 'src' (given our project structure)
            assert result.endswith("src")
