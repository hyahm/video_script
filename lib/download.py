# encoding=utf-8

from lib.base import filed_to_str
from typing import Dict
from lib.ftp import Ftp
# download的数据结构

# class Download():
#     def __init__(self, **kargs) -> None:
#         self.name = filed_to_str(kargs, "name")
#         self.user = filed_to_str(kargs, "user")  # 用户
#         self.ftp_user = filed_to_str(kargs, "ftp_user")
#         self.filename= filed_to_str(kargs, "filename")  # 视频文件
#         self.identifier= filed_to_str(kargs, "identifier")   # 唯一标识符
#         self.project= filed_to_str(kargs, "project")   # 项目文件夹
#         self.rule= filed_to_str(kargs, "rule")   # 规则名
#         self.resource_ftp: Dict = {}

    
#     def set_ftp(self, kargs: Dict) -> None:
#         # CONFIG["ftp_host"] = "127.0.0.1"
#         # CONFIG["ftp_port"] = 21
#         # CONFIG["ftp_user"] = "admin"
#         # CONFIG["ftp_pwd"] = "poaihopdshogiho234"
#         # CONFIG["ftp_dir"] = "/"  # FTP的路径
#         self.resource_ftp = Ftp(kargs).__dict__
