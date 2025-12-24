"""
Unit tests for the path utility module.
"""

import os
from unittest.mock import patch

from pipe.core.utils.path import get_project_root


class TestGetProjectRoot:
    """Tests for the get_project_root function."""

    def test_find_root_with_git_marker(self, tmp_path):
        """Test finding the project root with a .git directory marker."""
        # Setup: Create a .git directory in tmp_path
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Execute
        root = get_project_root(start_dir=str(tmp_path))

        # Verify
        assert root == str(tmp_path.resolve())

    def test_find_root_with_pyproject_marker(self, tmp_path):
        """Test finding the project root with a pyproject.toml file marker."""
        # Setup: Create a pyproject.toml file in tmp_path
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.poetry]")

        # Execute
        root = get_project_root(start_dir=str(tmp_path))

        # Verify
        assert root == str(tmp_path.resolve())

    def test_find_root_from_subdirectory(self, tmp_path):
        """Test searching upward from a deep subdirectory."""
        # Setup:
        # tmp_path/ (.git marker here)
        # └── a/
        #     └── b/
        #         └── c/ (start here)
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        start_dir = tmp_path / "a" / "b" / "c"
        start_dir.mkdir(parents=True)

        # Execute
        root = get_project_root(start_dir=str(start_dir))

        # Verify
        assert root == str(tmp_path.resolve())

    def test_find_root_with_custom_marker(self, tmp_path):
        """Test finding the root with a custom marker name."""
        # Setup: Create a custom marker file
        marker_name = "my_special_marker.txt"
        marker_file = tmp_path / marker_name
        marker_file.write_text("root")

        # Execute
        root = get_project_root(start_dir=str(tmp_path), markers=(marker_name,))

        # Verify
        assert root == str(tmp_path.resolve())

    def test_default_start_dir_is_cwd(self, tmp_path, monkeypatch):
        """Test that get_project_root uses CWD if start_dir is None."""
        # Setup: Create a marker in tmp_path and change CWD to it
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        # Execute (no start_dir provided)
        root = get_project_root()

        # Verify
        assert root == str(tmp_path.resolve())

        def test_fallback_when_no_marker_found(self, tmp_path):
            """Test the fallback logic when no marker is found up to the FS root."""

            # Setup: Start from an empty directory, searching for a non-existent marker

            start_dir = tmp_path / "empty"

            start_dir.mkdir()

            # Execute with a marker that definitely won't be found

            root = get_project_root(
                start_dir=str(start_dir), markers=("non_existent_marker_xyz",)
            )

            # Verify fallback: 3 levels up from src/pipe/core/utils/path.py

            # which should be src/

            # Let's dynamically calculate what it SHOULD be based on the source location

            import pipe.core.utils.path

            source_file = pipe.core.utils.path.__file__

            script_dir = os.path.dirname(os.path.abspath(source_file))

            expected_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

            assert root == expected_root

    def test_reached_filesystem_root(self, tmp_path):
        """Test behavior when the loop reaches the filesystem root."""
        # We patch os.path.dirname to return the same directory, simulating FS root
        start_dir = str(tmp_path)

        with patch("os.path.dirname") as mock_dirname:
            # Simulate FS root by returning the same path
            mock_dirname.return_value = start_dir

            # Execute
            root = get_project_root(start_dir=start_dir, markers=("none",))

            # Verify it hit the break and used fallback
            import pipe.core.utils.path

            source_file = pipe.core.utils.path.__file__
            script_dir = os.path.dirname(os.path.abspath(source_file))
            expected_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

            assert root == expected_root
            mock_dirname.assert_called()
