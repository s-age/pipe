from typing import Any

from flask import Request
from pipe.web.actions import (
    GetRolesAction,
    SessionGetAction,
    SessionTreeAction,
    SettingsGetAction,
)


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

        if session_status != 200:
            return session_response, session_status

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
            "session_tree": tree_response.get("session_tree", tree_response.get("sessions", [])),
            "current_session": session_response.get("session", {}),
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
            "session_tree": tree_response.get("session_tree", tree_response.get("sessions", [])),
        }, 200
