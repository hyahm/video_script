# encoding=utf-8
import unittest

from request.request import php
from common.log import log
log.set_out(True)

class TestStringMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.request = php

    # def test_get_rule(self) -> None:
    #     res = self.request.get_new_rule(  "ai", "7ai",url="http://localhost:9999/rule/get")
    #     log.info(res)

    # def test_exsit_identifier(self) -> None:
    #     res = self.request.exsit_identifier("tanhury7meah")
    #     log.info(res)


    # def test_get_project_by_cat_and_subcat(self) -> None:
    #     res = self.request.get_project_by_cat_and_subcat("7ai", "日本4K", "76ai")
    #     log.info(res)

    # def test_get_encrype(self) -> None:
    #     res = self.request.get_encrype("7ai")
    #     log.info(res)

    # def test_get_user_by_ftp_user(self) -> None:
    #     res = self.request.get_user_by_ftp_user("7ai")
    #     log.info(res)

    def test_get_remote_server_info(self) -> None:
        res = self.request.get_remote_server_info("7ai")
        log.info(res)
        

if __name__ == '__main__':
    unittest.main()