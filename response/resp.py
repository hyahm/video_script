# -*- coding: UTF-8 -*-

import json


class Response:
    def __init__(self):
        self.code = 0   # 状态码
        self.name = ""  # 文件名
        self.msg = ""   # 信息

    def _req_data(self):
        return json.dumps({
            "code": self.code,
            "msg": self.msg
        })

    def no_data(self):
        self.code = 1
        self.msg = "No parameters"
        return self._req_data()

    def success(self):
        self.msg = "Successful request"
        return self._req_data()

    def not_json(self):
        self.code = 2
        self.msg = "Parameter invaild"
        return self._req_data()

    def is_process(self):
        self.code = 3
        self.msg = "Processing: %s" % self.name
        return self._req_data()


resp = Response()
