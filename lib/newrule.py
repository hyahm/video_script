# encoding=utf-8
from copy import deepcopy

"""
{
	"name": "",
	"head": {
		"enable": false,
		"video_url": ""
	},
	"logo": {
		"enable": false,
		"padding": 0,
		"scale": 0,
		"image_url": "",
		"position": 0
	},
	"font": {
		"enable": false,
		"text": "",
		"color": "#000000",
		"size": 0,
		"position": 0,
		"interval": 0,
		"scroll": 0,
		"border": 0,
		"shadow": false,
		"space": 0
	},
	"ad": {
		"enable": false,
		"url": "",
		"start": 0,
		"stay": 5
	},
	"m3u8": {
		"enable": false,
		"encrypt": false,
		"interval": 0,
		"bitrate": 0,
		"fps": 0
	},
	"webp": {
		"enable": false,
		"start": 5,
		"interval": 1,
		"times": 10
	},
	"after": 0,
	"before": 0,
	"resolve": 0,
	"api": "",
	"enable": false
}

"""
from config import php_ip
from lib.base import filed_to_bool, filed_to_int, filed_to_dict, filed_to_str
from functional.download import download_video, download_file
import time
from common.log import log
from typing import Dict
from pydantic import BaseModel, validator

class Font(BaseModel):
    enable: bool = False
    text: str = ""
    color: str = ""
    size: int = 15
    interval: int = 0
    position: int = 0
    scroll: int = 0
    border: int = 0
    space: int = 0
    shadow: bool = False

    @validator('size')
    def default_size(cls, v):
        if v <= 0:
            return 15
        return v
    
    def make_fontfile(self) -> str:
        now = str(time.time()) + ".txt"
        with open(now, "w+", encoding="utf-8") as f:
            f.write(self.text)
        return now


class Logo(BaseModel):
    enable: bool = False
    padding: int = 0
    scale: int = 15
    image_url: str = ""
    position: int = 0

    @validator('scale')
    def default_scale(cls, v):
        if v <= 0:
            return 15
        return v
        
    def get_image(self) -> str:
        # 获取视频， 
        now = str(time.time()) + "logo"
        url = php_ip +self.image_url
        suffix = url.split(".")[-1]
        if not download_file(url, now + "." + suffix):
            return ""
        return now + "." + suffix

class Head(BaseModel):
    enable: bool = False
    video_url: str = ""
        
    def get_video(self) -> str:
        # 获取视频， 
        now = str(time.time())
        url = php_ip +self.video_url
        suffix = url.split(".")[-1]
        if not download_video(url, now + "." + suffix):
            return ""
        return now + "." + suffix
        
        
class Ad(BaseModel):
    enable: bool = False
    url: str = ""
    start: int = 0
    stay: int = 5

    @validator('stay')
    def default_stay(cls, v):
        if v <= 0:
            return 5
        return v
        
    def get_image(self) -> str:
        # 获取视频， 
        now = str(time.time()) + "ad"
        url = php_ip +self.url
        suffix = url.split(".")[-1]
        if not download_file(url, now + "." + suffix):
            log.error("failed")
            return ""
        return now + "." + suffix
        
class M3u8(BaseModel):
    enable: bool = False
    encrypt: bool = False
    interval: int = 0
    bitrate: int = 0
    fps: int = 0
        
class Webp(BaseModel):  
    enable: bool = False
    start: int = 5
    interval: int = 1
    count: int = 10

    @validator('start')
    def default_start(cls, v):
        if v <= 0:
            return 5
        return v

    @validator('interval')
    def default_interval(cls, v):
        if v <= 0:
            return 1
        return v

    @validator('count')
    def default_count(cls, v):
        if v <= 0:
            return 10
        return v

class Rule(BaseModel):
    name: str = ""
    api_path: str = ""
    after: int = 0
    before: int = 0
    enable: bool = False
    resolve: int = 0
    image_format: int = 0   # 0: 480 1: 720  2: 1080
    webp: Webp = Webp(**{})
    m3u8: M3u8= M3u8(**{})
    ad: Ad= Ad(**{})
    head: Head= Head(**{})
    logo: Logo= Logo(**{})
    font: Font= Font(**{})

    


    # def __init__(self, kargs: Dict) -> None:
    #     self.after = filed_to_int(kargs, "after", 0)
    #     self.before = filed_to_int(kargs, "before", 0)
    #     self.enable = filed_to_bool(kargs, "enable", True)
    #     self.resolve = filed_to_int(kargs, "resolve", 0)
    #     self.image_format = filed_to_int(kargs, "image_format", 0)
    #     if self.resolve == 0:
    #         self.resolve = 480
    #     elif self.resolve == 1:
    #         self.resolve = 720
    #     elif self.resolve == 2:
    #         self.resolve = 1080
    #     else:
    #         self.resolve = 480
    #     self.webp = Webp(filed_to_dict(kargs, "webp", {}))
    #     self.m3u8 = M3u8(filed_to_dict(kargs, "m3u8", {}))
    #     self.ad = Ad(filed_to_dict(kargs, "ad", {}))
    #     self.head = Head(filed_to_dict(kargs, "head", {}))
    #     self.logo = Logo(filed_to_dict(kargs, "logo", {}))
    #     self.font = Font(filed_to_dict(kargs, "font", {}))
        # self.font_image = FontImage(filed_to_dict(kargs, "font", {}))  # 图片专用  片头文字水印
        
        
    # def dict(self) -> dict:
    #     data = {}
    #     data = deepcopy(self.__dict__)
    #     data["font"] = self.font.__dict__
    #     data["webp"] = self.webp.__dict__
    #     data["m3u8"] = self.m3u8.__dict__
    #     data["ad"] = self.ad.__dict__
    #     data["head"] = self.head.__dict__
    #     data["logo"] = self.logo.__dict__
    #     # data.font_image = self.font_image.__dict__
    #     return data
    
    # 打给视频打水印, 
from request.request import php

def get_rule(user, rulename:str, rule_type=0) -> Rule:
    info = php.get_new_rule(user, rulename, rule_type)
    log.info(info)
    if info["code"] != 0:
        log.error(info)
        return False
    return Rule(**info["data"])

