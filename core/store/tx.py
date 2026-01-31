# encoding=utf-8


# 腾讯云 oss的处理逻辑

from service.txoss import TxOss
from common.log import log
import os
from os import path
from lib.data import HugoData
from core.store.store import Store

class TenXunYun(Store):
    def __init__(self, source_dir: str, reative: str, flowdata: HugoData) -> None:
        super().__init__(source_dir,reative,flowdata)

    def upload(self):
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