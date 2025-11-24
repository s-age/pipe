from pipe.core.models.procedure import ProcedureOption
from pipe.core.repositories.procedure_repository import ProcedureRepository


class ProcedureService:
    def __init__(self, procedure_repository: ProcedureRepository):
        self.procedure_repository = procedure_repository

    def get_all_procedure_options(self) -> list[ProcedureOption]:
        return self.procedure_repository.get_all_procedure_options()
