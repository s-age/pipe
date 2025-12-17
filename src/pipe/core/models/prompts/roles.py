from typing import TYPE_CHECKING

from pipe.core.models.base import CamelCaseModel

if TYPE_CHECKING:
    from pipe.core.repositories.resource_repository import ResourceRepository


class PromptRoles(CamelCaseModel):
    description: str
    definitions: list[str]

    @classmethod
    def build(
        cls, roles: list[str], resource_repository: "ResourceRepository"
    ) -> "PromptRoles":
        """Builds the PromptRoles component.

        Args:
            roles: List of role file paths.
            resource_repository: Repository for reading resources with path validation.

        Returns:
            A PromptRoles instance with role definitions loaded.
        """
        from pipe.core.collections.roles import RoleCollection

        return cls(
            description="The following are the roles for this session.",
            definitions=RoleCollection(roles).get_for_prompt(resource_repository),
        )
