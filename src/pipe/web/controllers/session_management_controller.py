from typing import Any

from flask import Request
from pipe.web.actions import SessionTreeAction
from pipe.web.actions.session_management import SessionsListBackupAction
from pipe.web.exceptions import HttpException


class SessionManagementController:
    """
    Controller for session management dashboard, including archives
    and bulk operations.
    """

    def __init__(self, session_service, settings):
        self.session_service = session_service
        self.settings = settings

    def get_dashboard(
        self, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        """
        Get session management dashboard with session tree
        and archived sessions.
        """
        try:
            session_tree_action = SessionTreeAction(
                params={}, request_data=request_data
            )
            tree_response = session_tree_action.execute()

            archives_action = SessionsListBackupAction(
                params={}, request_data=request_data
            )
            archives_response = archives_action.execute()

            # Extract sessions list from the response
            sessions_list = archives_response.sessions

            archives = []
            for item in sessions_list:
                session_data = item.session_data or {}
                archives.append(
                    {
                        "session_id": item.session_id or "",
                        "purpose": session_data.get("purpose", ""),
                        "background": session_data.get("background", ""),
                        "roles": session_data.get("roles", []),
                        "procedure": session_data.get("procedure", ""),
                        "artifacts": session_data.get("artifacts", []),
                        "multi_step_reasoning_enabled": session_data.get(
                            "multi_step_reasoning_enabled", False
                        ),
                        "token_count": session_data.get("token_count", 0),
                        "last_updated_at": session_data.get("last_updated", ""),
                        "deleted_at": item.deleted_at or "",
                    }
                )

            return {
                "session_tree": tree_response.session_tree,
                "archives": archives,
            }, 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
