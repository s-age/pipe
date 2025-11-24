from pipe.core.models.role import RoleOption
from pipe.core.repositories.role_repository import RoleRepository


class RoleService:
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def get_all_role_options(self) -> list[RoleOption]:
        return self.role_repository.get_all_role_options()
