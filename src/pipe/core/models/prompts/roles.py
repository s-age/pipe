from pydantic import BaseModel


class PromptRoles(BaseModel):
    description: str
    definitions: list[str]

    @classmethod
    def build(cls, roles: list[str], project_root: str) -> "PromptRoles":
        """Builds the PromptRoles component."""
        from pipe.core.collections.roles import RoleCollection

        return cls(
            description="The following are the roles for this session.",
            definitions=RoleCollection(roles).get_for_prompt(project_root),
        )
