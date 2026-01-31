# encoding=utf-8

from optparse import Option
from request.request import php
from pydantic import BaseModel
from typing import TypeVar, Dict
from lib.base import filed_to_str
from typing import Optional

class Project(BaseModel):
    host: str = ""
    download_path: str = ""
    play_path: str = ""
    thumbnail_path: str = ""
    cover_path: str = ""
    dir: str = ""
    preview_path: str = ""
    play_url: str = ""
    thumbnail_url: str = ""
    cover_url: str = ""
    preview_url: str = ""
    download_url: str = ""

class Server(BaseModel):
    id: int = 0
    server_ip: str = ""
    title: str = ""
    server_type: int = 0
    endpoint: str = ""
    access_key_id: str = ""
    access_key_secret: str = ""
    bucket: str = ""
    region: str = ""

class ServerInfo(BaseModel):
    project: Project = Project(**{})
    server: Server = Server(**{})



S = TypeVar('S', ServerInfo , bool)
def get_server_info(project_id: int) -> S:
    info = php.get_remote_server_info(project_id)
    if info["code"] == 0:
        return ServerInfo(**info["data"])
    return False
