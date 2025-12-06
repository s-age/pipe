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
            from pipe.web.service_container import get_session_service

            sessions_collection = get_session_service().list_sessions()
            sorted_sessions = sessions_collection.get_sorted_by_last_updated()

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

            return {"sessions": dict(sorted_sessions), "session_tree": roots}, 200
        except Exception as e:
            return {"message": str(e)}, 500
