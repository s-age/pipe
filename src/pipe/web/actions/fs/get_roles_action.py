"""Get roles action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.service_container import get_role_service


class GetRolesAction(BaseAction):
    """Action to get all available role options."""

    def execute(self) -> list[dict[str, str]]:
        role_options = get_role_service().get_all_role_options()
        return [option.model_dump() for option in role_options]
