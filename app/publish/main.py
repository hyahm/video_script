# -*- coding: UTF-8 -*-
# 处理发布的类, 获取规则，。 打水印， 生成m3u8文件， 发送到远程服务器
from textwrap import indent
from typing import Tuple
from xml.dom.minidom import Identified
from app.publish.part import CutPartVideo
from common.log import log
from common.ffmpeg import ffmpeg
from common.shell import shell
from remote.shell import remote_shell
from request.request import php
from os import path
from config import CONFIG
import os
from request.third import Third
from core.addwater import WaterMark
from common.imagelib import ImageHandle
from lib.newrule import Rule, get_rule
from functional.images import make_long_preview_to_size, to_webp
from request.status import UpdateStatus
from lib.data import HugoData
# from service.redis import local_rc
from functional.check import check_date
from functional.files import create_dir
# from lib.video import HandleVideo
from lib.serverinfo import get_server_info, ServerInfo
from app.publish.webp import MakeVideoWebp
from app.publish.hls import MakeVideoHLS


class Publish(Third):

    def __init__(self, dict_conf: HugoData):
        """
            dict_conf: redis读取解析后的数据
            queue_str: redis里面的数据
        """
        self.water_image = "water.png"
        self.flowdata = dict_conf
        # self.queue = queue_str
        # 资源文件的目录
        # 固定相对路径
        self.reative = path.join(self.flowdata.project, self.flowdata.user,  self.flowdata.identifier)
        # 本地项目完整根目录
        self.source_dir = path.normpath(path.join(path.normpath(
            CONFIG["local_dir"]), self.reative))
        ###################
        # 备份的视频文件
        self.backup_video_file = self.flowdata.identifier + "_resource.mp4"
        self.video_path = path.join(
            self.source_dir, self.flowdata.identifier + ".mp4")
        self.backup()
        self.flowdata.video_length = 0
        self.rule: Rule = Rule(**{})
        self.serverinfo = ServerInfo()
        self.tmp_font_water_image = ""
        self.flowdata.width, self.flowdata.height = ffmpeg.get_video_shape(self.video_path)
        self.error_msg = ""
        super().__init__(self.flowdata.identifier, self.flowdata.user,
                         self.flowdata.rule, self.flowdata.isupload)
        self.us = UpdateStatus(self.flowdata.identifier,
                               self.flowdata.user, self.flowdata.rule, isupload=self.flowdata.isupload)
        self.mvh: MakeVideoHLS = None

    def rollback(self) -> None:
        shell.copy(self.backup_video_file, self.video_path)

    def backup(self) -> None:
        if not os.path.exists(self.backup_video_file):
            shell.copy(self.video_path, self.backup_video_file)

    def _add_water(self):
        self.us.processing("正在打水印")
        wm = WaterMark(self.rule)
        ok = wm.add_water(self.video_path)
        wm.clean()
        return ok

    def _make_webp(self):
        # 生成动态图, 规则里面的webp打开才会生成    <identifier>_large_sync.webp   <identifier>_sync.webp
        if self.rule.webp.enable:
            vm = MakeVideoWebp(self.source_dir, self.video_path, self.rule.webp, self.flowdata.width, self.flowdata.height, self.flowdata.video_length)
            self.flowdata.postparam.webp_count = vm.make_webp(path.join(self.source_dir, self.flowdata.identifier + "_sync.webp"),
            path.join(self.source_dir, self.flowdata.identifier + "_large_sync.webp"), self.rule.ad.start)
            shell.remove_all(vm.temp_webp)
            return self.flowdata.postparam.webp_count > 0
        return True

    def _make_hls(self):
        # 先下载加密文件
        if not self.mvh.get_encrypt_file():
            log.error("get encrypt file error")
            return False
        if self.rule.m3u8.enable:
            self.us.processing("正在生成m3u8文件")
            ok = self.mvh.make_hls()
            return ok
        
        return True


    def _make_preview_hls(self) -> bool:
        # 这个是生成试看1/10分钟 最长6分钟的试看视频, 
        cut_video_path = path.join(
            self.source_dir, "preview_" + self.flowdata.identifier + ".mp4")
        duration = self.flowdata.postparam.duration // 10
        if duration > 360:
            duration = 360
        if not ffmpeg.cut(self.video_path, cut_video_path, 0, duration):
            log.error("cut video failed")
            return False
        
        if not self.mvh.make_hls("preview"):
            shell.remove_all(cut_video_path)
            return False
        shell.remove_all(cut_video_path)
        return True

    def clean(self):
        # 成功了就删除本地资源
        shell.remove_all(self.source_dir)
        shell.remove_all(self.flowdata.identifier + "_resource.mp4")
        # 处理完成后才能下载
        # self.video.clean()

    # 生成片段视频， 包含小的和大的  large_part_<indentifier>.mp4  part_<indentifier>.mp4
    def make_part_video(self) -> bool:
        log.info("make_part_video")
        # 
        cpv = CutPartVideo(self.flowdata.identifier, self.source_dir, self.video_path, self.flowdata.video_length)
        ok = cpv.make_part_video()
        if not ok:
            shell.remove_all(cpv.cut_part_path)
        shell.remove_all(cpv.tmpdir)
        return ok

    # 
    def handle(self) -> Tuple[bool, bool]:
        log.info(self.video_path)
        self.flowdata.video_length = ffmpeg.get_video_length(self.video_path)
        if self.flowdata.video_length == 0:
            self.us.fail("哪里有问题")
            return False, False
        # return: 是否处理成功， 是否尝试, 从哪个函数开始执行
        if self.flowdata.video.cat == "":
            self.us.fail("没有分类")
            log.info("没有分类信息")
            return False, False
        self.serverinfo = get_server_info(self.flowdata.project_id)
        if not self.serverinfo:
            log.error("获取分类信息失败")
            return False, True
  
        if not os.path.exists(self.video_path):
            self.us.fail("请重新切片")
            log.error("视频找不到")
            return False, False
        self.rule = get_rule(self.flowdata.user, self.flowdata.rule)
        if not self.rule:
            self.us.fail("规则错误user: {}, rulename: {}".format(
                self.flowdata.user, self.flowdata.rule))
            log.error("规则错误user: {}, rulename: {}".format(
                self.flowdata.user, self.flowdata.rule))
            # 规则有问题的直接删除
            return False, True
        self.mvh = MakeVideoHLS(self.video_path, self.source_dir, self.rule, self.flowdata.user)
        if self.rule.webp.enable and self.rule.webp.start >= self.flowdata.video_length:
            log.error("视频长度不足{}秒, 已删除".format( self.rule.webp.start + 1))
            self.us.fail("视频长度不足{}秒, 已删除".format( self.rule.webp.start + 1))
            return False, False
        # 测试
        # 这是发布需要做的主入口函数
        # 打水印
        handles = [
            {
                "error": "生成视频片段失败",
                "func": self.make_part_video,
                "sign": "get part"
            },
            {
                "error": "生成webp失败",
                "func": self._make_webp,
                "sign": "get webp"
            },
            {
                "error": "打水印失败",
                "func": self._add_water,
                "sign": "add water"
            },
            {
                "error": "生成m3u8失败",
                "func": self._make_hls,
                "sign": "make m3u8"
            },
            {
                "error": "生成试看视频失败",
                "func": self._make_preview_hls,
                "sign": "make preview"
            },
            {
                "error": "发布到远程服务器失败(可以忽略)",
                "func": self._to_remote,
                "sign": "send user server"
            },
            {
                "error": "发送到第三方失败",
                "func": self._send_to_third_server,
                "sign": "send user server api"
            },
            {
                "error": "发送到本地服务失败",
                "func": self._send_to_local_php,
                "sign": "save user info"
            }
            
        ]
        
        self.flowdata.postparam.duration = self.flowdata.video_length
        # 第一个是返回是否成功， 第二个是返回是否重试
        for index in range(len(handles)):
            if index < self.flowdata.funcnum:
                continue
            # 判断函数是否执行成功
            success = handles[index]["func"]()
            if not success:
                log.error(handles[index]["error"])
                self.rollback()
                # 生成试看的可以重试
                if index>=4:
                    self.flowdata.funcnum = index
                    self.us.processing(handles[index]["error"] + ", 请等待重试")
                    
                    return False, True
                else:
                    
                    self.us.fail(handles[index]["error"])
                return False, False
        self.us.success()
        return True, False

    def _send_to_third_server(self) -> bool:
        self.flowdata.overwrite = True
        for api in self.rule.api_path.split(","):
            msg = self.request_api(api, self.flowdata.dict(
                exclude={'ftp_user', 'name', "project", "project_id", "user", "pool", "dryrun", "before", "after",
                 "owner", "upload_uid", "isupload", "isspider", "funcnum", "republish", "resource", "domain", "status", "image"}))
            if msg["code"] != 0:
                # try:
                #     local_rc.rpush("backup", self.queue)
                # except Exception as e:
                #     log.error(e)
                return False
            
        return True


    def _long_preview_image(self):
        # 制作缩略图， 长预览图（由预览图拼接而成），

        #    1、视频时长<30s 长图截取1张  预览图5张
        #    30s<视频时长<3分钟 长图截取10张 预览图10张
        #    视频时长>3分钟 长图截取100张 预览图10张
        log.info("制作长预览图======== %d========" % self.flowdata.video_length)
        long_preview_tmp = path.join(
            self.source_dir, self.flowdata.identifier)  # 临时路径
        create_dir(long_preview_tmp)
        image_width = 640
        image_height = image_width * self.flowdata.height // self.flowdata.width
        if self.flowdata.video_length < 100:
            # 长图截取1张
            if not ffmpeg.screen_image(self.video_path, path.join(self.source_dir, "%s_longPreview.jpg" % self.flowdata.identifier),
                                       size="{0}*{1}".format(image_width, image_height), count=1, interval=1):
                log.info("截取1张大长图失败")
                return False

        else:
            # 根据时间切100张
            # 根据时间重命名
            for i in range(1, 101):
                # 截取的时间为  总时长 * 第几章 // 200  取整秒数
                if not ffmpeg.get_cover(self.video_path, (self.flowdata.video_length * i - 1) // 100, path.join(long_preview_tmp, "tmp{}.jpg".format(i)),  size="{0}*{1}".format(image_width, image_height)):
                    log.error("截取大长图失败")
                    return False

                # 合成大长图
            if not make_long_preview_to_size(long_preview_tmp, image_width, image_height, path.join(self.source_dir, "%s_longPreview.jpg" % self.flowdata.identifier)):
                log.info("合成长预览图失败")
                # shell.remove_all(long_preview_tmp)
                return False
        log.info("制作长预览图完成............")
        return True

    def _send_to_local_php(self) -> bool:
        if self.flowdata.video.title == "":
            self.flowdata.video.title = self.flowdata.identifier
        if not php.save_to_resource(self.flowdata.dict()):
            return False
        return True


    def _to_remote(self) -> bool:
        # 发送到第三方失败的直接移至backup
        if not self._send_to_remote_server():
            log.error("发送到第三方失败 已发送至后补")
            return False
        return True


    def _send_to_server(self) -> bool:
        if self.serverinfo.server.server_ip == "":
            log.error(self.flowdata.video.cat + "-分类没有配置服务器")
            return False
         # 生成json, 替换旧的
        if self.serverinfo.project.play_path and self.rule.m3u8.enable:
            log.info("拷贝播放文件")
            prefix, middle, ok = check_date(self.serverinfo.project.play_path)
            if not ok:
                log.error("路径格式不对")
                return False
            localfile = path.join(self.source_dir, "hls")
            remote_dir = path.join(prefix, middle, self.reative)
            remote_shell.make_remote_dirs(remote_dir, self.serverinfo.server.server_ip)
            if not remote_shell.rsync_to_server(localfile, remote_dir + "/", server=self.serverinfo.server.server_ip):
                log.info("send to publish server error")
                return False
            if middle != "":
                self.serverinfo.project.play_url = "{}/{}".format(self.serverinfo.project.play_url, middle)
            self.flowdata.postparam.play_url = "{}/{}/hls/{}/index.m3u8".format(self.serverinfo.project.play_url, self.reative, 1)
            self.flowdata.postparam.part_video = "{}/{}/{}.mp4".format(self.serverinfo.project.play_url, self.reative, "part_" + self.flowdata.identifier)
            self.flowdata.postparam.preview = "{}/{}/hls/{}/index.m3u8".format(self.serverinfo.project.play_url, self.reative, "preview")

        if self.serverinfo.project.download_path:
            log.info("拷贝视频文件")
            prefix, middle, ok = check_date(self.serverinfo.project.download_path)
            if not ok:
                log.error("路径格式不对")
                return False
            localfile = path.join(
                self.source_dir,  "*.mp4")
            remote_dir = path.join(prefix, middle, self.reative)
            remote_shell.make_remote_dirs(path.join(
                prefix, middle, self.reative), self.serverinfo.server.server_ip)
            if not remote_shell.rsync_to_server(localfile, remote_dir + "/", server=self.serverinfo.server.server_ip):
                log.error("send to publish server error")
                return False
            if middle != "":
                self.serverinfo.project.download_url = "{}/{}".format(self.serverinfo.project.download_url, middle)
            log.info(self.serverinfo.project.download_url)
         
            self.flowdata.postparam.download_url = "{}/{}/{}".format(
                self.serverinfo.project.download_url, self.reative, self.flowdata.identifier + ".mp4")
        # 大长图
        if self.serverinfo.project.preview_path:
            log.info("制作大长图")
            prefix, middle, ok = check_date(self.serverinfo.project.preview_path)
            if not ok:
                log.error("路径格式不对")
                return False
            localfile = path.join(
                self.source_dir, self.flowdata.identifier + "_longPreview.jpg")
            remote_dir = path.join(prefix, middle, self.reative, self.flowdata.identifier + "_longPreview.jpg")
            
            if not self._long_preview_image():
                return False
            # 判断是否是webp
            # shell.make_remote_dirs(path.join(prefix, middle,self.reative), info.host)
            # convertOK = False
            # if self.rule.image_format == 1:
            #     convertOK = to_webp(localfile, localfile[:-3] + "webp")
            #     localfile = localfile[:-3] + "webp"
            #     remote_dir = remote_dir[:-3] + "webp"

            remote_shell.make_remote_dirs(path.join(prefix, middle,self.reative), self.serverinfo.server.server_ip)
            if not remote_shell.rsync_to_server(localfile, remote_dir, server=self.serverinfo.server.server_ip):
                log.info("send to publish server error")
                return False
            if middle != "":
                self.serverinfo.project.preview_url = "{}/{}".format(self.serverinfo.project.preview_url, middle)
            
            self.flowdata.postparam.thumb_longview = "{}/{}/{}".format(
                self.serverinfo.project.preview_url, self.reative, self.flowdata.identifier + "_longPreview.jpg")
            # webp 的长度不支持，先注释
            # if convertOK and self.rule.image_format == 1:
            #     self.flowdata.postparam.thumb_longview = self.flowdata.postparam.thumb_longview[:-3] + "webp"
            

        # 缩略图
        if self.serverinfo.project.thumbnail_path:
            log.info("拷贝缩略图")
            prefix, middle, ok = check_date(self.serverinfo.project.thumbnail_path)
            if not ok:
                log.error("路径格式不对")
                return False
            localfile = path.join(
                self.source_dir, self.flowdata.identifier + "_thumb_*")
            remote_dir = path.join(
                prefix, middle, self.reative)
            remote_shell.make_remote_dirs(remote_dir, self.serverinfo.server.server_ip)
            if not remote_shell.rsync_to_server(localfile, remote_dir + "/", server=self.serverinfo.server.server_ip):
                log.info("send to publish server error")
                return False
            if middle != "":
                self.serverinfo.project.thumbnail_url = "{}/{}".format(self.serverinfo.project.thumbnail_url, middle)
            self.flowdata.postparam.thumbnail = "{}/{}/{}".format(self.serverinfo.project.thumbnail_url, self.reative, self.flowdata.identifier + "_thumb_{}.jpg".format(
                self.flowdata.postparam.thumb_series[0]
            ))
            if self.rule.image_format == 1:
                self.flowdata.postparam.thumbnail = self.flowdata.postparam.thumbnail[:-3] + "webp"
        else:
            self.flowdata.postparam.thumb_series = []

        if self.serverinfo.project.cover_path:
            log.info("拷贝封面图")
            prefix, middle, ok = check_date(self.serverinfo.project.cover_path)
            if not ok:
                log.error("路径格式不对")
                return False

            remote_dir = path.join(prefix, middle, self.reative)
            remote_shell.make_remote_dirs(remote_dir, self.serverinfo.server.server_ip)

            localfile_hor = path.join(self.source_dir, self.flowdata.identifier + "_hor.jpg")
            remote_dir_hor = path.join(remote_dir, self.flowdata.identifier + "_hor.jpg")
            horOK = False
            if self.rule.image_format == 1:
                horOK = to_webp(localfile_hor, localfile_hor[:-3] + "webp")
                localfile_hor = localfile_hor[:-3] + "webp"
                remote_dir_hor = remote_dir_hor[:-3] + "webp"
            
            localfile_ver = path.join(self.source_dir, self.flowdata.identifier + "_ver.jpg")
            remote_dir_ver = path.join(remote_dir, self.flowdata.identifier + "_ver.jpg")
            verOK = False
            if self.rule.image_format == 1:
                verOK = to_webp(localfile_ver, localfile_ver[:-3] + "webp")
                localfile_ver = localfile_ver[:-3] + "webp"
                remote_dir_ver = remote_dir_ver[:-3] + "webp"
            
            if not remote_shell.rsync_to_server(localfile_hor, remote_dir_hor, server=self.serverinfo.server.server_ip):
                log.info("send to publish server error")
                return False
            
            if not remote_shell.rsync_to_server(localfile_ver, remote_dir_ver, server=self.serverinfo.server.server_ip):
                log.info("send to publish server error")
                return False

            # 封面图
            localfile = path.join(self.source_dir, self.flowdata.identifier + ".jpg")
            ih = ImageHandle(localfile)
            # 封面图锐化
            ih.sharpen(localfile)
            coverOK = False
            if self.rule.image_format == 1:
                coverOK = to_webp(localfile, localfile[:-3] + "webp")

            remote_dir = path.join(prefix, middle, self.reative)
            if not remote_shell.rsync_to_server(localfile[:-3] + "*", remote_dir + "/", server=self.serverinfo.server.server_ip):
                log.info("send to publish server error")
                return False

            if middle != "":
                self.serverinfo.project.cover_url = "{}/{}".format(self.serverinfo.project.cover_url, middle)
            self.flowdata.postparam.thumb_ver = "{}/{}/{}".format(
                self.serverinfo.project.cover_url, self.reative, self.flowdata.identifier + "_hor.jpg")
            self.flowdata.postparam.thumb_hor = "{}/{}/{}".format(
                self.serverinfo.project.cover_url, self.reative, self.flowdata.identifier + "_ver.jpg")
            self.flowdata.postparam.cover = "{}/{}/{}".format(
                self.serverinfo.project.cover_url, self.reative, self.flowdata.identifier + ".jpg")
            
            if self.rule.image_format == 1:
                if verOK:
                    self.flowdata.postparam.thumb_ver = self.flowdata.postparam.thumb_ver[:-3] + "webp"
                if horOK:
                    self.flowdata.postparam.thumb_hor = self.flowdata.postparam.thumb_hor[:-3] + "webp"
                if coverOK:
                    self.flowdata.postparam.cover = self.flowdata.postparam.cover[:-3] + "webp"
            # 生成返回php 的参数
            localfile = path.join(self.source_dir, "*_sync.webp")
            if remote_shell.rsync_to_server(localfile, remote_dir + "/", server=self.serverinfo.server.server_ip):
                self.flowdata.postparam.webp = "{}/{}/{}".format(
                self.serverinfo.project.cover_url,self.reative, self.flowdata.identifier + "_sync.webp")
        return True
    
    def _send_to_tx_oss(self) -> bool:
        from service.txoss import TxOss
        to = TxOss(self.serverinfo.server)
        #1. 生成片段视频， 包含小的和大的  large_part_<indentifier>.mp4  part_<indentifier>.mp4
        # 连接腾讯云
        self.flowdata.postparam.part_video = to.upload(path.join(self.source_dir, "part_{}.mp4".format(self.flowdata.identifier)),self.reative)
        if not self.flowdata.postparam.part_video:
            return False
        log.info(self.flowdata.postparam.part_video)
        to.upload(path.join(self.source_dir, "large_part_{}.mp4".format(self.flowdata.identifier)), self.reative)
        # 2.   生成动态图, 规则里面的webp打开才会生成    <identifier>_large_sync.webp   <identifier>_sync.webp
        #
        if self.rule.webp.enable:
            self.flowdata.postparam.webp = to.upload(path.join(self.source_dir, "{}_sync.webp".format(self.flowdata.identifier)),self.reative)
            if not self.flowdata.postparam.webp:
                return False
            log.info(self.flowdata.postparam.webp)
            if not to.upload(path.join(self.source_dir, "{}_large_sync.webp".format(self.flowdata.identifier)),self.reative):
                return False
        # 3. 大长图
        if not self._long_preview_image():
            return False
        self.flowdata.postparam.thumb_longview = to.upload(path.join(self.source_dir, "{}_longPreview.jpg".format(self.flowdata.identifier)),self.reative)
        if not self.flowdata.postparam.thumb_longview:
            return False
        log.info(self.flowdata.postparam.thumb_longview)
        # 4. 缩略图, 先上传第一个jpg
        self.flowdata.postparam.thumbnail = to.upload(
            path.join(self.source_dir, "{}_thumb_{}.jpg".format(
                self.flowdata.identifier,self.flowdata.postparam.thumb_series[0])),self.reative)
        if not self.flowdata.postparam.thumbnail:
            return False
        log.info(self.flowdata.postparam.thumbnail)
        # 第一个webp
        if not to.upload(
            path.join(self.source_dir, "{}_thumb_{}.webp".format(
                self.flowdata.identifier,self.flowdata.postparam.thumb_series[0])),self.reative):
            return False
        # 接着上传后面的
        log.info(self.flowdata.postparam.thumb_series)
        for i in self.flowdata.postparam.thumb_series[1:]:
            if not to.upload(
                path.join(self.source_dir, "{}_thumb_{}.jpg".format(
                    self.flowdata.identifier,i)),self.reative):
                return False
            if not to.upload(
                path.join(self.source_dir, "{}_thumb_{}.webp".format(
                    self.flowdata.identifier,i)),self.reative):
                return False
        # 5.  封面图
        self.flowdata.postparam.cover = to.upload(
            path.join(self.source_dir, "{}.jpg".format(
                self.flowdata.identifier)),self.reative)
        if not self.flowdata.postparam.cover:
            return False
        log.info(self.flowdata.postparam.cover)
        # 第一个webp
        if not to.upload(
            path.join(self.source_dir, "{}.webp".format(
                self.flowdata.identifier)),self.reative):
            return False
        # 6. 横向图和纵向图
        # test_hor.jpg  test_hor_large.jpg  test_hor_large.webp    test_hor.webp
        self.flowdata.postparam.thumb_ver = to.upload(path.join(self.source_dir, "{}_ver.jpg".format(self.flowdata.identifier)),self.reative)
        if not self.flowdata.postparam.thumb_ver:
            return False
        log.info( self.flowdata.postparam.thumb_ver)
        self.flowdata.postparam.thumb_hor = to.upload(path.join(self.source_dir, "{}_hor.jpg".format(self.flowdata.identifier)),self.reative)
        if not self.flowdata.postparam.thumb_hor:
            return False
        log.info( self.flowdata.postparam.thumb_hor)
        hzimage = ["{}_hor_large.jpg", "{}_hor_large.webp", "{}_hor.webp", "{}_ver_large.jpg", "{}_ver_large.webp", "{}_ver.webp"]
        for f in hzimage:
            if not to.upload(path.join(self.source_dir, f.format(self.flowdata.identifier)),self.reative):
                return False
        # 7. 视频
        self.flowdata.postparam.download_url = to.upload(path.join(self.source_dir, "{}.mp4".format(self.flowdata.identifier)),self.reative)
        if not self.flowdata.postparam.download_url:
            return False
        log.info( self.flowdata.postparam.download_url)
        # 8. 试看视频（1/10）
        preview_reative_dir = os.path.join(self.reative, "hls", "preview")
        preview_ab_dir = os.path.join(self.source_dir, "hls", "preview")
        for pf in os.listdir(preview_ab_dir):
            name = to.upload(path.join(preview_ab_dir, pf),preview_reative_dir)
            if not name:
                return False
            if pf.count("m3u8") > 0:
                self.flowdata.postparam.preview = name
        
        log.info(self.flowdata.postparam.preview)
        # 9. 视频
        play_url_reative_dir = os.path.join(self.reative, "hls", "1")
        play_url_ab_dir = os.path.join(self.source_dir, "hls", "1")
        for pf in os.listdir(play_url_ab_dir):
            name = to.upload(path.join(play_url_ab_dir, pf),play_url_reative_dir)
            if not name:
                return False
            if pf.count("m3u8") > 0:
                self.flowdata.postparam.play_url = name
        
        log.info(self.flowdata.postparam.play_url)
        return True
        # # 返回对应的路径
        # 从这里找对应的文件 
        # print(filename)

    def _send_to_aliyun_oss(self) -> bool:
        return True


    def _send_to_remote_server(self) -> bool:
        # 拼接json 发送到远程服务器
        # 拼接数据
        server_function = [self._send_to_server, self._send_to_aliyun_oss, self._send_to_tx_oss]
        # 执行对应的函数处理
        return server_function[self.serverinfo.server.server_type]()
        
        