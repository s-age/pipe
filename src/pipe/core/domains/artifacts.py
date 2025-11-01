import os
from typing import TYPE_CHECKING

from pipe.core.models.artifact import Artifact
from pipe.core.utils.file import read_text_file

if TYPE_CHECKING:
    pass  # 仮の型ヒント


def process_artifacts_for_session(
    artifacts_data: list[str] | None, project_root: str
) -> list[Artifact]:
    """Processes a list of artifact paths, reading their contents if files exist.

    Args:
        artifacts_data: A list of artifact file paths.
        project_root: The absolute path to the project root directory.

    Returns:
        A new list of Artifact objects with 'contents' field populated.
    """
    processed_artifacts: list[Artifact] = []
    if artifacts_data:
        for artifact_path in artifacts_data:
            full_path = os.path.abspath(os.path.join(project_root, artifact_path))
            contents = None
            if os.path.exists(full_path) and os.path.isfile(full_path):
                contents = read_text_file(full_path)
            processed_artifacts.append(Artifact(path=artifact_path, contents=contents))
    return processed_artifacts
