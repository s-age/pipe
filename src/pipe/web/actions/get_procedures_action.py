from pathlib import Path

from flask import Request
from pipe.core.repositories.procedure_repository import ProcedureRepository
from pipe.core.services.procedure_service import ProcedureService


class GetProceduresAction:
    def __init__(self, params: dict, request_data: Request | None = None):
        self.params = params
        self.request_data = request_data
        procedures_root_dir = Path(__file__).parent.parent.parent.parent.parent / "procedures"
        self.procedure_repository = ProcedureRepository(procedures_root_dir)
        self.procedure_service = ProcedureService(self.procedure_repository)

    def execute(self) -> tuple[list[dict[str, str]], int]:
        try:
            procedure_options = self.procedure_service.get_all_procedure_options()
            procedure_options_dicts: list[dict[str, str]] = []
            for option in procedure_options:
                dumped_option: dict[str, str] = option.model_dump()
                procedure_options_dicts.append(dumped_option)
            return procedure_options_dicts, 200
        except Exception as e:
            return [{"message": str(e)}], 500