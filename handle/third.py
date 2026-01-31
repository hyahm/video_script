# encoding=utf-8

"""
所有第三方的处理类
"""


from lib.data import HugoData, Video
from common.log import log
from common.ffmpeg import ffmpeg
import os


class Send(HugoData):
    def __init__(self, data):
        super().__init__(data)

    def _make_preview_hls(self):
            # 这个是生成试看的m3u8地址
            log.info(self.dict_conf)
            # if self.dict_conf["user"] != "77xxx":
            #     return True
            cut_video_path = os.path.join(self.source_dir, "preview_" +self.identifier + ".mp4")
            duration =  self.dict_conf["postparam"]["duration"] // 10
            if duration > 360:
                duration = 360
            if not ffmpeg.cut(self.video_path, cut_video_path, 0, duration):
                log.info("cut video failed")
                return False
            video = Video(cut_video_path )
            if not video.make_hls(self.identifier, self.source_dir, self.rule.rule_dict, self.user, "preview"):
                os.remove(cut_video_path)
                return False
            os.remove(cut_video_path)
            return True