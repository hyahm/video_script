# encoding=utf-8

from lib.newrule import Webp
from functional.files import create_dir
from common.ffmpeg import ffmpeg
from common.log import log
from os import path

log.set_out

class MakeVideoWebp():
    def __init__(self, source_dir: str, video_path: str, webp: Webp, width: int, heigth: int, length: int) -> None:
        """
        source_dir: 视频处理后的根目录
        video_path: 视频路径
        webp: webp规则
        width: 视频宽度
        heigth: 视频高度
        length: 视频长度
        """
        self.video_path = video_path
        self.webp = webp
        self.width = width
        self.heigth = heigth
        self.length = length
        self.temp_webp = path.join(source_dir, "webp")

    def make_webp(self, output: str="-",largeoutput: str="-", ad_start: int = 0, this_width: int=400) -> int:
        """
            output: 输出文件
            this_width: 生产视频宽度  默认400
        """
        # 思路： 视频是无法多段截取动态图的， 所以先要切视频
        """
        params: 
            dir: 动态图的目录
            output: 输出路径
        """
        
        count = self.webp.count
        create_dir(self.temp_webp)
        if count <= 0:
            count = 10
        # 计算count
        interval = self.webp.interval
        #  视频开始截取时间
        start_time = 0
        if ad_start > 0:
            start_time = ad_start + 6
        start = self.length - start_time
        if start <= count:
            count = 1
        if count > 1:
            # 计算理想中的间隔
            wash_interval = (start - 1) // (count -1)
            # 如果设置的间隔大于理想中的间隔， 以理想的间隔为主, 小于等于0就自动计算间距
            if interval <= 1:
                interval = wash_interval

        # 计算 size
        if self.width == 0:
            return -1
        this_heigth = this_width * self.heigth // self.width
        if this_heigth % 2 != 0:
            this_heigth += 1
        size = "{}*{}".format(this_width, this_heigth)
        log.info("count: %d" % count )
        tmp_mp4_list = []
        large_mp4_list = []
        for i in range(count):
            # cut(self, input_path, output_path, start, step, size="310*174"):
            if not ffmpeg.cut(self.video_path, "{}/_tmp_{}.mp4".format(self.temp_webp, i), i * interval + start_time, 1, size):
                log.error("视频 {}秒处有问题".format(i * interval + start))
                return 0
            tmp_mp4_list.append("{}/_tmp_{}.mp4".format(self.temp_webp, i))

            if not ffmpeg.cut(self.video_path, "{}/_tmp_lager_{}.mp4".format(self.temp_webp, i), i * interval + start_time, 1):
                log.error("视频 {}秒处有问题".format(i * interval + start))
                return 0
            large_mp4_list.append("{}/_tmp_lager_{}.mp4".format(self.temp_webp, i))
        if not ffmpeg.merge_mp4s_and_make_webp(output, *tmp_mp4_list):
            log.error("视频不正常")
            return 0
        if not ffmpeg.merge_mp4s_and_make_webp(largeoutput, *large_mp4_list):
            log.error("视频不正常")
            return 0
        return count
