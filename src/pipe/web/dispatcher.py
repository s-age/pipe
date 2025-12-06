"""Central action dispatcher for routing requests to action handlers."""

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
    TurnDeleteAction,
    TurnEditAction,
)
from pipe.web.actions.file_search_actions import (
    IndexFilesAction,
    LsAction,
    SearchL2Action,
)
from pipe.web.actions.meta_actions import TodosDeleteAction, TodosEditAction
from pipe.web.actions.search_sessions_action import SearchSessionsAction
from pipe.web.actions.session_actions import (
    SessionDeleteAction,
    SessionForkAction,
    SessionGetAction,
    SessionInstructionAction,
    SessionRawAction,
    SessionStartAction,
)
from pipe.web.actions.session_management_actions import (
    SessionsDeleteBackupAction,
    SessionsListBackupAction,
    SessionsMoveToBackup,
)
from pipe.web.actions.session_tree_action import SessionTreeAction
from pipe.web.actions.settings_actions import SettingsGetAction
from pipe.web.actions.therapist_actions import ApplyDoctorModificationsAction
from pipe.web.actions.turn_actions import SessionTurnsGetAction


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
    ) -> tuple[dict | Response, int]:
        """Dispatch an action to the appropriate handler.

        Args:
            action: The action path (e.g., "session/{session_id}")
            params: Parameters extracted from the URL
            request_data: The Flask request object

        Returns:
            A tuple of (response_data, status_code)
        """
        method = request_data.method if request_data else "GET"

        route_map = [
            ("session_tree", "GET", SessionTreeAction),
            ("settings", "GET", SettingsGetAction),
            ("session/start", "POST", SessionStartAction),
            ("compress", "POST", CreateCompressorSessionAction),
            ("compress/{session_id}/approve", "POST", ApproveCompressorAction),
            ("compress/{session_id}/deny", "POST", DenyCompressorAction),
            ("therapist", "POST", CreateTherapistSessionAction),
            ("doctor", "POST", ApplyDoctorModificationsAction),
            ("sessions/archives", "POST", SessionsMoveToBackup),
            ("sessions/archives", "GET", SessionsListBackupAction),
            ("sessions/archives", "DELETE", SessionsDeleteBackupAction),
            ("session/{session_id}/raw", "GET", SessionRawAction),
            ("session/{session_id}/instruction", "POST", SessionInstructionAction),
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
            (
                "session/{session_id}/multi-step-reasoning",
                "POST",
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
            ("roles", "GET", GetRolesAction),
            ("procedures", "GET", GetProceduresAction),
            ("search_l2", "POST", self.search_l2_action),
            ("search", "POST", SearchSessionsAction),
            ("ls", "POST", self.ls_action),
            ("index_files", "POST", self.index_files_action),
        ]

        for route_pattern, route_method, action_class in route_map:
            if route_method != method:
                continue

            match, extracted_params = self._match_route(route_pattern, action, params)

            if match:
                try:
                    if isinstance(action_class, type):
                        action_instance = action_class(
                            params=extracted_params,
                            request_data=request_data,
                        )
                    else:
                        action_instance = action_class
                        action_instance.params = extracted_params
                        action_instance.request_data = request_data
                    return action_instance.execute()
                except Exception as e:
                    return {"message": str(e)}, 500

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
) -> tuple[dict | Response, int]:
    """Dispatch an action using the global dispatcher.

    This is a convenience function for backward compatibility.
    """
    return get_dispatcher().dispatch(action, params, request_data)
