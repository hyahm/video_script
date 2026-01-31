# encoding=utf-8
import imp
import unittest

from app.publish.main import Publish
from lib.data import HugoData
from common.log import log
import json
import sys


log.set_out(True)

class TestStringMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.iswindows = sys.platform.startswith("win")
        
        
        self.data = {
            "identifier": "62e484d7e1a37c91cc9741d2716c3aa0", 
            "ftp_user": "",
         "name": "62e484d7e1a37c91cc9741d2716c3aa0",
          "project": "uu", "user": "uu", "comefrom": 0, 
          "rule": "2021_API", "filename": "b6077692336db05de5b26c2b880d75be.mp4", 
          "video": 
          {"title": "长相清纯的女大学生自慰", 
          "cat": "uu手动上传", "subcat": 
          "手动", "uploader": "", "actor": ""}, 
          "postparam": {"duration": 0, "play_url": "", 
          "download_url": "http://23.225.165.34/resource/uu/uu/62e484d7e1a37c91cc9741d2716c3aa0/62e484d7e1a37c91cc9741d2716c3aa0.mp4", "thumb_longview": "", "thumbnail": "", "thumb_ver": "http://23.225.165.34/resource/uu/uu/62e484d7e1a37c91cc9741d2716c3aa0/62e484d7e1a37c91cc9741d2716c3aa0_hor.jpg", "thumb_hor": "http://23.225.165.34/resource/uu/uu/62e484d7e1a37c91cc9741d2716c3aa0/62e484d7e1a37c91cc9741d2716c3aa0_ver.jpg", 
          "thumb_series": [3, 40, 77, 114, 151, 188, 225, 262, 299, 336, 373, 410, 447, 484, 521, 558, 595, 632, 669, 706, 743, 780, 817, 854, 891], "cover": "", "webp_count": 0, "webp": "", "preview": "", "part_video": ""}, "overwrite": False, "pool": False, "dryrun": False, "before": 0, "after": 0, "status": 0, "owner": "uu", "image": {"title": "", "cat": "", "subcat": "", "actor": ""}, "upload_uid": 71, "isupload": True, 
          "isspider": False, "republish": {"subcat": "", "cat": "", "rule": "", "user": ""}}

    def test_publish(self) -> None:
        print(self.iswindows)
        publish = Publish(HugoData(**self.data))
        success, _ = publish.handle()
        self.assertTrue(success)
        

if __name__ == '__main__':
    # python -m unittest tests\test_publish.py
    unittest.main()