# encoding=utf-8
# 此项目的顶级类
from request.request import ReqPHP
from common.log import log
import socket
import json

class UpdateStatus():

    def __init__(self, identifier, user, rulename,  file_type:int = 0, isupload: bool=False):
        self.identifier = identifier
        self.user = user     # 后台用户
        self.rule = rulename
        self.file_type: int = file_type
        # self.script_status = 0  #  0: 处理失败   1: 处理中   2: 处理成功
        
        #  10: 等待资源  5: 处理失败   1: 处理中   2: 处理成功    1: 审核通过  4: 审核失败   3: 需要审核 ， 6 等待旋转, 7: 停止处理
        self.status = 0   
        self.msg = ""
        self.isupload = isupload
        self.size = 0
        self.resource_id = 0

    def _common(self):
        php = ReqPHP()
        log.info(self.__dict__, 2)
        data = json.dumps(self.__dict__)
        resp = php.req_update_status(data)
        return resp["code"] == 0

    def success(self, msg="视频处理完成"):
        self.status = 2
        self.msg = msg + " - hostname: " + socket.gethostname()
        return self._common()

    def fail(self, msg):
        self.status = 5
        self.msg = msg + " - hostname: " + socket.gethostname()
        return self._common()

    def processing(self, msg, size: int= 0):
        self.status = 1
        self.size = size
        self.msg = msg + " - hostname: " + socket.gethostname()
        return self._common()
    
    def audit(self, resource_id: int = 0):
        # 需要审核
        self.msg = "需要审核"
        self.status = 3
        self.resource_id = resource_id
        return self._common()
    
    def rotate(self, msg):
        # 需要审核
        self.msg = msg
        self.status = 6
        return self._common()
    
    def stop(self):
        # 需要审核
        self.msg = "停止处理"
        self.status = 7
        return self._common()
    
