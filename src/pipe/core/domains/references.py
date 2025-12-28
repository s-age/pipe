from typing import TYPE_CHECKING

from pipe.core.models.reference import Reference

if TYPE_CHECKING:
    from pipe.core.collections.references import ReferenceCollection


def add_reference(
    references_collection: "ReferenceCollection",
    path: str,
    default_ttl: int,
    persist: bool = False,
):
    if not any(ref.path == path for ref in references_collection.data):
        references_collection.data.append(
            Reference(path=path, disabled=False, ttl=default_ttl, persist=persist)
        )
        references_collection.sort_by_ttl()


def update_reference_ttl(
    references_collection: "ReferenceCollection", path: str, new_ttl: int
):
    for ref in references_collection.data:
        if ref.path == path:
            ref.ttl = new_ttl
            ref.disabled = new_ttl <= 0
            break
    references_collection.sort_by_ttl()


def update_reference_persist(
    references_collection: "ReferenceCollection", path: str, new_persist_state: bool
):
    for ref in references_collection.data:
        if ref.path == path:
            ref.persist = new_persist_state
            break
    references_collection.sort_by_ttl()


def toggle_reference_disabled(references_collection: "ReferenceCollection", path: str):
    for ref in references_collection.data:
        if ref.path == path:
            ref.disabled = not ref.disabled
            break
    references_collection.sort_by_ttl()


def get_active_references(
    references_collection: "ReferenceCollection",
) -> list[Reference]:
    """Get all active (non-disabled and non-expired) references from the collection.

    This is a pure function that filters references without performing I/O.
    The caller (Service layer) is responsible for reading file contents.

    Args:
        references_collection: Collection of references

    Returns:
        List of active Reference objects (disabled=False and ttl > 0 or ttl is None)
    """
    return [
        ref
        for ref in references_collection.data
        if not ref.disabled and (ref.ttl is None or ref.ttl > 0)
    ]


def decrement_all_references_ttl(
    references_collection: "ReferenceCollection",
):
    """Decrement TTL for all non-disabled, non-persisted references.

    Sets disabled=True and ttl=0 when TTL reaches 0 or below.
    Respects the persist flag, not decrementing persisted references.
    """
    for ref in references_collection:
        if not ref.disabled and not ref.persist:
            current_ttl = (
                ref.ttl if ref.ttl is not None else references_collection.default_ttl
            )
            current_ttl -= 1
            ref.ttl = current_ttl
            if current_ttl <= 0:
                ref.disabled = True
                ref.ttl = 0
    references_collection.sort_by_ttl()
