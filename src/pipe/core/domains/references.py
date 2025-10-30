import os
import sys
from typing import TYPE_CHECKING

from pipe.core.models.reference import Reference
from pipe.core.utils.file import read_text_file

if TYPE_CHECKING:
    from pipe.core.collections.references import ReferenceCollection


def add_reference(
    references_collection: "ReferenceCollection", path: str, default_ttl: int
):
    if not any(ref.path == path for ref in references_collection.data):
        references_collection.data.append(
            Reference(path=path, disabled=False, ttl=default_ttl)
        )
        sort_references_by_ttl(references_collection)


def update_reference_ttl(
    references_collection: "ReferenceCollection", path: str, new_ttl: int
):
    for ref in references_collection.data:
        if ref.path == path:
            ref.ttl = new_ttl
            ref.disabled = new_ttl <= 0
            break
    sort_references_by_ttl(references_collection)


def decrement_all_references_ttl(references_collection: "ReferenceCollection"):
    for ref in references_collection:
        if not ref.disabled:
            current_ttl = (
                ref.ttl if ref.ttl is not None else references_collection.default_ttl
            )
            current_ttl -= 1
            ref.ttl = current_ttl
            if current_ttl <= 0:
                ref.disabled = True
                ref.ttl = 0
    sort_references_by_ttl(references_collection)


def get_references_for_prompt(
    references_collection: "ReferenceCollection", project_root: str
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
                content = read_text_file(full_path)
                if content is not None:
                    yield {"path": ref.path, "content": content}
                else:
                    print(
                        "Warning: Reference file not found or could not be read: "
                        f"{full_path}",
                        file=sys.stderr,
                    )
            except Exception as e:
                print(
                    f"Warning: Could not process reference file {ref.path}: {e}",
                    file=sys.stderr,
                )


def sort_references_by_ttl(references_collection: "ReferenceCollection"):
    references_collection.sort(
        key=lambda ref:
        (
            not ref.disabled,
            ref.ttl if ref.ttl is not None else references_collection.default_ttl,
        ),
        reverse=True,
    )
