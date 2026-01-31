# encoding=utf-8

from lib.data import HugoData
import unittest
from common.log import log
from config import CONFIG
log.set_out(True)


class TestStringMethods(unittest.TestCase):
    def test_download_struct(self) -> None:
        d = {
            "category": "7ai",
            "identifier": "LTpxHsJ3MydyyLsCRw7HuQVHWYyDy7",
            "name": "",
            "user": "7ai",
            "comefrom": 0,
            "rule": "7ai",
            "filename": "LTpxHsJ3MydyyLsCRw7HuQVHWYyDy7.mp4",
            "video": {
                "cat": "7ai",
                "title": "#有码动漫 卒業○○電車 二輌目 女教師の尻はいつも後ろから見られている",
                "subcat": "高清动漫",
                "actor": "",
                "uploader": ""
            },
            "overwrite": False,
            "upload_uid": 0,
            "owner": "",
            "isupload": False,
            "republish": {
                "subcat": "高清动漫",
                "cat": "7ai",
                "rule": "7ai",
                "user": ""
            }
        }
        hd = HugoData(**d)
        download = hd.to_download()
        print(11111)
        download.set_ftp(**CONFIG)
        print(download.__dict__)



if __name__ == '__main__':
    unittest.main()