import os
import sys

from pipe.core.models.reference import Reference
from pipe.core.utils.file import read_text_file


class ReferenceCollection:
    def __init__(self, references: list[Reference]):
        self._references = references

    def add(self, path: str):
        """
        Adds a new reference with a default TTL of 3 if it doesn't already exist.
        If the reference exists, it does nothing.
        """
        if not any(ref.path == path for ref in self._references):
            self._references.append(Reference(path=path, disabled=False, ttl=3))

    def update_ttl(self, path: str, new_ttl: int):
        """
        Updates the TTL of an existing reference and sets its disabled state
        accordingly.
        If the reference does not exist, it does nothing.
        """
        for ref in self._references:
            if ref.path == path:
                ref.ttl = new_ttl
                ref.disabled = False if new_ttl > 0 else True
                break

    def decrement_all_ttl(self):
        """
        Decrements the TTL of all active references. If TTL drops to 0 or below,
        the reference is disabled and TTL is set to 0.
        """
        for ref in self._references:
            if not ref.disabled:
                # Use default TTL of 3 for backward compatibility if ttl is None
                current_ttl = ref.ttl if ref.ttl is not None else 3

                current_ttl -= 1
                ref.ttl = current_ttl

                if current_ttl <= 0:
                    ref.disabled = True
                    ref.ttl = 0  # Set to 0 to preserve the expired state

    def get_for_prompt(self, project_root: str):
        """
        Generator that yields active references with their file content for the prompt.
        Ensures that files are within the project root for security.
        """
        abs_project_root = os.path.abspath(project_root)

        for ref in self._references:
            if not ref.disabled:
                try:
                    full_path = os.path.abspath(
                        os.path.join(abs_project_root, ref.path)
                    )

                    # Security Check: Ensure the file is within the project root
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

    def sort_by_ttl(self):
        """
        Sorts the internal list of references.
        Active references come first, then sorted by TTL descending.
        """
        self._references.sort(
            key=lambda ref: (not ref.disabled, ref.ttl if ref.ttl is not None else 3),
            reverse=True,
        )

    @property
    def references(self) -> list[Reference]:
        """Returns the underlying list of references."""
        return self._references
