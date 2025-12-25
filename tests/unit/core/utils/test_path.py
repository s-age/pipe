import os

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_finds_marker_in_current_dir(self, tmp_path):
        """Test finding a marker in the starting directory."""
        # Setup: Create a marker file
        marker = "pyproject.toml"
        (tmp_path / marker).touch()

        root = get_project_root(start_dir=str(tmp_path), markers=(marker,))
        assert root == str(tmp_path)

    def test_finds_marker_in_parent_dir(self, tmp_path):
        """Test finding a marker in a parent directory."""
        # Setup: Create structure tmp_path/subdir, with marker in tmp_path
        marker = ".git"
        (tmp_path / marker).mkdir()  # .git is usually a dir
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        root = get_project_root(start_dir=str(subdir), markers=(marker,))
        assert root == str(tmp_path)

    def test_finds_marker_several_levels_up(self, tmp_path):
        """Test finding a marker several levels up."""
        # Setup: tmp_path/a/b/c, with marker in tmp_path
        marker = "pyproject.toml"
        (tmp_path / marker).touch()
        deep_dir = tmp_path / "a" / "b" / "c"
        deep_dir.mkdir(parents=True)

        root = get_project_root(start_dir=str(deep_dir), markers=(marker,))
        assert root == str(tmp_path)

    def test_custom_markers(self, tmp_path):
        """Test searching for custom markers."""
        marker = "custom_marker.txt"
        (tmp_path / marker).touch()

        root = get_project_root(start_dir=str(tmp_path), markers=(marker,))
        assert root == str(tmp_path)

    def test_precedence_of_markers(self, tmp_path):
        """Test that the first marker encountered is returned."""
        # Setup: tmp_path/subdir, marker1 in tmp_path, marker2 in subdir
        marker1 = "marker1"
        marker2 = "marker2"
        (tmp_path / marker1).touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / marker2).touch()

        # Start from subdir, should find marker2 first
        root = get_project_root(start_dir=str(subdir), markers=(marker1, marker2))
        assert root == str(subdir)

    def test_default_start_dir(self, tmp_path, monkeypatch):
        """Test when start_dir is None, it uses CWD."""
        marker = "pyproject.toml"
        (tmp_path / marker).touch()

        # Use monkeypatch to change CWD
        monkeypatch.chdir(tmp_path)

        root = get_project_root(start_dir=None, markers=(marker,))
        # Since we are in tmp_path, it should find it there
        assert root == str(tmp_path)

    def test_fallback_logic(self, monkeypatch):
        """Test the fallback logic when no markers are found."""
        # Mock os.path.exists to always return False to simulate no markers found
        monkeypatch.setattr(os.path, "exists", lambda x: False)

        # Mock os.path.dirname to reach the root quickly
        def mock_dirname(path):
            # If we are already at our mock root, return it to stop the loop
            if path == "/mock/root":
                return path
            return "/mock/root"

        monkeypatch.setattr(os.path, "dirname", mock_dirname)
        monkeypatch.setattr(
            os.path, "abspath", lambda x: x if x.startswith("/") else f"/{x}"
        )

        root = get_project_root(start_dir="/mock/root/subdir")

        # Fallback path is calculated from the script location
        import pipe.core.utils.path as path_module

        script_dir = os.path.dirname(os.path.abspath(path_module.__file__))
        expected_fallback = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

        assert root == expected_fallback
