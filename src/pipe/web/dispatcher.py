"""Central action dispatcher for routing requests to action handlers."""

import re
from typing import Any

from flask import Request, Response
from pipe.web.actions import (
    ApproveCompressorAction,
    CreateCompressorSessionAction,
    CreateTherapistSessionAction,
    DenyCompressorAction,
    GetProceduresAction,
    GetRolesAction,
    HyperparametersEditAction,
    MultiStepReasoningEditAction,
    ReferencePersistEditAction,
    ReferencesEditAction,
    ReferenceToggleDisabledAction,
    ReferenceTtlEditAction,
    SessionMetaEditAction,
    TodosDeleteAction,
    TodosEditAction,
    TurnDeleteAction,
    TurnEditAction,
)
from pipe.web.actions.fs import (
    IndexFilesAction,
    LsAction,
    SearchL2Action,
    SearchSessionsAction,
)
from pipe.web.actions.session import (
    SessionDeleteAction,
    SessionGetAction,
    SessionInstructionAction,
    SessionStartAction,
    SessionStopAction,
)
from pipe.web.actions.session_management import (
    SessionsDeleteAction,
    SessionsDeleteBackupAction,
    SessionsListBackupAction,
    SessionsMoveToBackup,
)
from pipe.web.actions.session_tree import SessionTreeAction
from pipe.web.actions.settings import SettingsGetAction
from pipe.web.actions.therapist import ApplyDoctorModificationsAction
from pipe.web.actions.turn import SessionForkAction, SessionTurnsGetAction
from pipe.web.exceptions import HttpException
from pipe.web.request_context import RequestContext
from pipe.web.requests.base_request import BaseRequest
from pipe.web.responses import ApiResponse
from pydantic import BaseModel, ValidationError


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def _convert_keys_to_snake(data: dict | list | Any) -> dict | list | Any:
    """Recursively convert all dict keys from camelCase to snake_case."""
    if isinstance(data, dict):
        return {_camel_to_snake(k): _convert_keys_to_snake(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_keys_to_snake(item) for item in data]
    else:
        return data


def _convert_keys_to_camel(data: dict | list | Any) -> dict | list | Any:
    """Recursively convert all dict keys from snake_case to camelCase."""
    if isinstance(data, dict):
        return {_snake_to_camel(k): _convert_keys_to_camel(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_keys_to_camel(item) for item in data]
    else:
        return data


class ActionDispatcher:
    """Dispatches actions to appropriate handlers based on route patterns."""

    def __init__(
        self,
        search_l2_action: SearchL2Action,
        ls_action: LsAction,
        index_files_action: IndexFilesAction,
    ):
        self.search_l2_action = search_l2_action
        self.ls_action = ls_action
        self.index_files_action = index_files_action

    def dispatch(
        self,
        action: str,
        params: dict,
        request_data: Request | None = None,
    ) -> tuple[dict | Response | Any, int] | Response:
        """Dispatch an action to the appropriate handler.

        Args:
            action: The action path (e.g., "session/{session_id}")
            params: Parameters extracted from the URL
            request_data: The Flask request object

        Returns:
            A tuple of (response_data, status_code) or Response object
        """
        method = request_data.method if request_data else "GET"

        # Convert request body from camelCase to snake_case
        converted_request_data = request_data
        if request_data and request_data.is_json:
            try:
                original_json = request_data.get_json(silent=True)
                if original_json:
                    converted_json = _convert_keys_to_snake(original_json)

                    # Create a wrapper that stores the converted data
                    class RequestWrapper:
                        def __init__(
                            self, original_request: Request, converted_data: dict | Any
                        ):
                            self._original = original_request
                            self._converted_data = converted_data
                            self.method = original_request.method
                            self.is_json = original_request.is_json

                        def get_json(self, *args, **kwargs):
                            return self._converted_data

                        def __getattr__(self, name):
                            return getattr(self._original, name)

                    converted_request_data = RequestWrapper(
                        request_data, converted_json
                    )  # type: ignore
            except Exception:
                # If JSON parsing fails, just use the original request
                pass

        route_map = [
            ("session_tree", "GET", SessionTreeAction),
            ("settings", "GET", SettingsGetAction),
            ("session/start", "POST", SessionStartAction),
            ("session/compress", "POST", CreateCompressorSessionAction),
            ("session/compress/{session_id}/approve", "POST", ApproveCompressorAction),
            ("session/compress/{session_id}/deny", "POST", DenyCompressorAction),
            ("therapist", "POST", CreateTherapistSessionAction),
            ("doctor", "POST", ApplyDoctorModificationsAction),
            ("session_management/archives", "POST", SessionsMoveToBackup),
            ("session_management/archives", "GET", SessionsListBackupAction),
            ("session_management/archives", "DELETE", SessionsDeleteBackupAction),
            ("session_management/sessions", "DELETE", SessionsDeleteAction),
            ("session/{session_id}/instruction", "POST", SessionInstructionAction),
            ("session/{session_id}/stop", "POST", SessionStopAction),
            ("session/{session_id}/meta", "PATCH", SessionMetaEditAction),
            (
                "session/{session_id}/hyperparameters",
                "PATCH",
                HyperparametersEditAction,
            ),
            ("session/{session_id}/hyperparameters", "POST", HyperparametersEditAction),
            (
                "session/{session_id}/multi-step-reasoning",
                "PATCH",
                MultiStepReasoningEditAction,
            ),
            ("session/{session_id}/todos", "PATCH", TodosEditAction),
            ("session/{session_id}/todos", "DELETE", TodosDeleteAction),
            (
                "session/{session_id}/references/{reference_index}/persist",
                "PATCH",
                ReferencePersistEditAction,
            ),
            (
                "session/{session_id}/references/{reference_index}/toggle",
                "PATCH",
                ReferenceToggleDisabledAction,
            ),
            (
                "session/{session_id}/references/{reference_index}/ttl",
                "PATCH",
                ReferenceTtlEditAction,
            ),
            ("session/{session_id}/references", "PATCH", ReferencesEditAction),
            ("session/{session_id}/turn/{turn_index}", "PATCH", TurnEditAction),
            ("session/{session_id}/turns", "GET", SessionTurnsGetAction),
            ("session/{session_id}/turn/{turn_index}", "DELETE", TurnDeleteAction),
            ("session/{session_id}/fork/{fork_index}", "POST", SessionForkAction),
            ("session/{session_id}", "GET", SessionGetAction),
            ("session/{session_id}", "DELETE", SessionDeleteAction),
            ("fs/roles", "GET", GetRolesAction),
            ("fs/procedures", "GET", GetProceduresAction),
            ("fs/search_l2", "POST", self.search_l2_action),
            ("fs/search", "POST", SearchSessionsAction),
            ("fs/ls", "POST", self.ls_action),
            ("fs/index_files", "POST", self.index_files_action),
        ]

        for route_pattern, route_method, action_class in route_map:
            if route_method != method:
                continue

            match, extracted_params = self._match_route(route_pattern, action, params)

            if match:
                # Debug: print which route matched
                action_name = (
                    action_class.__name__
                    if isinstance(action_class, type)
                    else action_class.__class__.__name__
                )
                import sys

                print(
                    f"DEBUG: Route matched - pattern={route_pattern}, "
                    f"method={route_method}, action={action_name}, "
                    f"params={extracted_params}"
                )
                sys.stdout.flush()
                try:
                    # Check if action uses BaseRequest for unified validation
                    request_model = (
                        getattr(action_class, "request_model", None)
                        if isinstance(action_class, type)
                        else None
                    )
                    validated_request = None

                    if request_model and issubclass(request_model, BaseRequest):
                        # Laravel/Struts style: validate before reaching the action
                        body_data = None
                        if converted_request_data and converted_request_data.is_json:
                            body_data = converted_request_data.get_json(silent=True)

                        try:
                            validated_request = request_model.create_with_path_params(
                                path_params=extracted_params,
                                body_data=body_data,
                            )
                        except ValidationError as e:
                            # Validation failed before reaching action
                            error_messages = [
                                (
                                    f"{'.'.join(str(loc) for loc in err['loc'])}: "
                                    f"{err['msg']}"
                                )
                                for err in e.errors()
                            ]
                            return {
                                "success": False,
                                "message": "; ".join(error_messages),
                            }, 422

                    # Create RequestContext for backward compatibility
                    request_context = RequestContext(
                        path_params=extracted_params,
                        request_data=converted_request_data,
                        body_model=(
                            getattr(action_class, "body_model", None)
                            if isinstance(action_class, type)
                            else None
                        ),
                    )

                    if isinstance(action_class, type):
                        # Pass validated request if available
                        if validated_request:
                            action_instance = action_class(
                                params=extracted_params,
                                request_data=converted_request_data,
                                request_context=request_context,
                                validated_request=validated_request,
                            )
                        else:
                            action_instance = action_class(
                                params=extracted_params,
                                request_data=converted_request_data,
                                request_context=request_context,
                            )
                    else:
                        # For pre-instantiated actions (like fs actions)
                        action_instance = action_class
                        action_instance.params = extracted_params
                        action_instance.request_data = converted_request_data
                        action_instance.request = request_context

                    # Execute action
                    result = action_instance.execute()

                    # Handle different return types
                    if isinstance(result, Response):
                        # Flask Response object (e.g., streaming response)
                        return result
                    elif isinstance(result, tuple):
                        # Legacy: (dict, status_code) or (ApiResponse, status_code)
                        response_data, status_code = result
                        if isinstance(response_data, BaseModel):
                            # Convert Pydantic model to dict, then to camelCase
                            response_data = _convert_keys_to_camel(
                                response_data.model_dump()
                            )
                        elif isinstance(response_data, dict):
                            # Convert snake_case to camelCase
                            response_data = _convert_keys_to_camel(response_data)
                        return response_data, status_code
                    else:
                        # New pattern: Action returns data directly
                        # Dispatcher wraps it in ApiResponse
                        response = ApiResponse(success=True, data=result)
                        response_dict = response.model_dump()
                        response_dict = _convert_keys_to_camel(response_dict)
                        return response_dict, 200

                except HttpException as e:
                    # Custom HTTP exceptions with specific status codes
                    response = ApiResponse(success=False, message=e.message)
                    return _convert_keys_to_camel(response.model_dump()), e.status_code
                except Exception as e:
                    # Unexpected errors -> 500
                    response = ApiResponse(success=False, message=str(e))
                    return _convert_keys_to_camel(response.model_dump()), 500

        return {"message": f"Unknown action: {action} with method {method}"}, 404

    def _match_route(
        self, route_pattern: str, action: str, params: dict
    ) -> tuple[bool, dict]:
        """Match a route pattern against an action path.

        Args:
            route_pattern: The pattern to match (e.g., "session/{session_id}")
            action: The action path to match against
            params: Existing parameters to merge with extracted ones

        Returns:
            A tuple of (matched: bool, params: dict)
        """
        extracted_params = dict(params)
        pattern_parts = route_pattern.split("/")
        action_parts = action.split("/")

        # Flexible matching to allow path-like parameters
        # (e.g. session IDs containing '/').
        match = True
        pi = 0
        ai = 0

        while pi < len(pattern_parts) and ai < len(action_parts):
            pp = pattern_parts[pi]
            if pp.startswith("{") and pp.endswith("}"):
                param_name = pp[1:-1]
                # If this is the last pattern part, capture the rest
                if pi == len(pattern_parts) - 1:
                    extracted_params[param_name] = "/".join(action_parts[ai:])
                    ai = len(action_parts)
                    pi += 1
                    break

                # Find the next literal pattern part to know where to stop
                next_literal = None
                for nxt in pattern_parts[pi + 1 :]:
                    if not (nxt.startswith("{") and nxt.endswith("}")):
                        next_literal = nxt
                        break

                if next_literal is None:
                    # No following literal, capture the rest
                    extracted_params[param_name] = "/".join(action_parts[ai:])
                    ai = len(action_parts)
                    pi = len(pattern_parts)
                    break

                # Find the index in action_parts where next_literal appears
                found_index = None
                for look in range(ai, len(action_parts)):
                    if action_parts[look] == next_literal:
                        found_index = look
                        break

                if found_index is None:
                    match = False
                    break

                # Capture action parts from ai up to found_index as the param
                extracted_params[param_name] = "/".join(action_parts[ai:found_index])
                ai = found_index
                pi += 1
                continue

            # literal must match exactly
            if action_parts[ai] != pp:
                match = False
                break

            pi += 1
            ai += 1

        # If we've consumed pattern parts, ai should have consumed all action parts
        if pi != len(pattern_parts) or ai != len(action_parts):
            match = False

        return match, extracted_params


# Global dispatcher instance (will be set by app.py)
_dispatcher: ActionDispatcher | None = None


def get_dispatcher() -> ActionDispatcher:
    """Get the global dispatcher instance."""
    if _dispatcher is None:
        raise RuntimeError("Dispatcher not initialized. Call init_dispatcher first.")
    return _dispatcher


def init_dispatcher(
    search_l2_action: SearchL2Action,
    ls_action: LsAction,
    index_files_action: IndexFilesAction,
) -> ActionDispatcher:
    """Initialize the global dispatcher instance."""
    global _dispatcher
    _dispatcher = ActionDispatcher(search_l2_action, ls_action, index_files_action)
    return _dispatcher


def dispatch_action(
    action: str,
    params: dict,
    request_data: Request | None = None,
) -> tuple[dict | Response | Any, int] | Response:
    """Dispatch an action using the global dispatcher.

    This is a convenience function for backward compatibility.
    """
    return get_dispatcher().dispatch(action, params, request_data)
