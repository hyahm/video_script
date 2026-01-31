# -*- coding: UTF-8 -*-
# 处理资源的类
import PIL
from config import CONFIG
from functional.files import create_dir
import os
from os import path
import time
from common.log import log
from common.ffmpeg import ffmpeg
from common.shell import shell
from remote.shell import remote_shell
from functional.images import to_webp
from common.imagelib import ImageHandle
from request.status import UpdateStatus
from lib.data import HugoData
from request.request import php
import json
from typing import Tuple 
from lib.resource import ResourceServer

class Resource():

    def __init__(self, dict_conf: HugoData):
        # 项目目录保存的视频 文件， 临时的
        self.flowdata = dict_conf
        # 项目目录保存的封面图 文件， 临时的

        self.reative = path.join(self.flowdata.project, self.flowdata.user, self.flowdata.identifier)
        # 本地资源根目录
        self.source_dir = path.join(path.normpath(CONFIG["local_dir"]), self.reative)
        # 本地源文件
        self.local_video_file = path.join(self.flowdata.user , self.flowdata.identifier + ".mp4")

        self.local_cover_image = path.join( self.flowdata.user ,self.flowdata.identifier + ".jpg")
        # 资源的视频文件
        self.video_path = path.join(self.source_dir, self.flowdata.identifier + ".mp4")
        # 资源的封面图文件
        self.resource_cover = path.join(self.source_dir, self.flowdata.identifier + ".jpg")

        self.update_status = UpdateStatus(
            self.flowdata.identifier, self.flowdata.user, self.flowdata.rule, isupload=self.flowdata.isupload)
        self.error_msg = ""
        # 1.  获取时长，
        self.video_length = ffmpeg.get_video_length(self.local_video_file)
        # 获取视频宽高
        self.width, self.height = ffmpeg.get_video_shape(self.local_video_file)
        # self.resource = Resource(php.get_resource())
        # self.user = self.resource.user
        # self.host, self.port = self.make_host_port(self.resource.ip)

    # 第一个bool 是成功还是失败， 第二是是否需要重试， 如果不重试就直接删除资源文件
    def handle(self) -> Tuple[bool, bool]:
        create_dir(self.source_dir)
        # 视频文件路径

        if not path.exists(self.local_video_file):
            self.error_msg = "not found video"
            return False, False
        # 下载的视频文件复制到资源文件
        shell.copy(self.local_video_file, self.video_path)

        if self.height == 0:
            log.error("视频高度0")
            self.error_msg = "视频高度0"
            return False, False
        # 2. 封图路径
        # 电影的话必须生成一张总封面
        # 不存在封面图或者封面图有问题就自动生成一张
        if not path.exists(self.local_cover_image) or not self.is_image(self.local_cover_image):
            log.info("not found cover will make one")
            if not self.make_cover_image(self.local_cover_image):
                log.error("make cover image failed")
                self.error_msg = "生成封面图失败"
                return False, False
        # 下载的封面图文件拷贝纸资源目录
        shell.copy(self.local_cover_image, self.resource_cover)
        # 图片转化为webp
        try:
            to_webp(self.resource_cover, self.resource_cover[:-3] + "webp")
        except PIL.UnidentifiedImageError:
            # 如果失败就再切一张封面图
            log.info("cover image break will make one")
            if not self.make_cover_image(self.local_cover_image):
                log.error("make cover image failed")
                self.error_msg = "生成封面图失败"
                return False, False
            shell.copy(self.local_cover_image, self.resource_cover)
            # 图片转化为webp
            to_webp(self.resource_cover, self.resource_cover[:-3] + "webp")
        # 4. 切割出横向和纵向的缩略图
        if not self._thumb(self.resource_cover):
            log.error("cut thumbnail fail")
            self.error_msg = "生成缩略图失败"
            return False, True

        # # 5. 制作缩略图
        if not self.make_thumb():
            # 删除资源目录
            self.error_msg = "视频图像有问题"
            log.error("视频图像有问题已删除")
            return False, False

         # 6. 同步到资源服务器。 包含数据和请求php
        log.info("start send to server")
        # self._update_conf()
        if not self.to_remote():
            self.error_msg = "拷贝数据到服务器失败"
            log.error("send to server error")
            return False, True

        ## 是否需要重新切片
        return True, True

    def republish(self) -> str:
        ## 是否需要重新切片
        if self.flowdata.republish.cat != "" and self.flowdata.republish.subcat != "" and \
             self.flowdata.republish.rule != "" and self.flowdata.republish.user != "":
            pool = {
                "identifier": self.flowdata.identifier,
                "name":  self.flowdata.name,
                "user": self.flowdata.republish.user,
                "rule":self.flowdata.republish.rule,
                "filename": self.flowdata.filename,
                "video": {
                    "cat": self.flowdata.republish.cat,
                    "title": self.flowdata.video.title,
                    "subcat": self.flowdata.republish.subcat,
                    "actor": self.flowdata.video.actor,
                    "uploader": self.flowdata.video.uploader
                },
                "overwrite": self.flowdata.overwrite,
                "upload_uid": self.flowdata.upload_uid,
                "owner": self.flowdata.user,
                "isupload": self.flowdata.isupload
            }
            return json.dumps(pool)
        return ""
        

    def _rename(self, count):
        increase = self.video_length//count
        for i in range(1, count+1):
            f = str(i)
            if i / 10 < 1:
                f = "0" + str(i)
            s = (i-1)*increase + 3
            src = path.join(
                self.source_dir, self.flowdata.identifier + "_thumb_{}.jpg".format(f))
            dst = path.join(
                self.source_dir, self.flowdata.identifier + "_thumb_{}.jpg".format(s))
            if not path.exists(src):
                break
            try:
                os.remove(dst)
            except:
                pass
            os.rename(src, dst)
            to_webp(dst, dst[:-3] + "webp")
            self.flowdata.postparam.thumb_series.append(s)

    def make_thumb(self):
        # 制作缩略图， 长预览图（由预览图拼接而成），

        #    1、视频时长<30s 长图截取1张  预览图5张
        #    30s<视频时长<3分钟 长图截取10张 预览图10张
        #    视频时长>3分钟 长图截取100张 预览图10张
        log.info("制作长预览图================")
        log.info("video length: %ds " % self.video_length)
        if self.video_length < 30:
            # 预览图5张
            if self.video_length < 6:
                count = 1
                if not ffmpeg.screen_image(self.video_path, path.join(self.source_dir, self.flowdata.identifier + "_thumb_%2d.jpg"), interval=1, count=count):
                    log.info("截取1张缩略图失败")
                    return False
            else:
                count = 5
                if not ffmpeg.screen_image(self.video_path, path.join(self.source_dir, self.flowdata.identifier + "_thumb_%2d.jpg"), interval=((self.video_length-1)//count), count=count):
                    log.info("截取5张缩略图失败")
                    return False
            self._rename(count)
        else:
            count = 25
            # 预览图10张
            if self.video_length < 600:
                count = 10
            if not ffmpeg.screen_image(self.video_path, path.join(self.source_dir, self.flowdata.identifier + "_thumb_%2d.jpg"), interval=((self.video_length-3)//count), count=count):
                log.info("截取{}张缩略图失败".format(count))
                return False
            self._rename(count)
            # 根据时间重命名
        log.info("制作长预览图完成............")
        # 将所有的jpg转为webp
        for fn in os.listdir(self.source_dir):
            # 
            if fn.find("_thumb_")  >= 0 and fn[-3:] == "jpg":
                filepath = path.join(self.source_dir, fn)
                to_webp(filepath, filepath[:-3] + "webp")

        return True

    def make_cover_image(self, output):
        """
        提取视频长度
        提取封面
        """
        log.info("开始提取封面图============ %s" % output)

        _, self.height = ffmpeg.get_video_shape(self.video_path)
        if not self.height:
            log.info("%s（视频长宽失败）" % self.video_path)
            return False
        if not ffmpeg.get_cover(self.video_path, 0, output):
            # 删除视频
            return False
        log.info("提取封面图完成............")
        return True

    def to_remote(self):
        # 获取远程服务器的信息
        # 复制源视频文件
        
        self.flowdata.resource = ResourceServer(**php.get_resource())

        if self.flowdata.resource.ip == "":
            log.error("没有配置资源服务器，请尽快配置")
            time.sleep(10)
            return self.to_remote()
        localfile = path.join(
            self.source_dir, self.flowdata.identifier + "*")
        remote_dir = path.join(self.flowdata.resource.root, self.reative)
        remote_shell.make_remote_dirs(remote_dir, self.flowdata.resource.ip)
        if not remote_shell.rsync_to_resource(localfile, remote_dir, "", self.flowdata.resource.ip):
            log.info("send to server error")
            self.flowdata.overwrite = True
            return False
        cover_file = path.join(
            self.source_dir, self.flowdata.identifier + ".jpg")
        return remote_shell.rsync_to_resource(cover_file, remote_dir + "/",self.flowdata.identifier + ".jpg",self.flowdata.resource.ip)

    # def _update_conf(self):
    #     # 生成json, 替换旧的
       
    #     self.flowdata.postparam.download_url = "{}/resource/{}/{}".format(
    #         CONFIG["resource_domain"],  self.reative, self.flowdata.identifier + ".mp4")

    #     self.flowdata.postparam.thumb_ver = "{}/resource/{}/{}".format(
    #         CONFIG["resource_domain"], self.reative, self.flowdata.identifier + "_hor.jpg")
    #     self.flowdata.postparam.thumb_hor = "{}/resource/{}/{}".format(
    #         CONFIG["resource_domain"],  self.reative, self.flowdata.identifier + "_ver.jpg")
    #     # 生成返回php 的参数
    #     # self.audio_url = self.flowdata.postparam.play_url
    #     # self.audio_url_down = self.flowdata.postparam.download_url
    #     # 更新生成需要使用的json文件
    #     # json_content = json.dumps(self.flowdata)

    #     return True

    def is_image(self, image_path: str) -> bool:
        """
        缩略图必须存在， 不然raise
        """
        # thumb_hor  310*174 横向的缩略图
        # thumb_ver 纵向的缩略图 180*246
        # 大图是小图的 5倍
        try:
            ImageHandle(image_path)
        except Exception as e:
            log.info(e)
            return False
        return True

    def _thumb(self, image_file) -> bool:
        """
        缩略图必须存在， 不然raise
        """
        # thumb_hor  310*174 横向的缩略图
        # thumb_ver 纵向的缩略图 180*246
        # 大图是小图的 5倍
        try:
            ih = ImageHandle(image_file)
        except Exception as e:
            log.info(e)
            return False
        # 通过封面获取横向缩略图
        hor = path.join(
            self.source_dir, self.flowdata.identifier + "_hor.jpg")
        if not ih.get_thumb(hor, 310, 174):
            log.info("error")
            return False

        to_webp(hor, hor[:-3] + "webp")
        ver = path.join(
            self.source_dir, self.flowdata.identifier + "_ver.jpg")
        # 通过封面获取纵向缩略图
        if not ih.get_thumb(ver, 180, 246):
            log.info("error")
            return False

        to_webp(ver, ver[:-3] + "webp")
        # 通过封面获取大横向缩略图
        hor_large = path.join(
            self.source_dir, self.flowdata.identifier + "_hor_large.jpg")
        if not ih.get_thumb(hor_large, 310*5, 174*5):
            log.info("error")
            return False
        to_webp(hor_large, hor_large[:-3] + "webp")
        # 通过封面获取大纵向缩略图
        ver_large = path.join(
            self.source_dir, self.flowdata.identifier + "_ver_large.jpg")
        if not ih.get_thumb(ver_large, 180*5, 246*5):
            log.info("error")
            return False
        to_webp(ver_large, ver_large[:-3] + "webp")
        return True
