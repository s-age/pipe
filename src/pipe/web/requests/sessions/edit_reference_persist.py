from typing import Any, ClassVar

from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import model_validator


class EditReferencePersistRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id", "reference_index"]

    # Path parameters (from URL)
    session_id: str
    reference_index: int

    # Body field
    persist: bool

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
