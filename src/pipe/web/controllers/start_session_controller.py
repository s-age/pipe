from flask import Request
from pipe.web.actions import (
    GetRolesAction,
    SessionGetAction,
    SessionTreeAction,
    SettingsGetAction,
)
from pipe.web.exceptions import HttpException
from pipe.web.responses import ApiResponse
from pipe.web.responses.start_session_responses import StartSessionContextResponse


class StartSessionController:
    """Controller for initializing new sessions and loading initial session data."""

    def __init__(self, session_service, settings):
        self.session_service = session_service
        self.settings = settings

    def get_session_with_tree(
        self, session_id: str, request_data: Request | None = None
    ) -> tuple[ApiResponse[StartSessionContextResponse] | ApiResponse, int]:
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

            response_data = StartSessionContextResponse(
                session_tree=tree_response.session_tree,
                current_session=session_data,
                settings=settings_data.settings,
                role_options=roles_data.roles,
            )

            return ApiResponse(success=True, data=response_data), 200
        except HttpException as e:
            return ApiResponse(success=False, message=e.message), e.status_code
        except Exception as e:
            return ApiResponse(success=False, message=str(e)), 500

    def get_settings_with_tree(
        self, request_data: Request | None = None
    ) -> tuple[ApiResponse[StartSessionContextResponse] | ApiResponse, int]:
        """Get settings with session tree for initial app load."""
        try:
            session_tree_action = SessionTreeAction(
                params={}, request_data=request_data
            )
            tree_response = session_tree_action.execute()

            settings_action = SettingsGetAction(params={}, request_data=request_data)
            settings_data = settings_action.execute()

            roles_action = GetRolesAction(params={}, request_data=request_data)
            roles_data = roles_action.execute()

            response_data = StartSessionContextResponse(
                settings=settings_data.settings,
                session_tree=tree_response.session_tree,
                role_options=roles_data.roles,
            )

            return ApiResponse(success=True, data=response_data), 200
        except HttpException as e:
            return ApiResponse(success=False, message=e.message), e.status_code
        except Exception as e:
            return ApiResponse(success=False, message=str(e)), 500
