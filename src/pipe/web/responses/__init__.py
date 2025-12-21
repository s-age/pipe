from typing import Generic, TypeVar

from pipe.core.models.base import CamelCaseModel

DataT = TypeVar("DataT")


class ApiResponse(CamelCaseModel, Generic[DataT]):
    success: bool
    message: str | None = None
    data: DataT | None = None
