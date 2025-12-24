"""Unit tests for script_validator utility."""

import os
from pathlib import Path

import pytest
from pipe.core.utils.script_validator import ScriptValidationError, validate_script_path


@pytest.fixture
def tmp_project_root(tmp_path: Path) -> Path:
    """Create a temporary project root with a scripts directory."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    return tmp_path


class TestValidateScriptPath:
    """Tests for validate_script_path function."""

    def test_validate_valid_script(self, tmp_project_root: Path):
        """Test validating a valid script in the scripts directory."""
        script_name = "test_script.sh"
        script_file = tmp_project_root / "scripts" / script_name
        script_file.write_text("echo hello")

        result = validate_script_path(script_name, str(tmp_project_root))

        assert result.absolute() == script_file.resolve()
        assert result.name == script_name

    def test_validate_valid_script_in_subdirectory(self, tmp_project_root: Path):
        """Test validating a valid script in a subdirectory of scripts/."""
        sub_dir = tmp_project_root / "scripts" / "python"
        sub_dir.mkdir()
        script_name = "python/test_script.py"
        script_file = tmp_project_root / "scripts" / "python" / "test_script.py"
        script_file.write_text("print('hello')")

        result = validate_script_path(script_name, str(tmp_project_root))

        assert result.absolute() == script_file.resolve()

    def test_raises_error_if_script_contains_parent_dir(self, tmp_project_root: Path):
        """Test that scripts containing '..' are rejected immediately."""
        script_name = "../etc/passwd"

        with pytest.raises(
            ScriptValidationError, match="Invalid characters in script name"
        ):
            validate_script_path(script_name, str(tmp_project_root))

    def test_raises_error_if_script_contains_backslash(self, tmp_project_root: Path):
        """Test that scripts containing '\\' are rejected immediately."""
        script_name = "subdir\\test.sh"

        with pytest.raises(
            ScriptValidationError, match="Invalid characters in script name"
        ):
            validate_script_path(script_name, str(tmp_project_root))

    def test_raises_error_if_resolves_outside_scripts_dir(self, tmp_project_root: Path):
        """Test that scripts resolving outside the scripts directory are rejected."""
        # Create a file outside scripts/
        outside_file = tmp_project_root / "outside.sh"
        outside_file.write_text("echo outside")

        # Although we block ".." in script_name, we test the is_relative_to check
        # by mocking or finding a way to resolve outside if possible.
        # Since we block "..", direct traversal is hard via script_name.
        # But resolve() handles symlinks too.

        # Create a symlink inside scripts pointing outside
        symlink_path = tmp_project_root / "scripts" / "malicious.sh"
        try:
            os.symlink(outside_file, symlink_path)
        except OSError:
            pytest.skip("Symlinks not supported on this platform")

        with pytest.raises(ScriptValidationError, match="Path traversal detected"):
            validate_script_path("malicious.sh", str(tmp_project_root))

    def test_raises_error_if_not_found(self, tmp_project_root: Path):
        """Test that FileNotFoundError is raised if the script doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Script not found"):
            validate_script_path("non_existent.sh", str(tmp_project_root))

    def test_raises_error_if_directory(self, tmp_project_root: Path):
        """Test that ScriptValidationError is raised if the path is a directory."""
        dir_name = "sub_directory"
        (tmp_project_root / "scripts" / dir_name).mkdir()

        with pytest.raises(ScriptValidationError, match="Not a regular file"):
            validate_script_path(dir_name, str(tmp_project_root))

    def test_normalize_path(self, tmp_project_root: Path):
        """Test that the returned path is normalized."""
        script_name = "test.sh"
        script_file = tmp_project_root / "scripts" / script_name
        script_file.write_text("test")

        # Using redundant slashes or dots that resolve() should clean up
        # Note: script_name itself cannot have ".." as per implementation
        result = validate_script_path(script_name, str(tmp_project_root))

        assert str(result) == str(script_file.resolve())
