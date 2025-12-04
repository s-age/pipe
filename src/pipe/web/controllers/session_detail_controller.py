from typing import Any

from flask import Request
from pipe.web.actions import (
    GetRolesAction,
    SessionGetAction,
    SessionTreeAction,
    SettingsGetAction,
)
from pipe.web.actions.session_management_actions import SessionsListBackupAction


class SessionDetailController:
    def __init__(self, session_service, settings):
        self.session_service = session_service
        self.settings = settings

    def get_session_with_tree(
        self, session_id: str, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        session_tree_action = SessionTreeAction(params={}, request_data=request_data)
        tree_response, tree_status = session_tree_action.execute()

        if tree_status != 200:
            return tree_response, tree_status

        session_action = SessionGetAction(
            params={"session_id": session_id}, request_data=request_data
        )
        session_response, session_status = session_action.execute()

        # Even if session is not found, continue to get roles and settings
        roles_action = GetRolesAction(params={}, request_data=request_data)
        roles_response, roles_status = roles_action.execute()

        if roles_status != 200:
            return roles_response, roles_status

        # Use the Settings action so the public API shape is consistent
        settings_action = SettingsGetAction(params={}, request_data=request_data)
        settings_response, settings_status = settings_action.execute()
        if settings_status != 200:
            return settings_response, settings_status

        return {
            # Prefer hierarchical session_tree if provided by the action
            "session_tree": tree_response.get(
                "session_tree", tree_response.get("sessions", [])
            ),
            "current_session": (
                session_response.get("session", {}) if session_status == 200 else None
            ),
            "settings": settings_response.get("settings", {}),
            "role_options": roles_response,
        }, 200

    def get_settings_with_tree(
        self, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        session_tree_action = SessionTreeAction(params={}, request_data=request_data)
        tree_response, tree_status = session_tree_action.execute()

        if tree_status != 200:
            return tree_response, tree_status

        settings_action = SettingsGetAction(params={}, request_data=request_data)
        settings_response, settings_status = settings_action.execute()
        if settings_status != 200:
            return settings_response, settings_status

        return {
            "settings": settings_response.get("settings", {}),
            # Prefer hierarchical session_tree when available
            "session_tree": tree_response.get(
                "session_tree", tree_response.get("sessions", [])
            ),
        }, 200

    def get_session_management_dashboard(
        self, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        session_tree_action = SessionTreeAction(params={}, request_data=request_data)
        tree_response, tree_status = session_tree_action.execute()

        if tree_status != 200:
            return tree_response, tree_status

        archives_action = SessionsListBackupAction(params={}, request_data=request_data)
        archives_response, archives_status = archives_action.execute()

        if archives_status != 200:
            return archives_response, archives_status

        archives_raw = archives_response.get("sessions", [])
        archives = []
        for item in archives_raw:
            session_data = item.get("session_data", {})
            archives.append(
                {
                    "session_id": item.get("session_id", ""),
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
                    "deleted_at": item.get("deleted_at", ""),
                }
            )

        return {
            "session_tree": tree_response.get(
                "session_tree", tree_response.get("sessions", [])
            ),
            "archives": archives,
        }, 200

    def get_chat_history(
        self, session_id: str | None, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        session_tree_action = SessionTreeAction(params={}, request_data=request_data)
        tree_response, tree_status = session_tree_action.execute()

        if tree_status != 200:
            return tree_response, tree_status

        # Get settings
        settings_action = SettingsGetAction(params={}, request_data=request_data)
        settings_response, settings_status = settings_action.execute()

        response = {
            "sessions": tree_response.get("sessions", []),
            "session_tree": tree_response.get(
                "session_tree", tree_response.get("sessions", [])
            ),
            "settings": (
                settings_response.get("settings", {}) if settings_status == 200 else {}
            ),
        }

        if session_id:
            session_action = SessionGetAction(
                params={"session_id": session_id}, request_data=request_data
            )
            session_response, session_status = session_action.execute()

            if session_status == 200:
                response["current_session"] = session_response.get("session")

        return response, 200
