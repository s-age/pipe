from typing import Any

from pydantic import BaseModel, model_validator


class TodoItem(BaseModel):
    title: str
    description: str = ""
    checked: bool = False

    @model_validator(mode="before")
    @classmethod
    def _map_item_to_title(cls, data: Any) -> Any:
        if isinstance(data, dict) and "item" in data:
            data["title"] = data.pop("item")
        return data
