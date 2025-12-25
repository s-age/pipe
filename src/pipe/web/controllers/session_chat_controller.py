from flask import Request
from pipe.web.actions import SessionGetAction, SessionTreeAction, SettingsGetAction
from pipe.web.dispatcher import dispatch_action
from pipe.web.exceptions import HttpException
from pipe.web.responses import ApiResponse
from pipe.web.responses.session_chat_responses import ChatContextResponse


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
    ) -> tuple[ApiResponse[ChatContextResponse] | ApiResponse, int]:
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

            current_session = None
            if session_id:
                try:
                    # Use dispatch_action to leverage DI container
                    response_data, status_code = dispatch_action(
                        action=SessionGetAction,
                        params={"session_id": session_id},
                        request_data=request_data,
                    )
                    if status_code == 200:
                        current_session = response_data.get("data")
                except HttpException:
                    # Session not found, but still return tree and settings
                    pass

            response_data = ChatContextResponse(
                sessions=tree_response.sessions,
                session_tree=tree_response.session_tree,
                settings=settings_data.settings,
                current_session=current_session,
            )

            return ApiResponse(success=True, data=response_data), 200

        except HttpException as e:
            return ApiResponse(success=False, message=e.message), e.status_code
        except Exception as e:
            return ApiResponse(success=False, message=str(e)), 500
