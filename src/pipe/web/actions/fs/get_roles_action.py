"""Get roles action."""

from pipe.web.action_responses import RolesResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.service_container import get_role_service


class GetRolesAction(BaseAction):
    """Action to get all available role options."""

    def execute(self) -> RolesResponse:
        role_options = get_role_service().get_all_role_options()
        return RolesResponse(roles=role_options)
