from __future__ import annotations
from typing import List, Iterator, Dict
import os

from pipe.core.models.reference import Reference
from pipe.core.utils.file import read_text_file

class ReferenceCollection:
    """
    Manages a list of Reference objects and provides utility methods for them.
    This class is used as a transient logic container and does not handle its own persistence.
    It is instantiated on-the-fly with a list of references to perform operations.
    """
    def __init__(self, references: List[Reference]):
        self._references = references

    def get_for_prompt(self, project_root: str) -> Iterator[Dict[str, str]]:
        """
        Yields file references suitable for inclusion in a prompt.

        This method iterates through the references, reads the content of each
        valid and enabled file, and yields a dictionary containing the file path
        and its content.
        """
        if not self._references:
            return

        for ref in self._references:
            if not ref.disabled:
                # The path stored in the reference is relative to the project root.
                # We need to construct the absolute path to read the file.
                abs_path = os.path.abspath(os.path.join(project_root, ref.path))

                # Security check: Ensure the file is within the project directory.
                if not abs_path.startswith(os.path.abspath(project_root)):
                    # Skip files outside the project root for security.
                    continue

                content = read_text_file(abs_path)
                if content is not None:
                    # For the prompt, we provide the original relative path.
                    yield {
                        "path": ref.path,
                        "content": content
                    }