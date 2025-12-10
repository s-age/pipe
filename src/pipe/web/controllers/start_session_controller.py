from typing import Any

from flask import Request
from pipe.web.actions import (
    GetRolesAction,
    SessionGetAction,
    SessionTreeAction,
    SettingsGetAction,
)
from pipe.web.exceptions import HttpException


class StartSessionController:
    """Controller for initializing new sessions and loading initial session data."""

    def __init__(self, session_service, settings):
        self.session_service = session_service
        self.settings = settings

    def get_session_with_tree(
        self, session_id: str, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        """
        Get session details with tree, roles, and settings
        for starting a session.
        """
        try:
            session_tree_action = SessionTreeAction(
                params={}, request_data=request_data
            )
            tree_response = session_tree_action.execute()

            session_action = SessionGetAction(
                params={"session_id": session_id}, request_data=request_data
            )
            session_data = session_action.execute()

            # Even if session is not found, continue to get roles and settings
            roles_action = GetRolesAction(params={}, request_data=request_data)
            roles_data = roles_action.execute()

            # Use the Settings action so the public API shape is consistent
            settings_action = SettingsGetAction(params={}, request_data=request_data)
            settings_data = settings_action.execute()

            return {
                # Prefer hierarchical session_tree if provided by the action
                "session_tree": tree_response.get(
                    "session_tree", tree_response.get("sessions", [])
                ),
                "current_session": session_data,
                "settings": settings_data.get("settings", {}),
                "role_options": roles_data,
            }, 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

    def get_settings_with_tree(
        self, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        """Get settings with session tree for initial app load."""
        try:
            session_tree_action = SessionTreeAction(
                params={}, request_data=request_data
            )
            tree_response = session_tree_action.execute()

            settings_action = SettingsGetAction(params={}, request_data=request_data)
            settings_data = settings_action.execute()

            return {
                "settings": settings_data.get("settings", {}),
                # Prefer hierarchical session_tree when available
                "session_tree": tree_response.get(
                    "session_tree", tree_response.get("sessions", [])
                ),
            }, 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
