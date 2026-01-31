# encoding=utf-8
from lib.base import filed_to_str, filed_to_int
from pydantic import BaseModel

class Ftp(BaseModel):
    host: str = ""
    port: int = 0
    user: str = ""
    pwd: str = ""
    dir: str = ""