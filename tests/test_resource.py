# encoding=utf-8
import unittest

from aiohttp import request

from app.publish.main import Publish
from lib.data import HugoData
from request.request import php
from common.log import log


log.set_out(True)

class TestStringMethods(unittest.TestCase):

    # def setUp(self) -> None:
    #     self.data = {
    #         "identifier": "gc_bbu4tuc3",
    #         "ftp_user": "maomi",
    #         "name": "gc_bbu4tuc3",
    #         "project": "maomi",
    #         "user": "maomi",
    #         "comefrom": 0,
    #         "rule": "mm_online_mp4",
    #         "filename": "gc_bbu4tuc3.mp4",
    #         "video": {
    #             "title": "土豪酒店各种花招玩稚嫩漂亮的大学干女儿,电动机器炮都用上了,妹子被折磨的一次次高潮,操完后还把她B毛给刮了!",
    #             "cat": "mm_在线电影",
    #             "subcat": "国产精品",
    #             "uploader": "",
    #             "actor": ""
    #         },
    #         "postparam": {
    #             "duration": 0,
    #             "play_url": "",
    #             "download_url": "",
    #             "thumb_longview": "",
    #             "thumbnail": "",
    #             "thumb_ver": "",
    #             "thumb_hor": "",
    #             "thumb_series": [],
    #             "cover": "maomi/gc_bbu4tuc3.jpg",
    #             "webp_count": 0,
    #             "webp": "",
    #             "preview": "",
    #             "part_video": ""
    #         },
    #         "overwrite": False,
    #         "pool": False,
    #         "dryrun": False,
    #         "before": 0,
    #         "after": 0,
    #         "status": 0,
    #         "owner": "maomi",
    #         "image": {
    #             "title": None,
    #             "cat": None,
    #             "subcat": None,
    #             "actor": None
    #         },
    #         "upload_uid": 0,
    #         "isupload": False,
    #         "isspider": False,
    #         "republish": {
    #             "subcat": "",
    #             "cat": "",
    #             "rule": "",
    #             "user": ""
    #         }
    #     }

    # def test_publish(self) -> None:
    #     resource = Resource(HugoData(self.data))
    #     success, _ = resource.handle()


    def test_get_resource(self) -> None:
        x = php.get_resource("http://127.0.0.1:9999/resource/get")
        print(x.domain)
        

if __name__ == '__main__':
    #  python -m unittest tests\test_resource.py
    unittest.main()