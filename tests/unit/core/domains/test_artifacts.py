from pipe.core.domains.artifacts import build_artifacts_from_data
from pipe.core.models.artifact import Artifact


class TestBuildArtifactsFromData:
    """Test build_artifacts_from_data domain logic."""

    def test_build_artifacts_from_data_empty(self) -> None:
        """Test building artifacts from an empty list."""
        result = build_artifacts_from_data([])
        assert result == []

    def test_build_artifacts_from_data_single(self) -> None:
        """Test building a single artifact."""
        data = [("test.txt", "hello world")]
        result = build_artifacts_from_data(data)

        assert len(result) == 1
        assert isinstance(result[0], Artifact)
        assert result[0].path == "test.txt"
        assert result[0].contents == "hello world"

    def test_build_artifacts_from_data_multiple(self) -> None:
        """Test building multiple artifacts."""
        data = [
            ("file1.py", "print('hi')"),
            ("file2.md", "# Title"),
        ]
        result = build_artifacts_from_data(data)

        assert len(result) == 2
        assert result[0].path == "file1.py"
        assert result[0].contents == "print('hi')"
        assert result[1].path == "file2.md"
        assert result[1].contents == "# Title"

    def test_build_artifacts_from_data_with_none_content(self) -> None:
        """Test building an artifact where content is None (e.g., file not found)."""
        data = [("missing.txt", None)]
        result = build_artifacts_from_data(data)

        assert len(result) == 1
        assert result[0].path == "missing.txt"
        assert result[0].contents is None

    def test_build_artifacts_from_data_immutability(self) -> None:
        """Test that the input list is not mutated."""
        data = [("file.txt", "content")]
        data_copy = data.copy()
        build_artifacts_from_data(data)
        assert data == data_copy
