# encoding=utf-8
import unittest

from request.third import Third
from common.log import log
from lib.data import HugoData
log.set_out(True)

class TestStringMethods(unittest.TestCase):

    def setUp(self) -> None:
        
        self.request = Third("pjbncek735kbq3m2yhf86sdj4nb5kj", "7ai", "7ai", False)
        self.urls = [
            # "http://localhost:8080/1",
            #  "http://localhost:8080/2",
            #  "http://localhost:8080/3",
            #  "http://localhost:8080/4",
            #  "http://localhost:8080/5",
             "http://localhost:8080/asdf",
             "http://localhost:9080/asdf"
        ]
        self.data =  {"identifier": "pjbncek735kbq3m2yhf86sdj4nb5kj", "ftp_user": "", "name": "pjbncek735kbq3m2yhf86sdj4nb5kj", "project": "7ai", "user": "7ai", "comefrom": 0, "rule": "7ai", "filename": "pjbncek735kbq3m2yhf86sdj4nb5kj.mp4", "video": {"title": "日本AV-AMBI-098 以成為偶像為目標來到東京的青梅竹馬，色情又回來瞭！", "cat": "7ai", "subcat": "日本4K", "uploader": "", "actor": ""}, "postparam": {"duration": 0, "play_url": "", "download_url": "http://23.225.165.34/resource/7ai/7ai/pjbncek735kbq3m2yhf86sdj4nb5kj/pjbncek735kbq3m2yhf86sdj4nb5kj.mp4", "thumb_longview": "", "thumbnail": "", "thumb_ver": "http://23.225.165.34/resource/7ai/7ai/pjbncek735kbq3m2yhf86sdj4nb5kj/pjbncek735kbq3m2yhf86sdj4nb5kj_hor.jpg", "thumb_hor": "http://23.225.165.34/resource/7ai/7ai/pjbncek735kbq3m2yhf86sdj4nb5kj/pjbncek735kbq3m2yhf86sdj4nb5kj_ver.jpg", "thumb_series": [3, 93, 183, 273, 363, 453, 543, 633, 723, 813, 903, 993, 1083, 1173, 1263, 1353, 1443, 1533, 1623, 1713, 1803, 1893, 1983, 2073, 2163], "cover": "", "webp_count": 0, "webp": "", "preview": "", "part_video": ""}, "overwrite": False, "pool": False, "dryrun": False, "before": 0, "after": 0, "status": 0, "owner": "7ai", "image": {"title": None, "cat": None, "subcat": None, "actor": None}, "upload_uid": 0, "isupload": False, "isspider": False, "republish": {"subcat": "", "cat": "", "rule": "", "user": ""}}


    def test_request_api(self) -> None:
        for url in self.urls:
            try:
                res = self.request.request_api(url, self.data)
                log.info(res["msg"] + "444")
            except Exception as e:
                log.error(e + "a")



if __name__ == '__main__':
    
    unittest.main()