import os
from typing import TYPE_CHECKING

from pipe.core.models.artifact import Artifact

if TYPE_CHECKING:
    from pipe.core.repositories.resource_repository import ResourceRepository


def process_artifacts_for_session(
    artifacts_data: list[str] | None,
    resource_repository: "ResourceRepository",
    project_root: str,
) -> list[Artifact]:
    """Processes a list of artifact paths, reading their contents if files exist.

    Args:
        artifacts_data: A list of artifact file paths.
        resource_repository: Repository for reading resources with path validation.
        project_root: The absolute path to the project root directory.

    Returns:
        A new list of Artifact objects with 'contents' field populated.
    """
    processed_artifacts: list[Artifact] = []
    if artifacts_data:
        for artifact_path in artifacts_data:
            full_path = os.path.abspath(os.path.join(project_root, artifact_path))
            contents = None
            if resource_repository.exists(full_path, allowed_root=project_root):
                contents = resource_repository.read_text(
                    full_path, allowed_root=project_root
                )
            processed_artifacts.append(Artifact(path=artifact_path, contents=contents))
    return processed_artifacts
