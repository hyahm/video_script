# encoding=utf-8

# 数据结构
"""
{
    "identifier": "om_dvu3wj4u", 
    "video": {
        "title": "xxxxxxx", "cat": 
        "maomivip_vip\u4e13\u533a", 
        "subcat": "\u6b27\u7f8e\u5927\u7247", 
        "actor": ""
    }, 
    "filename": "om_dvu3wj4u.mp4", 
    "rule": "mm_vip_online_mp4", 
    "comefrom": 0, 
    "postparam": {
        "duration": 0, 
        "play_url": "", 
        "download_url": "http://23.225.165.34/resource/maomivip/maomivip_m3u8_online/om_dvu3wj4u/om_dvu3wj4u.mp4", 
        "thumb_longview": "http://23.225.165.34/resource/maomivip/maomivip_m3u8_online/om_dvu3wj4u/om_dvu3wj4u_longPreview.jpg",
        "thumbnail": "http://23.225.165.34/resource/maomivip/maomivip_m3u8_online/om_dvu3wj4u/om_dvu3wj4u_thumb_3.jpg", 
        "thumb_ver": "http://23.225.165.34/resource/maomivip/maomivip_m3u8_online/om_dvu3wj4u/om_dvu3wj4u_hor.jpg", 
        "thumb_hor": "http://23.225.165.34/resource/maomivip/maomivip_m3u8_online/om_dvu3wj4u/om_dvu3wj4u_ver.jpg", 
        "thumb_series": [3, 75, 147, 219, 291, 363, 435, 507, 579, 651, 723, 795, 867, 939, 1011, 1083, 1155, 1227, 1299, 1371, 1443, 1515, 1587, 1659, 1731], 
        "cover": "maomivip/om_dvu3wj4u.jpg", 
        "webp_count": "", 
        "webp": "", 
        "preview": ""
    },
    "name": "om_dvu3wj4u", 
    "overwrite": false, "category": "maomivip_m3u8_online", "user": "maomivip"

}
"""
from lib.newrule import get_rule
from pydantic import BaseModel
from functional.files import have_space
from response.error import isEmpty, haveSpace
from lib.base import  filed_to_dict, filed_to_int,  filed_to_str, filed_to_list, filed_to_bool
from request.request import php
from typing import Optional, Tuple, Dict
from lib.resource import ResourceServer
from lib.ftp import Ftp
from typing import List


class Image(BaseModel):
    title: str = ""
    cat: str = ''
    subcat: str = ''
    actor: str = ''

class Video(BaseModel):
    title: str = ""
    cat: str = ""
    subcat: str = ""
    uploader: str = ""
    actor: str = ""


class PostParam(BaseModel):
    duration: int = 0
    play_url: str = ""
    download_url: str = ""
    thumb_longview: str = ""
    thumbnail: str = ""
    thumb_ver: str = ""
    thumb_hor: str = ""
    thumb_series: List[int] = []
    play_url: str = ""
    cover: str = ""
    webp_count: int = 0
    webp: str = ""
    preview: str = ""
    part_video: str = ""


"""
{
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
	"overwrite": false,
	"upload_uid": 0,
	"owner": "",
	"isupload": false,
    "republish": {
        "subcat": "高清动漫",
		"cat": "7ai",
        "rule": "7ai",
        "user": ""
    }
}
"""

class RePublish(BaseModel):
    subcat: str = ''
    cat: str = ""
    rule: str = ""
    user: str = ""

class HugoData(BaseModel):
    identifier: str = ""
    ftp_user: str = ""
    name: str = ""
    project: str = ""
    project_id: int = 0
    user: str = ""
    comefrom: int = 0
    rule: str = ""
    filename: str = ""
    video: Video = Video()
    postparam: PostParam = PostParam()
    overwrite: bool = False
    pool: bool = False
    dryrun: bool = False
    before: int = 0
    after: int = 0
    status: int = 0
    owner: str = ""
    image: Image = Image()
    upload_uid: int = 0
    isupload: bool = False
    isspider: bool = False
    republish: RePublish = RePublish()
    funcnum: int = 0
    resource_ftp: Ftp = Ftp()
    domain: str = ""
    resource: ResourceServer = ResourceServer()
    video_length: int = 0
    width: int = 0
    height: int = 0


    def _check_empty(self) -> Tuple[str, bool]:
        """
        return: 第一个是错误信息， 第二个是成功与否
        """
        field = ["identifier", "filename", "title", "cat", "subcat"]

        values = [self.identifier, self.filename,
                  self.video.title, self.video.cat, self.video.subcat]
        if self.user == "shenhe":
            field = ["identifier", "filename", "title"]
            values = [self.identifier, self.filename, self.video.title]
        for i, v in enumerate(values):
            if v == "":
                return isEmpty.format(field[i]), False
        return "", True

    def _check_space(self) -> Tuple[str, bool]:
        """
        return: 第一个是错误信息， 第二个是成功与否
        """
        field = ["json_file_name", "identifier", "filename"]
        values = [self.name, self.identifier, self.filename]
        for i, v in enumerate(values):
            if have_space(v):
                return haveSpace.format(field[i]), False
        return "", True

    def check_cate_and_subcat(self) -> bool:
        return php.get_project_by_cat_and_subcat(self.video.cat, self.video.subcat, self.user)

    # 返回的是一个FtpErrors 或 False

    def check_ftp_integrity(self) -> Tuple[str, bool]:
        """
        return: 第一个是错误信息， 第二个是成功与否
        """
        # 哪些字段不能为空
        err, ok = self._check_empty()
        if not ok:
            return err, False
        # 如果规则为空的， 那么就是爬虫
        if self.rule:
            # ftp的规则检测， 不用检查规则下载
            if not get_rule(self.user, self.rule):
                return "rule_error", False
        # 检查json， identify， mp4 文件是否有空格
        err, ok = self._check_space()
        if not ok:
            return err, False

        # 检查分类是否正确
        project = php.get_project_dir(self.ftp_user, self.resource_ftp.host)
       
        self.project = project["project"]
        self.project_id = project["project_id"]
        if self.user != "shenhe":
            ok = self.check_cate_and_subcat()
            if not ok:
                return "cat_or_subcat_not_found", False
        return "", True
 
