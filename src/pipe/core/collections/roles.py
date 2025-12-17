from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipe.core.repositories.resource_repository import ResourceRepository


class RoleCollection:
    """
    Manages a list of role file paths and provides utility methods for them.
    This class is used as a transient logic container, primarily for loading
    the content of role files to be included in a prompt.
    """

    def __init__(self, role_paths: list[str]):
        self._role_paths = role_paths if role_paths is not None else []

    def get_for_prompt(self, resource_repository: ResourceRepository) -> list[str]:
        """
        Loads the content of each role file.

        Args:
            resource_repository: Repository for reading resources with path validation.

        Returns:
            List of role file contents.
        """
        content = []
        project_root = str(resource_repository.project_root)
        for rel_path in self._role_paths:
            path = os.path.join(project_root, rel_path.strip())
            if resource_repository.exists(path, allowed_root=project_root):
                text = resource_repository.read_text(path, allowed_root=project_root)
                content.append(text)
        return content
