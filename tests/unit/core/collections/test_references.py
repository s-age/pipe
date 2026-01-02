from unittest.mock import MagicMock, patch

import pytest
from pipe.core.collections.references import ReferenceCollection

from tests.factories.models import ReferenceFactory


class TestReferenceCollection:
    """Tests for ReferenceCollection."""

    def test_init_empty(self):
        """Test initialization with default values."""
        collection = ReferenceCollection()
        assert collection.data == []
        assert collection.default_ttl == 3

    def test_init_with_data(self):
        """Test initialization with provided data."""
        refs = ReferenceFactory.create_batch(2)
        collection = ReferenceCollection(data=refs, default_ttl=5)
        assert len(collection.data) == 2
        assert collection.default_ttl == 5

    def test_add_new_reference(self):
        """Test adding a new reference."""
        collection = ReferenceCollection()
        collection.add("test.py")
        assert len(collection.data) == 1
        assert collection.data[0].path == "test.py"
        assert collection.data[0].ttl == 3

    def test_add_duplicate_reference(self):
        """Test that duplicate references are not added."""
        collection = ReferenceCollection()
        collection.add("test.py")
        collection.add("test.py")
        assert len(collection.data) == 1

    def test_update_ttl(self):
        """Test updating TTL for a reference."""
        ref = ReferenceFactory.create(path="test.py", ttl=3)
        collection = ReferenceCollection(data=[ref])
        collection.update_ttl("test.py", 5)
        assert collection.data[0].ttl == 5
        assert collection.data[0].disabled is False

    def test_update_ttl_disables_when_zero(self):
        """Test that setting TTL to 0 disables the reference."""
        ref = ReferenceFactory.create(path="test.py", ttl=3)
        collection = ReferenceCollection(data=[ref])
        collection.update_ttl("test.py", 0)
        assert collection.data[0].ttl == 0
        assert collection.data[0].disabled is True

    def test_sort_by_ttl(self):
        """Test internal sorting by TTL and disabled state."""
        refs = [
            ReferenceFactory.create(path="low.py", ttl=1),
            ReferenceFactory.create(path="high.py", ttl=10),
            ReferenceFactory.create(path="disabled.py", ttl=5, disabled=True),
        ]
        collection = ReferenceCollection(data=refs)
        # Order should be: high (10), low (1), disabled (True)
        assert collection.data[0].path == "high.py"
        assert collection.data[1].path == "low.py"
        assert collection.data[2].path == "disabled.py"

    def test_sort_by_ttl_with_none(self):
        """Test sorting when some TTLs are None (uses default_ttl)."""
        refs = [
            ReferenceFactory.create(path="none.py", ttl=None),
            ReferenceFactory.create(path="high.py", ttl=10),
        ]
        collection = ReferenceCollection(data=refs, default_ttl=5)
        # high (10) > none (5)
        assert collection.data[0].path == "high.py"
        assert collection.data[1].path == "none.py"

    def test_update_ttl_by_index(self):
        """Test updating TTL by index."""
        refs = [ReferenceFactory.create(path="test.py", ttl=3)]
        collection = ReferenceCollection(data=refs)
        collection.update_ttl_by_index(0, 10)
        assert collection.data[0].ttl == 10

    def test_update_ttl_by_index_out_of_range(self):
        """Test update_ttl_by_index raises IndexError for invalid index."""
        collection = ReferenceCollection()
        with pytest.raises(IndexError):
            collection.update_ttl_by_index(0, 10)

    def test_update_persist_by_index(self):
        """Test updating persist state by index."""
        refs = [ReferenceFactory.create(path="test.py", persist=False)]
        collection = ReferenceCollection(data=refs)
        collection.update_persist_by_index(0, True)
        assert collection.data[0].persist is True

    def test_update_persist_by_index_out_of_range(self):
        """Test update_persist_by_index raises IndexError for invalid index."""
        collection = ReferenceCollection()
        with pytest.raises(IndexError):
            collection.update_persist_by_index(0, True)

    def test_toggle_disabled_by_index(self):
        """Test toggling disabled state by index."""
        refs = [ReferenceFactory.create(path="test.py", disabled=False)]
        collection = ReferenceCollection(data=refs)
        new_state = collection.toggle_disabled_by_index(0)
        assert new_state is True
        assert collection.data[0].disabled is True

        new_state = collection.toggle_disabled_by_index(0)
        assert new_state is False
        assert collection.data[0].disabled is False

    def test_toggle_disabled_by_index_out_of_range(self):
        """Test toggle_disabled_by_index raises IndexError for invalid index."""
        collection = ReferenceCollection()
        with pytest.raises(IndexError):
            collection.toggle_disabled_by_index(0)

    @patch("pipe.core.domains.references.decrement_all_references_ttl")
    def test_decrement_all_ttl(self, mock_decrement):
        """Test decrement_all_ttl calls domain function."""
        collection = ReferenceCollection()
        collection.decrement_all_ttl()
        mock_decrement.assert_called_once_with(collection)

    def test_sort_by_ttl_public(self):
        """Test public sort_by_ttl method."""
        refs = [
            ReferenceFactory.create(path="low.py", ttl=1),
            ReferenceFactory.create(path="high.py", ttl=10),
        ]
        collection = ReferenceCollection(data=refs)
        # Manually mess up order
        collection.data = [refs[0], refs[1]]
        collection.sort_by_ttl()
        assert collection.data[0].path == "high.py"

    def test_get_for_prompt_basic(self):
        """Test get_for_prompt yields correct data."""
        mock_repo = MagicMock()
        mock_repo.read_text.return_value = "file content"

        ref = ReferenceFactory.create(path="test.py", disabled=False)
        collection = ReferenceCollection(data=[ref])

        # Patch at the source module because it's a function-level import
        with patch(
            "pipe.core.domains.references.get_active_references", return_value=[ref]
        ):
            results = list(collection.get_for_prompt(mock_repo, "/project"))

            assert len(results) == 1
            assert results[0] == {"path": "test.py", "content": "file content"}

    def test_get_for_prompt_outside_root(self):
        """Test get_for_prompt skips files outside project root."""
        mock_repo = MagicMock()
        ref = ReferenceFactory.create(path="../outside.py", disabled=False)
        collection = ReferenceCollection(data=[ref])

        with patch(
            "pipe.core.domains.references.get_active_references", return_value=[ref]
        ):
            # Use real os.path behavior but mock the commonpath check if needed
            # Or just use paths that actually trigger the logic
            results = list(collection.get_for_prompt(mock_repo, "/project/root"))
            assert len(results) == 0

    def test_get_for_prompt_read_error(self):
        """Test get_for_prompt handles read errors."""
        mock_repo = MagicMock()
        mock_repo.read_text.return_value = None

        ref = ReferenceFactory.create(path="test.py", disabled=False)
        collection = ReferenceCollection(data=[ref])

        with patch(
            "pipe.core.domains.references.get_active_references", return_value=[ref]
        ):
            results = list(collection.get_for_prompt(mock_repo, "/project"))
            assert len(results) == 0

    def test_get_for_prompt_exception(self):
        """Test get_for_prompt handles exceptions during processing."""
        mock_repo = MagicMock()
        mock_repo.read_text.side_effect = Exception("Read error")

        ref = ReferenceFactory.create(path="test.py", disabled=False)
        collection = ReferenceCollection(data=[ref])

        with patch(
            "pipe.core.domains.references.get_active_references", return_value=[ref]
        ):
            results = list(collection.get_for_prompt(mock_repo, "/project"))
            assert len(results) == 0

    def test_pydantic_serialization(self):
        """Test Pydantic serialization and validation."""
        from pydantic import BaseModel

        class MockModel(BaseModel):
            refs: ReferenceCollection

        refs = [ReferenceFactory.create(path="test.py", ttl=3)]
        collection = ReferenceCollection(data=refs)
        model = MockModel(refs=collection)

        dumped = model.model_dump()
        assert isinstance(dumped["refs"], list)
        assert dumped["refs"][0]["path"] == "test.py"

        # Round trip
        restored = MockModel.model_validate(dumped)
        assert isinstance(restored.refs, ReferenceCollection)
        assert restored.refs.data[0].path == "test.py"

    def test_pydantic_json_schema(self):
        """Test Pydantic JSON schema generation."""
        from pydantic import TypeAdapter

        adapter = TypeAdapter(ReferenceCollection)
        schema = adapter.json_schema()
        assert schema["type"] == "array"
        assert "items" in schema
