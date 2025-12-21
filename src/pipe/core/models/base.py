from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Base model that automatically converts snake_case fields to camelCase aliases."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
