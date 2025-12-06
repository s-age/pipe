from typing import Any

from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, model_validator


class EditReferencePersistRequest(BaseModel):
    persist: bool

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
