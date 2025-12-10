from typing import Any

from flask import Request
from pipe.web.actions import (
    SessionGetAction,
    SessionTreeAction,
    SettingsGetAction,
)
from pipe.web.exceptions import HttpException
from pipe.web.requests.sessions.get_session import GetSessionRequest


class SessionChatController:
    """
    Controller for chat interface, providing session history
    and current session context.
    """

    def __init__(self, session_service, settings):
        self.session_service = session_service
        self.settings = settings

    def get_chat_context(
        self, session_id: str | None, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        """
        Get chat interface context including session tree, settings,
        and current session if specified.
        """
        try:
            session_tree_action = SessionTreeAction(
                params={}, request_data=request_data
            )
            tree_response = session_tree_action.execute()

            # Get settings
            settings_action = SettingsGetAction(params={}, request_data=request_data)
            settings_data = settings_action.execute()

            response = {
                "sessions": tree_response.get("sessions", []),
                "session_tree": tree_response.get(
                    "session_tree", tree_response.get("sessions", [])
                ),
                "settings": settings_data.get("settings", {}),
            }

            if session_id:
                try:
                    # Create validated request for the action
                    validated_request = GetSessionRequest(session_id=session_id)
                    session_action = SessionGetAction(
                        params={"session_id": session_id},
                        request_data=request_data,
                        validated_request=validated_request,
                    )
                    session_data = session_action.execute()
                    response["current_session"] = session_data
                except HttpException:
                    # Session not found, but still return tree and settings
                    response["current_session"] = None

            return response, 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
