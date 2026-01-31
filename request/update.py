# encoding=utf-8
from enum import IntEnum
from lib.base import HugoData

#  10: 等待资源  5: 处理失败   1: 处理中   2: 处理成功    1: 审核通过  4: 审核失败   3: 需要审核 ， 6 等待旋转
class Status(IntEnum):
    WatingResource = 10
    Failed = 5
    Processing = 1
    Success = 2
    AuditSuccess = 1
    AuditFailed = 4
    NeedAudit = 3
    Rotating = 6

class UpdateStats():
    def __init__(self, status: Status, msg: str, data: HugoData) -> None:
        self.identifier: str = data.identifier
        self.rule :str= data.rule
        self.user: str = data.user
        self.status: int = status
        self.msg: str = msg