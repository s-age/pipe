from pydantic import BaseModel


class EditReferencePersistRequest(BaseModel):
    persist: bool
