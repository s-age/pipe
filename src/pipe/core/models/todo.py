from pydantic import BaseModel, model_validator


class TodoItem(BaseModel):
    title: str
    description: str = ""
    checked: bool = False

    @model_validator(mode="before")
    @classmethod
    def _map_item_to_title(cls, data: dict[str, str | bool]) -> dict[str, str | bool]:
        if "item" in data:
            data["title"] = data.pop("item")
        return data
