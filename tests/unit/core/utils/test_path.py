"""
Unit tests for path utility functions.
"""

import os

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Test get_project_root function."""

    def test_find_root_with_git_in_current_dir(self, tmp_path, monkeypatch):
        """Test finding root when .git exists in the current directory."""
        # Setup: Create a .git directory in tmp_path
        (tmp_path / ".git").mkdir()

        # Action: Call get_project_root from tmp_path
        monkeypatch.chdir(tmp_path)
        root = get_project_root()

        # Assert: Should return tmp_path as the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_find_root_with_pyproject_in_parent_dir(self, tmp_path):
        """Test finding root when pyproject.toml exists in the parent directory."""
        # Setup: Create pyproject.toml in tmp_path and a subdirectory
        (tmp_path / "pyproject.toml").touch()
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)

        # Action: Call get_project_root with start_dir=subdir
        root = get_project_root(start_dir=str(subdir))

        # Assert: Should return tmp_path as the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_find_root_with_custom_markers(self, tmp_path):
        """Test finding root using custom marker files."""
        # Setup: Create a custom marker in tmp_path
        (tmp_path / "root.marker").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Action: Call get_project_root with custom markers
        root = get_project_root(start_dir=str(subdir), markers=("root.marker",))

        # Assert: Should return tmp_path as the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_fallback_when_no_markers_found(self, tmp_path, monkeypatch):
        """Test fallback behavior when no markers are found up to filesystem root."""
        # Setup: A directory without any markers
        monkeypatch.chdir(tmp_path)

        # We need to simulate reaching the filesystem root.
        # However, it's safer to just check if the fallback logic is executed
        # when markers are not found.
        # The fallback logic uses __file__ which refers to src/pipe/core/utils/path.py.
        # It goes up 3 levels: utils -> core -> pipe -> src -> project_root (usually)
        # Actually: path.py is in src/pipe/core/utils/
        # dirname(abspath(__file__)) is src/pipe/core/utils
        # .. -> src/pipe/core
        # .. -> src/pipe
        # .. -> src
        # Wait, the code says:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # return os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
        # utils -> (..) core -> (..) pipe -> (..) src
        # So it returns 'src' directory (if it's in src/pipe/core/utils/path.py)

        root = get_project_root(markers=("non_existent_marker",))

        # Assert: The result should be absolute and exist
        assert os.path.isabs(root)
        assert os.path.exists(root)

        # Check against the expected fallback calculation
        import pipe.core.utils.path as path_module

        script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
        expected_fallback = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
        assert root == expected_fallback

    def test_start_dir_as_file_path(self, tmp_path):
        """Test when start_dir is actually a path to a file."""
        # Setup: Create .git in tmp_path and a file in a subdirectory
        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        file_path = subdir / "test.txt"
        file_path.touch()

        # Action: Call get_project_root with path to file
        root = get_project_root(start_dir=str(file_path))

        # Assert: Should still find the root
        assert os.path.abspath(root) == os.path.abspath(str(tmp_path))

    def test_multiple_markers_existence(self, tmp_path):
        """Test priority or finding any of the multiple markers."""
        # Setup: Create both markers at different levels
        (tmp_path / "pyproject.toml").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / ".git").mkdir()

        # Action: Search from subdir
        # It should find .git in subdir first
        root = get_project_root(start_dir=str(subdir))
        assert os.path.abspath(root) == os.path.abspath(str(subdir))

        # Search from a deeper nested dir
        nested = subdir / "nested"
        nested.mkdir()
        root = get_project_root(start_dir=str(nested))
        assert os.path.abspath(root) == os.path.abspath(str(subdir))
