from typing import Optional
from pydantic import BaseModel

class Reference(BaseModel):
    path: str
    disabled: bool = False
    ttl: Optional[int] = None