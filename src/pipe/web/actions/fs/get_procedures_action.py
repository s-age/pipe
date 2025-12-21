"""Get procedures action."""

from pipe.web.action_responses import ProceduresResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.service_container import get_procedure_service


class GetProceduresAction(BaseAction):
    """Action to get all available procedure options."""

    def execute(self) -> ProceduresResponse:
        procedure_options = get_procedure_service().get_all_procedure_options()
        return ProceduresResponse(procedures=procedure_options)
