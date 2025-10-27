from __future__ import annotations

import os

from pipe.core.utils.file import read_text_file


class RoleCollection:
    """
    Manages a list of role file paths and provides utility methods for them.
    This class is used as a transient logic container, primarily for loading
    the content of role files to be included in a prompt.
    """

    def __init__(self, role_paths: list[str]):
        self._role_paths = role_paths if role_paths is not None else []

    def get_for_prompt(self, project_root: str) -> list[str]:
        """
        Loads the content of each role file.
        """
        content = []
        for rel_path in self._role_paths:
            path = os.path.join(project_root, rel_path.strip())
            if os.path.isfile(path):
                content.append(read_text_file(path))
        return content
