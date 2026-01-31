# encoding=utf-8
from lib.data import HugoData
from common.log import log
from os import path
from common.ffmpeg import ffmpeg
from functional.files import create_dir
from functional.images import make_long_preview_to_size

# 存储的父类

class Store():

    def __init__(self, source_dir: str, reative: str, flowdata: HugoData) -> None:
        self.flowdata = flowdata
        self.source_dir = source_dir
        self.reative = reative
        self.video_path = path.join(self.source_dir, self.flowdata + ".mp4")

    def _long_preview_image(self):
        # 制作缩略图， 长预览图（由预览图拼接而成），

        #    1、视频时长<30s 长图截取1张  预览图5张
        #    30s<视频时长<3分钟 长图截取10张 预览图10张
        #    视频时长>3分钟 长图截取100张 预览图10张
        log.info("制作长预览图======== %d========" % self.video_length)
        long_preview_tmp = path.join(
            self.source_dir, self.flowdata.identifier)  # 临时路径
        create_dir(long_preview_tmp)
        image_width = 640
        image_height = image_width * self.height // self.width
        if self.video_length < 100:
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
                if not ffmpeg.get_cover(self.video_path, (self.video_length * i - 1) // 100, path.join(long_preview_tmp, "tmp{}.jpg".format(i)),  size="{0}*{1}".format(image_width, image_height)):
                    log.error("截取大长图失败")
                    return False

                # 合成大长图
            if not make_long_preview_to_size(long_preview_tmp, image_width, image_height, path.join(self.source_dir, "%s_longPreview.jpg" % self.flowdata.identifier)):
                log.info("合成长预览图失败")
                # shell.remove_all(long_preview_tmp)
                return False
        log.info("制作长预览图完成............")
        return True
