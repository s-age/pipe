from pathlib import Path

from flask import Request
from pipe.core.repositories.role_repository import RoleRepository
from pipe.core.services.role_service import RoleService


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
