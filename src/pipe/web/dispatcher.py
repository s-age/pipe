"""Central action dispatcher for routing requests to action handlers."""

from typing import Any

from flask import Request, Response
from pipe.core.agents.takt_agent import TaktAgent
from pipe.core.container import DependencyContainer

# No longer importing specific fs actions for registration
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.core.services.search_sessions_service import SearchSessionsService
from pipe.core.services.session_artifact_service import SessionArtifactService
from pipe.core.services.session_instruction_service import SessionInstructionService
from pipe.core.services.session_management_service import SessionManagementService
from pipe.core.services.session_service import SessionService
from pipe.core.services.session_workflow_service import SessionWorkflowService
from pipe.web.binder import RequestBinder
from pipe.web.factory import GenericActionFactory
from pipe.web.responses import ApiResponse
from pydantic import ValidationError


class ActionDispatcher:
    """Dispatches actions to appropriate handlers using auto-wiring."""

    def __init__(
        self,
        binder: RequestBinder,
        factory: GenericActionFactory,
    ):
        self.binder = binder
        self.factory = factory

    def dispatch(
        self,
        action_class: type,
        params: dict,
        request_data: Request | None = None,
    ) -> tuple[dict | Response | Any, int] | Response:
        """Dispatch an action to the appropriate handler.

        Args:
            action_class: The Action class to instantiate and execute.
            params: Parameters extracted from the URL (path params).
            request_data: The Flask request object.

        Returns:
            A tuple of (response_data, status_code) or Response object
        """
        if request_data is None:
            return {"message": "Request object is missing"}, 500

        # 1. Bind & Validate Request
        try:
            validated_data = self.binder.bind(action_class, request_data, params)
        except ValidationError as e:
            error_messages = [
                f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
                for err in e.errors()
            ]
            response = ApiResponse(success=False, message="; ".join(error_messages))
            return response.model_dump(mode="json", by_alias=True), 422
        except Exception as e:
            # Check if this is a custom HTTP exception from validation
            from pipe.web.exceptions import HttpException

            if isinstance(e, HttpException):
                response = ApiResponse(success=False, message=e.message)
                return response.model_dump(mode="json", by_alias=True), e.status_code

            return {"success": False, "message": str(e)}, 500

        # 2. Prepare Runtime Context
        runtime_context = {
            "params": params,
            "request_data": request_data,
            "validated_request": validated_data,
        }

        # 3. Instantiate Action (Auto-Wiring)
        try:
            action_instance = self.factory.create(action_class, runtime_context)

            # Manual injection fallback
            if hasattr(action_instance, "request_data") and not getattr(
                action_instance, "request_data", None
            ):
                action_instance.request_data = request_data  # type: ignore
            if hasattr(action_instance, "params") and not getattr(
                action_instance, "params", None
            ):
                action_instance.params = params  # type: ignore

            # 4. Execute Action
            result = action_instance.execute()

            # 5. Format Response
            if isinstance(result, Response):
                return result
            elif isinstance(result, tuple):
                response_data, status_code = result
                if hasattr(response_data, "model_dump"):
                    response_data = response_data.model_dump(mode="json", by_alias=True)
                return response_data, status_code
            else:
                response = ApiResponse(success=True, data=result)
                return response.model_dump(mode="json", by_alias=True), 200

        except Exception as e:
            import traceback

            traceback.print_exc()

            try:
                from pipe.web.exceptions import (
                    BadRequestError,
                    HttpException,
                    NotFoundError,
                    UnprocessableEntityError,
                )

                # 1. Custom HTTP Exceptions (Subclasses first for specific handling)
                if isinstance(e, BadRequestError):
                    response = ApiResponse(success=False, message=e.message)
                    return response.model_dump(
                        mode="json", by_alias=True
                    ), e.status_code
                elif isinstance(e, NotFoundError):
                    response = ApiResponse(success=False, message=e.message)
                    return response.model_dump(
                        mode="json", by_alias=True
                    ), e.status_code
                elif isinstance(e, UnprocessableEntityError):
                    response = ApiResponse(success=False, message=e.message)
                    return response.model_dump(
                        mode="json", by_alias=True
                    ), e.status_code
                # Catch any other custom HttpExceptions not covered by specific checks
                elif isinstance(e, HttpException):
                    response = ApiResponse(success=False, message=e.message)
                    return response.model_dump(
                        mode="json", by_alias=True
                    ), e.status_code

                # 2. Standard Python Exceptions with specific HTTP codes
                elif isinstance(
                    e, ValueError
                ):  # Changed to 422 as it's often a validation issue
                    response = ApiResponse(success=False, message=str(e))
                    return response.model_dump(mode="json", by_alias=True), 422
                elif isinstance(
                    e, IndexError
                ):  # Index out of range can be a Bad Request
                    response = ApiResponse(success=False, message=str(e))
                    return response.model_dump(mode="json", by_alias=True), 400
                elif isinstance(e, FileNotFoundError):
                    response = ApiResponse(success=False, message=str(e))
                    return response.model_dump(mode="json", by_alias=True), 404
                elif isinstance(
                    e, TypeError
                ):  # Type errors can often be client-side bad request
                    response = ApiResponse(success=False, message=str(e))
                    return response.model_dump(mode="json", by_alias=True), 400

            except ImportError:
                pass

            # Fallback to 500 for any other unhandled exceptions
            response = ApiResponse(success=False, message=str(e))
            return response.model_dump(mode="json", by_alias=True), 500


# Global instances
_dispatcher: ActionDispatcher | None = None
_container: DependencyContainer | None = None


def get_dispatcher() -> ActionDispatcher:
    """Get the global dispatcher instance."""
    if _dispatcher is None:
        raise RuntimeError("Dispatcher not initialized. Call init_dispatcher first.")
    return _dispatcher


def init_dispatcher(
    file_indexer_service: FileIndexerService,
    session_service: SessionService,
    session_management_service: SessionManagementService,
    session_artifact_service: SessionArtifactService,
    session_workflow_service: SessionWorkflowService,
    search_sessions_service: SearchSessionsService,
    takt_agent: TaktAgent,
    session_instruction_service: SessionInstructionService,
) -> ActionDispatcher:
    """Initialize the global dispatcher instance and DI container.

    Args:
        file_indexer_service: FileIndexerService instance
        session_service: SessionService instance
        session_management_service: SessionManagementService instance
        session_artifact_service: SessionArtifactService instance
        session_workflow_service: SessionWorkflowService instance
        search_sessions_service: SearchSessionsService instance
        takt_agent: TaktAgent instance
        session_instruction_service: SessionInstructionService instance
    """
    global _dispatcher, _container

    _container = DependencyContainer()

    # Register Services for DI
    _container.register(FileIndexerService, file_indexer_service)
    _container.register(SessionService, session_service)
    _container.register(SessionManagementService, session_management_service)
    _container.register(SessionArtifactService, session_artifact_service)
    _container.register(SessionWorkflowService, session_workflow_service)
    _container.register(SearchSessionsService, search_sessions_service)
    _container.register(TaktAgent, takt_agent)
    _container.register(SessionInstructionService, session_instruction_service)

    binder = RequestBinder()
    factory = GenericActionFactory(_container)

    _dispatcher = ActionDispatcher(binder, factory)
    return _dispatcher


def dispatch_action(
    action: type | str,
    params: dict,
    request_data: Request | None = None,
) -> tuple[dict | Response | Any, int] | Response:
    """Dispatch an action using the global dispatcher."""
    if isinstance(action, str):
        raise ValueError(
            f"Dispatching by string path '{action}' is no longer supported. "
            "Please pass the Action class directly."
        )

    return get_dispatcher().dispatch(action, params, request_data)
