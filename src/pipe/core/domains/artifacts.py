from pipe.core.models.artifact import Artifact


def build_artifacts_from_data(
    artifacts_with_contents: list[tuple[str, str | None]],
) -> list[Artifact]:
    """Build Artifact objects from path-content pairs.

    This is a pure transformation function that creates Artifact objects
    from pre-loaded data. The caller (Service layer) is responsible for
    reading file contents.

    Args:
        artifacts_with_contents: List of tuples containing (path, content).
            Content can be None if the file doesn't exist or couldn't be read.

    Returns:
        A list of Artifact objects.
    """
    return [
        Artifact(path=path, contents=contents)
        for path, contents in artifacts_with_contents
    ]
