"""Session Tree Action for listing sessions in tree structure."""

from typing import Any

from pipe.web.actions.base_action import BaseAction


class SessionTreeAction(BaseAction):
    """Action for getting session tree data."""

    def execute(self) -> tuple[dict[str, Any], int]:
        """Execute the session tree retrieval.

        Returns:
            A tuple of (response_dict, status_code)
        """
        try:
            # Import session_service from the Flask app module
            from pipe.web.app import session_service

            sessions_collection = session_service.list_sessions()
            sorted_sessions = sessions_collection.get_sorted_by_last_updated()

            # Build hierarchical tree from flat session id map.
            # Each session_id may contain slashes indicating parent/child relation
            # (parent_id/child_hash). We create nodes and attach children to parents.
            nodes: dict[str, dict] = {}
            for sid, meta in sorted_sessions:
                nodes[sid] = {"session_id": sid, "overview": meta, "children": []}

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

            return {"sessions": sorted_sessions, "session_tree": roots}, 200
        except Exception as e:
            return {"message": str(e)}, 500
