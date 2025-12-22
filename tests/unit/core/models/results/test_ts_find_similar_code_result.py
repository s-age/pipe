import pytest
from pipe.core.models.results.ts_find_similar_code_result import (
    SimilarCodeMatch,
    TSFindSimilarCodeResult,
)
from pydantic import ValidationError


class TestSimilarCodeMatch:
    """Tests for SimilarCodeMatch model."""

    def test_valid_creation(self):
        """Test creating a valid SimilarCodeMatch."""
        match = SimilarCodeMatch(
            file="src/utils.ts",
            symbol="processData",
            similarity=0.95,
            snippet="function processData() { ... }",
        )
        assert match.file == "src/utils.ts"
        assert match.symbol == "processData"
        assert match.similarity == 0.95
        assert match.snippet == "function processData() { ... }"

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SimilarCodeMatch(file="src/utils.ts")

        error_msg = str(exc_info.value)
        assert "symbol" in error_msg
        assert "similarity" in error_msg
        assert "snippet" in error_msg

    def test_serialization_camel_case(self):
        """Test serialization to camelCase."""
        match = SimilarCodeMatch(
            file="src/utils.ts", symbol="processData", similarity=0.95, snippet="code"
        )
        dumped = match.model_dump(by_alias=True)
        # These fields are single words so snake_case == camelCase
        assert dumped["file"] == "src/utils.ts"
        assert dumped["symbol"] == "processData"
        assert dumped["similarity"] == 0.95
        assert dumped["snippet"] == "code"


class TestTSFindSimilarCodeResult:
    """Tests for TSFindSimilarCodeResult model."""

    def test_valid_creation_defaults(self):
        """Test creating a result with defaults."""
        result = TSFindSimilarCodeResult()
        assert result.base_snippet is None
        assert result.base_type_definitions is None
        assert result.matches is None
        assert result.error is None

    def test_valid_creation_full(self):
        """Test creating a result with all fields."""
        match = SimilarCodeMatch(
            file="src/foo.ts", symbol="Foo", similarity=1.0, snippet="class Foo {}"
        )
        result = TSFindSimilarCodeResult(
            base_snippet="class Base {}",
            base_type_definitions={"Base": "type"},
            matches=[match],
            error=None,
        )
        assert result.base_snippet == "class Base {}"
        assert result.base_type_definitions == {"Base": "type"}
        assert len(result.matches) == 1
        assert result.matches[0].file == "src/foo.ts"
        assert result.error is None

    def test_serialization_camel_case(self):
        """Test serialization to camelCase."""
        result = TSFindSimilarCodeResult(
            base_snippet="snippet", base_type_definitions={"key": "value"}, matches=[]
        )
        dumped = result.model_dump(by_alias=True)

        assert "baseSnippet" in dumped
        assert dumped["baseSnippet"] == "snippet"
        assert "baseTypeDefinitions" in dumped
        assert dumped["baseTypeDefinitions"] == {"key": "value"}
        assert "matches" in dumped
        assert dumped["matches"] == []

    def test_deserialization(self):
        """Test deserialization from dict."""
        data = {
            "baseSnippet": "snippet",
            "baseTypeDefinitions": {"a": 1},
            "matches": [
                {"file": "f.ts", "symbol": "S", "similarity": 0.8, "snippet": "s"}
            ],
        }
        result = TSFindSimilarCodeResult.model_validate(data)
        assert result.base_snippet == "snippet"
        assert result.base_type_definitions == {"a": 1}
        assert len(result.matches) == 1
        assert result.matches[0].similarity == 0.8

    def test_error_field(self):
        """Test error field."""
        result = TSFindSimilarCodeResult(error="Something went wrong")
        assert result.error == "Something went wrong"
        dumped = result.model_dump(by_alias=True)
        assert dumped["error"] == "Something went wrong"

    def test_roundtrip(self):
        """Test roundtrip serialization."""
        match = SimilarCodeMatch(
            file="src/utils.ts",
            symbol="processData",
            similarity=0.95,
            snippet="function processData() { ... }",
        )
        original = TSFindSimilarCodeResult(base_snippet="base", matches=[match])

        json_str = original.model_dump_json(by_alias=True)
        restored = TSFindSimilarCodeResult.model_validate_json(json_str)

        assert restored.base_snippet == original.base_snippet
        assert len(restored.matches) == 1
        assert restored.matches[0].file == original.matches[0].file
