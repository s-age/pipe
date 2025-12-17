import os
import sys
from typing import TYPE_CHECKING

from pipe.core.models.reference import Reference

if TYPE_CHECKING:
    from pipe.core.collections.references import ReferenceCollection
    from pipe.core.repositories.resource_repository import ResourceRepository


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


def get_references_for_prompt(
    references_collection: "ReferenceCollection",
    resource_repository: "ResourceRepository",
    project_root: str,
):
    abs_project_root = os.path.abspath(project_root)
    for ref in references_collection.data:
        if not ref.disabled:
            try:
                full_path = os.path.abspath(os.path.join(abs_project_root, ref.path))
                if os.path.commonpath([abs_project_root]) != os.path.commonpath(
                    [abs_project_root, full_path]
                ):
                    print(
                        f"Warning: Reference path '{ref.path}' is outside the "
                        "project root. Skipping.",
                        file=sys.stderr,
                    )
                    continue
                content = resource_repository.read_text(full_path, project_root)
                if content is not None:
                    yield {"path": ref.path, "content": content}
                else:
                    print(
                        "Warning: Reference file not found or could not be read: "
                        f"{full_path}",
                        file=sys.stderr,
                    )
            except (FileNotFoundError, ValueError) as e:
                print(
                    f"Warning: Could not process reference file {ref.path}: {e}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"Warning: Could not process reference file {ref.path}: {e}",
                    file=sys.stderr,
                )


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
