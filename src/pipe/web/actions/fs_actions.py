"""File system related actions."""

from pathlib import Path
from typing import Any

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

    def execute(self) -> tuple[dict[str, Any], int]:
        try:
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
            from pydantic import ValidationError

            try:
                req = SearchSessionsRequest(**(request_json or {}))
            except ValidationError as ve:
                # Return 400 with validation errors (client mistake)
                return {"message": str(ve), "errors": ve.errors()}, 400

            query = req.query.strip()

            sessions_dir = get_session_service().repository.sessions_dir

            # Delegate the search logic to the service layer for reusability
            from pipe.core.services.search_sessions_service import (
                SearchSessionsService,
            )

            svc = SearchSessionsService(sessions_dir)
            matches = svc.search(query)

            return {"results": matches}, 200
        except Exception as e:
            return {"message": str(e)}, 500


class SearchL2Action(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict,
        request_data: Request | None = None,
    ):
        super().__init__(params, request_data)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> tuple[dict, int]:
        try:
            request_data = self.request_data.get_json()
            request = SearchL2Request(**request_data)
            response = self.file_indexer_service.search_l2_data(
                request.current_path_list, request.query
            )
            return response.model_dump(), 200
        except Exception as e:
            return {"error": str(e)}, 400


class LsAction(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict,
        request_data: Request | None = None,
    ):
        super().__init__(params, request_data)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> tuple[dict, int]:
        try:
            request_data = self.request_data.get_json()
            request = LsRequest(**request_data)
            response_entries = self.file_indexer_service.get_ls_data(
                request.final_path_list
            )
            # LsResponseモデルに適合させるためにリストをラップ
            from pipe.core.models.file_search import LsResponse

            response = LsResponse(entries=response_entries)
            return response.model_dump(), 200
        except Exception as e:
            return {"error": str(e)}, 400


class IndexFilesAction(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict,
        request_data: Request | None = None,
    ):
        super().__init__(params, request_data)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> tuple[dict, int]:
        try:
            self.file_indexer_service.create_index()
            return {"message": "Index created successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500


class GetRolesAction:
    def __init__(self, params: dict, request_data: Request | None = None):
        self.params = params
        self.request_data = request_data
        roles_root_dir = Path(__file__).parent.parent.parent.parent.parent / "roles"
        self.role_repository = RoleRepository(roles_root_dir)
        self.role_service = RoleService(self.role_repository)

    def execute(self) -> tuple[list[dict[str, str]], int]:
        try:
            role_options = self.role_service.get_all_role_options()
            role_options_dicts: list[dict[str, str]] = []
            for option in role_options:
                dumped_option: dict[str, str] = option.model_dump()
                role_options_dicts.append(dumped_option)
            return role_options_dicts, 200
        except Exception as e:
            return [{"message": str(e)}], 500


class GetProceduresAction:
    def __init__(self, params: dict, request_data: Request | None = None):
        self.params = params
        self.request_data = request_data
        procedures_root_dir = (
            Path(__file__).parent.parent.parent.parent.parent / "procedures"
        )
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
