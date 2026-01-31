# encoding=utf-8
from typing import Dict
from common.log import log
import json
import requests
from request.api import save, save_image, get_rule, check_cat_and_subcat, exsit_identifier, get_server_info
from request.api import update_json_status, get_resource, get_user_key, get_user_by_ftp_user,upload_callback
from request.api import get_project

class ReqPHP:
    def __init__(self):
        self._headers = {"Content-Type": "application/json"}
        self._error = ""
        self._errorData = None
        self._successData = None

    def error(self):
        return self._error

    def error_data(self):
        return self._errorData

    def successData(self):
        return self._successData


    def post_callback(self, id: int, data: dict):
        """
        id: upload_uid
        data: {
            ""
        }

        """
        return  self._request(
            upload_callback.format(id), method="post")

    def _request(self, url, data=None, timeout=30, method="POST"):
        data = self._request_call(url, data, timeout, method)
        # log.info(data)
        return data
    #
    def _request_call(self, url: str, data=None, timeout=30, method="POST"):
        """
            请求
              return:   

                response, 
                status: 
                switch：  2： 成功，response 
                         1：   errormsg
                         0：   connect error（status code）
        """
        log.info(url, 2)
        r = None
        try:
            str_data = self._format_to_json_str(data)
            if not str_data:
                return {"code": 400, "msg": "data error"}
            log.info(str_data)
            if method.upper() == "POST":
                r = requests.post(url, data=str_data,
                                    timeout=timeout, headers=self._headers)
            elif method.upper() == "GET":
                r = requests.get(url, timeout=timeout,
                                    headers=self._headers)
            else:
                return {"code": 405, "msg": "method not support"}
            if r.status_code == 200:
                log.info(r.json())
                return r.json()
            else:
                log.info(r.text)
                return {"code": r.status_code, "msg": r.text}
        except Exception as e:
            if len(e.args) > 0:
                return {"code": 500, "msg": e.args[0]}
            else:
                return {"code": 500, "msg": str(e)}

    def request(self, url, data):
        return self._request(url, data)


    def req_update_status(self, data, url=update_json_status):
        return self._request(url, data)

    def save_to_resource(self, data, url=save) -> bool:
        # 修改处理状态
        #    data  =   {
        #   "identifier": "test_1",
        #   "script_status": 0,  0: 处理失败  | 1: 处理中 | 2: 处理成功 |3:未处理
        #   "msg": "zhh"
        # }
        res = self._request(url, data)
        return res["code"] == 0
    
    def save_image_to_resource(self, data, url=save_image) -> bool:
        # 修改处理状态
        #    data  =   {
        #   "identifier": "test_1",
        #   "script_status": 0,  0: 处理失败  | 1: 处理中 | 2: 处理成功 |3:未处理
        #   "msg": "zhh"
        # }
        res = self._request(url, data)
        return res["code"] == 0

    def get_new_rule(self, user, rulename, rule_type: int=0, url=get_rule):
        # 获取规则, rule_type:  0 视频    1 图片
        data = {
            "user": user,
            "rulename": rulename,
            "rule_type": rule_type
        }
        return self._request(url, data)


    def exsit_identifier(self, identifier, url=exsit_identifier) -> bool: 
        # 获取规则, rule_type:  0 视频    1 图片
       return self._request(url + identifier, method="get")["code"] == 0
        # if status == 2:
        #     return True
        # return  False

    # 试凑存在分类， 返回 bool
    def get_project_by_cat_and_subcat(self, cat: str, subcat: str, user: str, url=check_cat_and_subcat) -> bool:
        data = {
            "category": cat,
            "subcategory": subcat,
            "user": user
        }
        res = self._request(url, data=data)
        return res["code"] == 0

    def get_resource(self, url=get_resource) -> Dict:
        res = self._request(url)
        log.info(res)
        if res["code"] != 0:
            return {}
        return res["data"]
    
    def get_project_dir(self,ftp_user: str, host: str, url=get_project) -> Dict:
        data = {
            "ftp_user": ftp_user,
            "host": host
        }
        res = self._request(url, data=data)
        log.info(res)
        if res["code"] != 0:
            return {}
        return res["data"]

    def get_encrype(self, user, url=get_user_key):
        data = {
            "user": user
        }
        return self._request(url, data)

    def get_user_by_ftp_user(self, ftp_user, url=get_user_by_ftp_user):
        data = {
            "ftp_user": ftp_user
        }
        return self._request(url, data)

    def get_remote_server_info(self, project_id, url=get_server_info):
        # 获取服务器信息
        return self._request(url.format(project_id))


    def _format_to_json_str(self, data):
        # 格式化未json字符串
        if isinstance(data, str):
            return data
        try:
            str_data = json.dumps(data)
        except Exception as e:
            log.error(e)
            return ""
        return str_data


php = ReqPHP()
