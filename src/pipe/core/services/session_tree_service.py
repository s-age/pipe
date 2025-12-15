"""
Service for building and managing session tree structures.

This service is responsible for constructing hierarchical views of sessions,
handling parent-child relationships, and providing tree-based queries.
"""

from pipe.core.models.results.session_tree_result import (
    SessionTreeNode,
    SessionTreeResult,
)
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

    def get_session_tree(self) -> SessionTreeResult:
        """Build a hierarchical tree structure from sessions.

        Returns:
            SessionTreeResult with:
            - sessions: Map of session_id to metadata
            - session_tree: List of root nodes with children

        Example:
            SessionTreeResult(
                sessions={"session1": {...}, "session2": {...}},
                session_tree=[
                    SessionTreeNode(
                        session_id="session1",
                        overview={...},
                        children=[
                            SessionTreeNode(
                                session_id="session1/fork1",
                                overview={...},
                                children=[]
                            )
                        ]
                    )
                ]
            )
        """
        index = self.repository.load_index()
        sorted_sessions = index.get_sessions_sorted_by_last_updated()

        # Build nodes dictionary using SessionTreeNode
        nodes: dict[str, SessionTreeNode] = {}
        for sid, session_meta in sorted_sessions:
            if not sid:
                continue
            # Convert SessionIndexEntry to dict and add session_id
            meta = session_meta.model_dump(by_alias=True)
            meta["session_id"] = sid
            # last_updated_at is already present in SessionIndexEntry
            nodes[sid] = SessionTreeNode(session_id=sid, overview=meta, children=[])

        # Build tree structure by resolving parent-child relationships
        roots: list[SessionTreeNode] = []
        for sid in nodes:
            if "/" in sid:
                parent_id = sid.rsplit("/", 1)[0]
                parent_node = nodes.get(parent_id)
                if parent_node is not None:
                    # Attach as child and ensure it's not also listed as a root
                    parent_node.children.append(nodes[sid])
                    # Remove any previous root instance of this node
                    # (if added earlier)
                    roots = [r for r in roots if r.session_id != sid]
                else:
                    # parent not present in index — treat as root
                    roots.append(nodes[sid])
            else:
                roots.append(nodes[sid])

        # Prepare sessions dict with session_id included in the value
        sessions_with_id = {}
        for sid, meta in sorted_sessions:
            meta_dict = meta.model_dump(by_alias=True)
            sessions_with_id[sid] = {**meta_dict, "session_id": sid}

        return SessionTreeResult(
            sessions=sessions_with_id,
            session_tree=roots,
        )
