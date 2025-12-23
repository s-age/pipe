import pytest
from pipe.core.repositories.procedure_repository import ProcedureRepository


@pytest.fixture
def repository(tmp_path):
    """Create a ProcedureRepository with temporary directory."""
    return ProcedureRepository(procedures_root_dir=str(tmp_path))


class TestProcedureRepositoryGetAllProcedureOptions:
    """Test ProcedureRepository.get_all_procedure_options() method."""

    def test_get_all_procedure_options_empty(self, repository):
        """Test returning empty list when no procedure files exist."""
        options = repository.get_all_procedure_options()
        assert options == []

    def test_get_all_procedure_options_flat(self, repository, tmp_path):
        """Test finding procedure files in the root directory."""
        # Create some markdown files
        (tmp_path / "test1.md").write_text("content1")
        (tmp_path / "test2.md").write_text("content2")

        options = repository.get_all_procedure_options()

        assert len(options) == 2
        assert options[0].label == "test1"
        assert options[0].value == "procedures/test1.md"
        assert options[1].label == "test2"
        assert options[1].value == "procedures/test2.md"

    def test_get_all_procedure_options_nested(self, repository, tmp_path):
        """Test finding procedure files in nested directories."""
        # Create nested directories and files
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.md").write_text("nested content")
        (tmp_path / "root.md").write_text("root content")

        options = repository.get_all_procedure_options()

        assert len(options) == 2
        # Sorted by label: "root", "subdir/nested"
        assert options[0].label == "root"
        assert options[0].value == "procedures/root.md"
        assert options[1].label == "subdir/nested"
        assert options[1].value == "procedures/subdir/nested.md"

    def test_get_all_procedure_options_ignore_non_md(self, repository, tmp_path):
        """Test that non-markdown files are ignored."""
        (tmp_path / "test.md").write_text("md content")
        (tmp_path / "test.txt").write_text("text content")
        (tmp_path / "test.py").write_text("python content")

        options = repository.get_all_procedure_options()

        assert len(options) == 1
        assert options[0].label == "test"
        assert options[0].value == "procedures/test.md"

    def test_get_all_procedure_options_sorting(self, repository, tmp_path):
        """Test that options are returned sorted by label."""
        (tmp_path / "c.md").write_text("c")
        (tmp_path / "a.md").write_text("a")
        (tmp_path / "b.md").write_text("b")

        options = repository.get_all_procedure_options()

        assert len(options) == 3
        assert options[0].label == "a"
        assert options[1].label == "b"
        assert options[2].label == "c"

    def test_get_all_procedure_options_deeply_nested(self, repository, tmp_path):
        """Test finding procedure files in deeply nested directories."""
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (deep / "deep.md").write_text("deep content")

        options = repository.get_all_procedure_options()

        assert len(options) == 1
        assert options[0].label == "a/b/c/deep"
        assert options[0].value == "procedures/a/b/c/deep.md"

    def test_get_all_procedure_options_with_multiple_dots(self, repository, tmp_path):
        """Test finding files with multiple dots in the filename."""
        (tmp_path / "my.custom.procedure.md").write_text("content")

        options = repository.get_all_procedure_options()

        assert len(options) == 1
        # os.path.splitext only removes the last extension
        assert options[0].label == "my.custom.procedure"
        assert options[0].value == "procedures/my.custom.procedure.md"

    def test_get_all_procedure_options_with_hidden_files(self, repository, tmp_path):
        """Test finding hidden markdown files."""
        (tmp_path / ".hidden.md").write_text("hidden")
        (tmp_path / "normal.md").write_text("normal")

        options = repository.get_all_procedure_options()

        assert len(options) == 2
        # Sorting: ".hidden" comes before "normal"
        assert options[0].label == ".hidden"
        assert options[1].label == "normal"

    def test_get_all_procedure_options_cross_platform(self, repository, tmp_path):
        """Test that path separators are always normalized to '/'."""
        sub = tmp_path / "path" / "to"
        sub.mkdir(parents=True)
        (sub / "file.md").write_text("content")

        options = repository.get_all_procedure_options()

        assert len(options) == 1
        # Even on Windows, the label and value should use '/'
        assert options[0].label == "path/to/file"
        assert options[0].value == "procedures/path/to/file.md"
