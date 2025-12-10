"""
Service for building and managing session tree structures.

This service is responsible for constructing hierarchical views of sessions,
handling parent-child relationships, and providing tree-based queries.
"""

from pipe.core.collections.sessions import SessionCollection
from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository


class SessionTreeService:
    """Service for session tree operations."""

    def __init__(self, repository: SessionRepository, settings: Settings):
        """Initialize with repository and settings for data access.

        Args:
            repository: SessionRepository instance for accessing session data
            settings: Settings for timezone information
        """
        self.repository = repository
        self.settings = settings

    def get_session_tree(self) -> dict:
        """Build a hierarchical tree structure from sessions.

        Returns:
            Dictionary with:
            - sessions: Map of session_id to metadata
            - session_tree: List of root nodes with children

        Example:
            {
                "sessions": {"session1": {...}, "session2": {...}},
                "session_tree": [
                    {
                        "session_id": "session1",
                        "overview": {...},
                        "children": [
                            {
                                "session_id": "session1/fork1",
                                "overview": {...},
                                "children": [],
                            }
                        ]
                    }
                ]
            }
        """
        index_data = self.repository.get_index()
        sessions_collection = SessionCollection(index_data, self.settings.timezone)
        sorted_sessions = sessions_collection.get_sorted_by_last_updated()

        # Build nodes dictionary
        nodes: dict[str, dict] = {}
        for sid, session_meta in sorted_sessions:
            if not sid:
                continue
            # Add session_id to the metadata from index
            meta = {**session_meta, "session_id": sid}
            # Ensure last_updated_at is present
            meta["last_updated_at"] = meta.get(
                "last_updated_at", meta.get("last_updated", "")
            )
            nodes[sid] = {"session_id": sid, "overview": meta, "children": []}

        # Build tree structure by resolving parent-child relationships
        roots: list[dict] = []
        for sid in nodes:
            if "/" in sid:
                parent_id = sid.rsplit("/", 1)[0]
                parent_node = nodes.get(parent_id)
                if parent_node is not None:
                    # Attach as child and ensure it's not also listed as a root
                    parent_node["children"].append(nodes[sid])
                    # Remove any previous root instance of this node
                    # (if added earlier)
                    roots = [r for r in roots if r.get("session_id") != sid]
                else:
                    # parent not present in index — treat as root
                    roots.append(nodes[sid])
            else:
                roots.append(nodes[sid])

        return {
            "sessions": dict(sorted_sessions),
            "session_tree": roots,
        }
