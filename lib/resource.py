# encoding=utf-8
from pydantic import BaseModel

class ResourceServer(BaseModel):
    name: str = ""
    user: str = "root"
    ip: str = ""
    id: int = 0
    domain: str = ""
    root: str = ""
        