import pytest
from pipe.core.collections.references import ReferenceCollection
from pipe.core.domains.references import (
    add_reference,
    decrement_all_references_ttl,
    get_active_references,
    toggle_reference_disabled,
    update_reference_persist,
    update_reference_ttl,
)

from tests.factories.models.reference_factory import ReferenceFactory


class TestReferencesDomain:
    """Tests for references domain logic."""

    @pytest.fixture
    def references_collection(self) -> ReferenceCollection:
        """Create a ReferenceCollection for testing."""
        return ReferenceCollection(default_ttl=3)

    def test_add_reference_new(self, references_collection: ReferenceCollection):
        """Test adding a new reference to the collection."""
        path = "test.py"
        add_reference(references_collection, path, default_ttl=5, persist=True)

        assert len(references_collection.data) == 1
        assert references_collection.data[0].path == path
        assert references_collection.data[0].ttl == 5
        assert references_collection.data[0].persist is True
        assert references_collection.data[0].disabled is False

    def test_add_reference_duplicate(self, references_collection: ReferenceCollection):
        """Test that duplicate references are not added."""
        path = "test.py"
        add_reference(references_collection, path, default_ttl=3)
        add_reference(references_collection, path, default_ttl=5)

        assert len(references_collection.data) == 1
        assert references_collection.data[0].ttl == 3  # Original TTL preserved

    def test_update_reference_ttl(self, references_collection: ReferenceCollection):
        """Test updating the TTL of a reference."""
        path = "test.py"
        add_reference(references_collection, path, default_ttl=3)
        update_reference_ttl(references_collection, path, new_ttl=10)

        assert references_collection.data[0].ttl == 10
        assert references_collection.data[0].disabled is False

    def test_update_reference_ttl_disabled(
        self, references_collection: ReferenceCollection
    ):
        """Test that updating TTL to 0 or less disables the reference."""
        path = "test.py"
        add_reference(references_collection, path, default_ttl=3)
        update_reference_ttl(references_collection, path, new_ttl=0)

        assert references_collection.data[0].ttl == 0
        assert references_collection.data[0].disabled is True

    def test_update_reference_persist(self, references_collection: ReferenceCollection):
        """Test updating the persist state of a reference."""
        path = "test.py"
        add_reference(references_collection, path, default_ttl=3, persist=False)
        update_reference_persist(references_collection, path, new_persist_state=True)

        assert references_collection.data[0].persist is True

    def test_toggle_reference_disabled(
        self, references_collection: ReferenceCollection
    ):
        """Test toggling the disabled state of a reference."""
        path = "test.py"
        add_reference(references_collection, path, default_ttl=3)

        # Toggle to True
        toggle_reference_disabled(references_collection, path)
        assert references_collection.data[0].disabled is True

        # Toggle back to False
        toggle_reference_disabled(references_collection, path)
        assert references_collection.data[0].disabled is False

    def test_get_active_references(self, references_collection: ReferenceCollection):
        """Test filtering active references."""
        # Active: TTL > 0, disabled=False
        ref1 = ReferenceFactory.create(path="active1.py", ttl=3, disabled=False)
        # Active: TTL is None, disabled=False
        ref2 = ReferenceFactory.create(path="active2.py", ttl=None, disabled=False)
        # Inactive: disabled=True
        ref3 = ReferenceFactory.create(path="inactive1.py", ttl=3, disabled=True)
        # Inactive: TTL <= 0
        ref4 = ReferenceFactory.create(path="inactive2.py", ttl=0, disabled=False)

        references_collection.data = [ref1, ref2, ref3, ref4]

        active_refs = get_active_references(references_collection)

        assert len(active_refs) == 2
        assert any(ref.path == "active1.py" for ref in active_refs)
        assert any(ref.path == "active2.py" for ref in active_refs)

    def test_decrement_all_references_ttl(
        self, references_collection: ReferenceCollection
    ):
        """Test decrementing TTL for all applicable references."""
        ref1 = ReferenceFactory.create(path="ref1.py", ttl=3, persist=False)
        ref2 = ReferenceFactory.create(path="ref2.py", ttl=5, persist=False)
        references_collection.data = [ref1, ref2]

        decrement_all_references_ttl(references_collection)

        assert ref1.ttl == 2
        assert ref2.ttl == 4

    def test_decrement_all_references_ttl_persist(
        self, references_collection: ReferenceCollection
    ):
        """Test that persisted references are not decremented."""
        ref1 = ReferenceFactory.create(path="persist.py", ttl=3, persist=True)
        references_collection.data = [ref1]

        decrement_all_references_ttl(references_collection)

        assert ref1.ttl == 3  # Unchanged

    def test_decrement_all_references_ttl_disabled(
        self, references_collection: ReferenceCollection
    ):
        """Test that disabled references are not decremented."""
        ref1 = ReferenceFactory.create(path="disabled.py", ttl=3, disabled=True)
        references_collection.data = [ref1]

        decrement_all_references_ttl(references_collection)

        assert ref1.ttl == 3  # Unchanged

    def test_decrement_all_references_ttl_reaches_zero(
        self, references_collection: ReferenceCollection
    ):
        """Test that references are disabled when TTL reaches zero."""
        ref1 = ReferenceFactory.create(path="expire.py", ttl=1, persist=False)
        references_collection.data = [ref1]

        decrement_all_references_ttl(references_collection)

        assert ref1.ttl == 0
        assert ref1.disabled is True

    def test_decrement_all_references_ttl_uses_default_ttl(
        self, references_collection: ReferenceCollection
    ):
        """Test that default_ttl is used when ref.ttl is None."""
        ref1 = ReferenceFactory.create(path="default.py", ttl=None, persist=False)
        references_collection.data = [ref1]
        references_collection.default_ttl = 5

        decrement_all_references_ttl(references_collection)

        assert ref1.ttl == 4

    def test_functions_call_sort_by_ttl(
        self, references_collection: ReferenceCollection
    ):
        """Test that domain functions call sort_by_ttl on the collection."""
        # We use a mock to verify the call
        from unittest.mock import MagicMock

        references_collection.sort_by_ttl = MagicMock()
        path = "test.py"
        add_reference(references_collection, path, default_ttl=3)

        # add_reference calls sort_by_ttl
        assert references_collection.sort_by_ttl.call_count == 1

        update_reference_ttl(references_collection, path, 5)
        assert references_collection.sort_by_ttl.call_count == 2

        update_reference_persist(references_collection, path, True)
        assert references_collection.sort_by_ttl.call_count == 3

        toggle_reference_disabled(references_collection, path)
        assert references_collection.sort_by_ttl.call_count == 4

        decrement_all_references_ttl(references_collection)
        assert references_collection.sort_by_ttl.call_count == 5
