# encoding=utf-8


# 第三方接口
from request.request import ReqPHP
from common.log import log
from request.status import UpdateStatus
from lib.newrule import get_rule
from lib.data import HugoData


class Third(ReqPHP):
    # 第三方接口
    def __init__(self, identifier, user, rule, isupload):
        super().__init__()
        # json文件内容传递过来, 不应该传过来，应该传给参数
        self._error_msg = ["操作成功", "参数错误",
                           "标题重复", "identify重复", "子分类不存在", "其他错误"]
        self._error_name = ".json"
        self._user = user
        self._overwrite = False
        self.delete = False
        self.us = UpdateStatus(identifier, user, rule, isupload=isupload)

    def get_error_name(self):
        return self._error_name

    def request_api(self, url, data: dict) -> bool:
        if isinstance(data, HugoData):
            data.dryrun = False
            data = data.dict()
        return self.request(url, data)

    def check_title_and_identifier(self, data):
        # 检查标题或id重复的接口， 与上面类似
        # 获取 url， 不用下载
        rule = get_rule(self._user, data["rule"])
        if not rule:
            self._error_name = ".json-rule_error"
            return False
        url = rule.api_path
        data["dryrun"] = True
        resp = self.request(url, data)
        log.debug(resp)
        if not resp:
            if self.error_data():
                # 如果是接口返回了错误信息， 返回
                code = self.error_data()["code"]
                if code == 2:
                    self._error_name = ".json-title_duplicate"
                elif code == 3:
                    self._error_name = ".json-identifier_duplicate"
                else:
                    self._error_name = ".json-api_error"
                return False
        return True
