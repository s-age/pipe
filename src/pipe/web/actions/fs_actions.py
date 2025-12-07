"""File system related actions."""

from pathlib import Path

from flask import Request
from pipe.core.models.file_search import LsRequest, SearchL2Request
from pipe.core.repositories.procedure_repository import ProcedureRepository
from pipe.core.repositories.role_repository import RoleRepository
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.core.services.procedure_service import ProcedureService
from pipe.core.services.role_service import RoleService
from pipe.web.actions.base_action import BaseAction


class SearchSessionsAction(BaseAction):
    """Action that searches session files for a query and returns session_id/title."""

    body_model = None  # Will validate manually with SearchSessionsRequest

    def execute(self) -> dict[str, list[dict[str, str]]]:
        # Lazy import app-level objects to avoid circular imports
        from pipe.web.service_container import get_session_service

        request_json = {}
        if self.request_data and self.request_data.is_json:
            try:
                request_json = self.request_data.get_json(force=True)
            except Exception:
                request_json = {}

        # Validate request shape using a pydantic request model
        from pipe.web.requests.search_sessions import SearchSessionsRequest

        req = SearchSessionsRequest(**(request_json or {}))

        query = req.query.strip()

        sessions_dir = get_session_service().repository.sessions_dir

        # Delegate the search logic to the service layer for reusability
        from pipe.core.services.search_sessions_service import (
            SearchSessionsService,
        )

        svc = SearchSessionsService(sessions_dir)
        matches = svc.search(query)

        return {"results": matches}


class SearchL2Action(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,  # Accept additional kwargs from dispatcher
    ):
        super().__init__(params, request_data, **kwargs)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> dict:
        request_data = self.request_data.get_json()
        request = SearchL2Request(**request_data)
        response = self.file_indexer_service.search_l2_data(
            request.current_path_list, request.query
        )
        return response.model_dump()


class LsAction(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,  # Accept additional kwargs from dispatcher
    ):
        super().__init__(params, request_data, **kwargs)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> dict:
        request_data = self.request_data.get_json()
        request = LsRequest(**request_data)
        response_entries = self.file_indexer_service.get_ls_data(
            request.final_path_list
        )
        # LsResponseモデルに適合させるためにリストをラップ
        from pipe.core.models.file_search import LsResponse

        response = LsResponse(entries=response_entries)
        return response.model_dump()


class IndexFilesAction(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,  # Accept additional kwargs from dispatcher
    ):
        super().__init__(params, request_data, **kwargs)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> dict[str, str]:
        self.file_indexer_service.create_index()
        return {"message": "Index created successfully"}


class GetRolesAction(BaseAction):
    """Action to get all available role options."""

    def __init__(
        self,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,  # Accept additional kwargs from dispatcher
    ):
        super().__init__(params, request_data, **kwargs)
        roles_root_dir = Path(__file__).parent.parent.parent.parent.parent / "roles"
        self.role_repository = RoleRepository(roles_root_dir)
        self.role_service = RoleService(self.role_repository)

    def execute(self) -> list[dict[str, str]]:
        role_options = self.role_service.get_all_role_options()
        role_options_dicts: list[dict[str, str]] = []
        for option in role_options:
            dumped_option: dict[str, str] = option.model_dump()
            role_options_dicts.append(dumped_option)
        return role_options_dicts


class GetProceduresAction(BaseAction):
    """Action to get all available procedure options."""

    def __init__(
        self,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,  # Accept additional kwargs from dispatcher
    ):
        super().__init__(params, request_data, **kwargs)
        procedures_root_dir = (
            Path(__file__).parent.parent.parent.parent.parent / "procedures"
        )
        self.procedure_repository = ProcedureRepository(procedures_root_dir)
        self.procedure_service = ProcedureService(self.procedure_repository)

    def execute(self) -> list[dict[str, str]]:
        procedure_options = self.procedure_service.get_all_procedure_options()
        procedure_options_dicts: list[dict[str, str]] = []
        for option in procedure_options:
            dumped_option: dict[str, str] = option.model_dump()
            procedure_options_dicts.append(dumped_option)
        return procedure_options_dicts
